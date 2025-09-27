package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"gateway/internal/config"
	"gateway/internal/models"
	"gateway/internal/registry"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize configuration manager
	configManager := config.NewManager()

	// Load configuration
	if err := configManager.LoadConfig(""); err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Validate configuration
	if err := configManager.ValidateConfig(); err != nil {
		log.Fatalf("Invalid configuration: %v", err)
	}

	cfg := configManager.GetConfig()

	// Initialize service registry
	serviceRegistry := registry.NewServiceRegistry()

	// Register services from configuration
	if len(cfg.Services) > 0 {
		for name, serviceConfig := range cfg.Services {
			serviceRegistry.RegisterService(serviceConfig)
			log.Printf("Registered service: %s at %s", name, serviceConfig.URL)
		}
	} else {
		log.Println("No services configured - running in basic mode")
	}

	// Register routes from configuration
	if len(cfg.Routes) > 0 {
		for _, routeConfig := range cfg.Routes {
			serviceRegistry.RegisterRoute(routeConfig)
			log.Printf("Registered route: %s -> %s", routeConfig.Path, routeConfig.ServiceName)
		}
	} else {
		log.Println("No routes configured - only management endpoints available")
	}

	// Start health checking
	serviceRegistry.StartHealthChecking(30 * time.Second)
	log.Println("Health checker started with 30s interval")

	// Set Gin mode
	if cfg.Logging.Level == "debug" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create Gin router
	router := gin.New()

	// Add basic middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Add CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Accept, Authorization, X-Correlation-ID")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Health endpoints
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"timestamp": time.Now().Format(time.RFC3339),
			"version":   "1.0.0",
			"uptime":    "1m", // TODO: Calculate actual uptime
		})
	})

	router.GET("/health/ready", func(c *gin.Context) {
		services := serviceRegistry.GetAllServices()
		allHealthy := true

		serviceStatus := make(map[string]interface{})
		for name, service := range services {
			status := map[string]interface{}{
				"name":         service.Name,
				"status":       string(service.Status),
				"url":          service.URL,
				"last_checked": service.LastChecked.Format(time.RFC3339),
			}
			if service.ResponseTime > 0 {
				status["response_time"] = service.ResponseTime
			}
			serviceStatus[name] = status

			if service.Status != models.ServiceHealthy {
				allHealthy = false
			}
		}

		statusCode := http.StatusOK
		readyStatus := "ready"
		if !allHealthy {
			statusCode = http.StatusServiceUnavailable
			readyStatus = "not_ready"
		}

		c.JSON(statusCode, gin.H{
			"status":    readyStatus,
			"timestamp": time.Now().Format(time.RFC3339),
			"services":  serviceStatus,
		})
	})

	// Gateway management endpoints
	router.GET("/gateway/services", func(c *gin.Context) {
		services := serviceRegistry.GetAllServices()
		serviceList := make([]interface{}, 0, len(services))

		for _, service := range services {
			serviceData := map[string]interface{}{
				"name":         service.Name,
				"status":       string(service.Status),
				"url":          service.URL,
				"last_checked": service.LastChecked.Format(time.RFC3339),
			}
			if service.ResponseTime > 0 {
				serviceData["response_time"] = service.ResponseTime
			}
			serviceList = append(serviceList, serviceData)
		}

		c.JSON(http.StatusOK, gin.H{
			"services": serviceList,
			"total":    len(serviceList),
		})
	})

	router.GET("/gateway/routes", func(c *gin.Context) {
		routes := serviceRegistry.GetRoutes()
		routeList := make([]interface{}, 0, len(routes))

		for _, route := range routes {
			routeData := map[string]interface{}{
				"path":         route.Path,
				"service_name": route.ServiceName,
			}
			if route.Method != "*" {
				routeData["method"] = route.Method
			}
			if route.StripPrefix {
				routeData["strip_prefix"] = route.StripPrefix
			}
			if route.AuthRequired {
				routeData["auth_required"] = route.AuthRequired
			}
			routeList = append(routeList, routeData)
		}

		c.JSON(http.StatusOK, gin.H{
			"routes": routeList,
			"total":  len(routeList),
		})
	})

	router.GET("/gateway/metrics", func(c *gin.Context) {
		stats := serviceRegistry.GetServiceStats()

		c.JSON(http.StatusOK, gin.H{
			"timestamp": time.Now().Format(time.RFC3339),
			"requests": gin.H{
				"total":             0, // TODO: Implement request counting
				"success":           0,
				"errors":            0,
				"avg_response_time": 0.0,
			},
			"rate_limits": gin.H{
				"active_limiters":   0, // TODO: Implement rate limiting metrics
				"blocked_requests":  0,
			},
			"circuit_breakers": gin.H{}, // TODO: Implement circuit breaker metrics
			"services":         stats,
		})
	})

	// Proxy routes - simplified implementation
	router.Any("/api/*proxyPath", func(c *gin.Context) {
		method := c.Request.Method
		path := c.Request.URL.Path

		route, service := serviceRegistry.FindRoute(method, path)
		if route == nil || service == nil {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "Route not found",
				"message": fmt.Sprintf("No route found for %s %s", method, path),
			})
			return
		}

		// For now, just return a simple response indicating the route was found
		// TODO: Implement actual reverse proxy logic
		c.JSON(http.StatusOK, gin.H{
			"message":     "Proxy endpoint found",
			"route":       route.Path,
			"service":     service.Name,
			"target_url":  service.URL,
			"method":      method,
			"path":        path,
		})
	})

	// Create HTTP server
	server := &http.Server{
		Addr:         configManager.GetServerAddress(),
		Handler:      router,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
		IdleTimeout:  cfg.Server.IdleTimeout,
	}

	// Start server in a goroutine
	go func() {
		log.Printf("Server listening on %s", server.Addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed to start: %v", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// Stop health checking
	serviceRegistry.StopHealthChecking()

	// Give server 30 seconds to shutdown gracefully
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited")
}