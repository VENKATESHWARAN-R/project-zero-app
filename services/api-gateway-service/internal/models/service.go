package models

import (
	"time"
)

type ServiceStatus string

const (
	ServiceHealthy   ServiceStatus = "healthy"
	ServiceUnhealthy ServiceStatus = "unhealthy"
	ServiceUnknown   ServiceStatus = "unknown"
)

type ServiceConfig struct {
	Name        string            `json:"name" yaml:"name" validate:"required"`
	URL         string            `json:"url" yaml:"url" validate:"required,url"`
	Timeout     time.Duration     `json:"timeout" yaml:"timeout" validate:"required"`
	HealthPath  string            `json:"health_path" yaml:"health_path"`
	Headers     map[string]string `json:"headers,omitempty" yaml:"headers,omitempty"`
	Enabled     bool              `json:"enabled" yaml:"enabled"`
	LastChecked time.Time         `json:"last_checked"`
	Status      ServiceStatus     `json:"status"`
	ResponseTime float64          `json:"response_time,omitempty"`
}

func NewServiceConfig(name, url string, timeout time.Duration) *ServiceConfig {
	return &ServiceConfig{
		Name:       name,
		URL:        url,
		Timeout:    timeout,
		HealthPath: "/health",
		Enabled:    true,
		Status:     ServiceUnknown,
		Headers:    make(map[string]string),
	}
}

func (s *ServiceConfig) IsHealthy() bool {
	return s.Status == ServiceHealthy && s.Enabled
}

func (s *ServiceConfig) UpdateStatus(status ServiceStatus, responseTime float64) {
	s.Status = status
	s.LastChecked = time.Now()
	s.ResponseTime = responseTime
}