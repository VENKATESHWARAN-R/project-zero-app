package registry

import (
	"context"
	"fmt"
	"net/http"
	"sync"
	"time"

	"gateway/internal/models"
)

type ServiceRegistry struct {
	services  map[string]*models.ServiceConfig
	routes    []*models.RouteConfig
	mutex     sync.RWMutex
	client    *http.Client
	stopChan  chan struct{}
	isRunning bool
}

func NewServiceRegistry() *ServiceRegistry {
	return &ServiceRegistry{
		services: make(map[string]*models.ServiceConfig),
		routes:   make([]*models.RouteConfig, 0),
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
		stopChan: make(chan struct{}),
	}
}

func (sr *ServiceRegistry) RegisterService(config models.ServiceConfig) {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()

	// Create a copy to avoid race conditions
	serviceCopy := config
	if serviceCopy.Headers == nil {
		serviceCopy.Headers = make(map[string]string)
	}
	if serviceCopy.HealthPath == "" {
		serviceCopy.HealthPath = "/health"
	}
	if serviceCopy.Status == "" {
		serviceCopy.Status = models.ServiceUnknown
	}

	sr.services[config.Name] = &serviceCopy
}

func (sr *ServiceRegistry) RegisterRoute(config models.RouteConfig) {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()

	// Create a copy to avoid race conditions
	routeCopy := config
	if routeCopy.Headers == nil {
		routeCopy.Headers = make(map[string]string)
	}
	if routeCopy.Method == "" {
		routeCopy.Method = "*"
	}

	sr.routes = append(sr.routes, &routeCopy)
}

func (sr *ServiceRegistry) GetService(name string) (*models.ServiceConfig, bool) {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	service, exists := sr.services[name]
	if !exists {
		return nil, false
	}

	// Return a copy to avoid race conditions
	serviceCopy := *service
	return &serviceCopy, true
}

func (sr *ServiceRegistry) GetAllServices() map[string]models.ServiceConfig {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	result := make(map[string]models.ServiceConfig, len(sr.services))
	for name, service := range sr.services {
		result[name] = *service
	}
	return result
}

func (sr *ServiceRegistry) GetRoutes() []models.RouteConfig {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	result := make([]models.RouteConfig, len(sr.routes))
	for i, route := range sr.routes {
		result[i] = *route
	}
	return result
}

func (sr *ServiceRegistry) FindRoute(method, path string) (*models.RouteConfig, *models.ServiceConfig) {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	// Find matching route
	for _, route := range sr.routes {
		if route.Matches(method, path) {
			// Get the associated service
			if service, exists := sr.services[route.ServiceName]; exists && service.Enabled {
				return route, service
			}
		}
	}

	return nil, nil
}

func (sr *ServiceRegistry) GetHealthyServices() map[string]models.ServiceConfig {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	result := make(map[string]models.ServiceConfig)
	for name, service := range sr.services {
		if service.IsHealthy() {
			result[name] = *service
		}
	}
	return result
}

func (sr *ServiceRegistry) StartHealthChecking(interval time.Duration) {
	sr.mutex.Lock()
	if sr.isRunning {
		sr.mutex.Unlock()
		return
	}
	sr.isRunning = true
	sr.mutex.Unlock()

	go sr.healthCheckLoop(interval)
}

func (sr *ServiceRegistry) StopHealthChecking() {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()

	if sr.isRunning {
		close(sr.stopChan)
		sr.isRunning = false
		sr.stopChan = make(chan struct{})
	}
}

func (sr *ServiceRegistry) healthCheckLoop(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	// Initial health check
	sr.performHealthChecks()

	for {
		select {
		case <-ticker.C:
			sr.performHealthChecks()
		case <-sr.stopChan:
			return
		}
	}
}

func (sr *ServiceRegistry) performHealthChecks() {
	sr.mutex.RLock()
	services := make([]*models.ServiceConfig, 0, len(sr.services))
	for _, service := range sr.services {
		if service.Enabled {
			services = append(services, service)
		}
	}
	sr.mutex.RUnlock()

	// Perform health checks concurrently
	var wg sync.WaitGroup
	for _, service := range services {
		wg.Add(1)
		go func(svc *models.ServiceConfig) {
			defer wg.Done()
			sr.checkServiceHealth(svc)
		}(service)
	}
	wg.Wait()
}

func (sr *ServiceRegistry) checkServiceHealth(service *models.ServiceConfig) {
	start := time.Now()
	healthURL := service.URL + service.HealthPath

	ctx, cancel := context.WithTimeout(context.Background(), service.Timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", healthURL, nil)
	if err != nil {
		sr.updateServiceStatus(service.Name, models.ServiceUnhealthy, 0)
		return
	}

	// Add any custom headers
	for key, value := range service.Headers {
		req.Header.Set(key, value)
	}

	resp, err := sr.client.Do(req)
	responseTime := float64(time.Since(start).Nanoseconds()) / 1e6 // Convert to milliseconds

	if err != nil {
		sr.updateServiceStatus(service.Name, models.ServiceUnhealthy, responseTime)
		return
	}
	defer resp.Body.Close()

	// Consider 2xx status codes as healthy
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		sr.updateServiceStatus(service.Name, models.ServiceHealthy, responseTime)
	} else {
		sr.updateServiceStatus(service.Name, models.ServiceUnhealthy, responseTime)
	}
}

func (sr *ServiceRegistry) updateServiceStatus(serviceName string, status models.ServiceStatus, responseTime float64) {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()

	if service, exists := sr.services[serviceName]; exists {
		service.UpdateStatus(status, responseTime)
	}
}

func (sr *ServiceRegistry) RemoveService(name string) {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()

	delete(sr.services, name)
}

func (sr *ServiceRegistry) RemoveRoute(path, serviceName string) {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()

	for i, route := range sr.routes {
		if route.Path == path && route.ServiceName == serviceName {
			// Remove route by swapping with last element and truncating
			sr.routes[i] = sr.routes[len(sr.routes)-1]
			sr.routes = sr.routes[:len(sr.routes)-1]
			break
		}
	}
}

func (sr *ServiceRegistry) GetServiceStats() map[string]interface{} {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	healthy := 0
	unhealthy := 0
	unknown := 0
	total := len(sr.services)

	for _, service := range sr.services {
		switch service.Status {
		case models.ServiceHealthy:
			healthy++
		case models.ServiceUnhealthy:
			unhealthy++
		case models.ServiceUnknown:
			unknown++
		}
	}

	return map[string]interface{}{
		"total":     total,
		"healthy":   healthy,
		"unhealthy": unhealthy,
		"unknown":   unknown,
		"routes":    len(sr.routes),
	}
}

func (sr *ServiceRegistry) ValidateConfiguration() error {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()

	// Check that all routes reference existing services
	for i, route := range sr.routes {
		if _, exists := sr.services[route.ServiceName]; !exists {
			return fmt.Errorf("route %d references non-existent service: %s", i, route.ServiceName)
		}
	}

	return nil
}