package models

import (
	"time"
)

type GatewayConfig struct {
	Server         ServerConfig               `json:"server" yaml:"server"`
	Services       map[string]ServiceConfig   `json:"services" yaml:"services"`
	Routes         []RouteConfig              `json:"routes" yaml:"routes"`
	RateLimit      RateLimitPolicy            `json:"rate_limit" yaml:"rate_limit"`
	CircuitBreaker CircuitBreakerSettings     `json:"circuit_breaker" yaml:"circuit_breaker"`
	Auth           AuthConfig                 `json:"auth" yaml:"auth"`
	Logging        LoggingConfig              `json:"logging" yaml:"logging"`
}

type ServerConfig struct {
	Host         string        `json:"host" yaml:"host"`
	Port         int           `json:"port" yaml:"port" validate:"required,min=1000,max=65535"`
	ReadTimeout  time.Duration `json:"read_timeout" yaml:"read_timeout"`
	WriteTimeout time.Duration `json:"write_timeout" yaml:"write_timeout"`
	IdleTimeout  time.Duration `json:"idle_timeout" yaml:"idle_timeout"`
}

type AuthConfig struct {
	ServiceURL string        `json:"service_url" yaml:"service_url" validate:"required,url"`
	Timeout    time.Duration `json:"timeout" yaml:"timeout"`
	CacheTTL   time.Duration `json:"cache_ttl" yaml:"cache_ttl"`
	SkipPaths  []string      `json:"skip_paths,omitempty" yaml:"skip_paths,omitempty"`
}

type LoggingConfig struct {
	Level      string `json:"level" yaml:"level"`
	Format     string `json:"format" yaml:"format"`
	OutputFile string `json:"output_file,omitempty" yaml:"output_file,omitempty"`
	MaxSize    int    `json:"max_size,omitempty" yaml:"max_size,omitempty"`
	MaxBackups int    `json:"max_backups,omitempty" yaml:"max_backups,omitempty"`
}

func NewDefaultGatewayConfig() *GatewayConfig {
	return &GatewayConfig{
		Server: ServerConfig{
			Host:         "0.0.0.0",
			Port:         8000,
			ReadTimeout:  30 * time.Second,
			WriteTimeout: 30 * time.Second,
			IdleTimeout:  60 * time.Second,
		},
		Services: make(map[string]ServiceConfig),
		Routes:   []RouteConfig{},
		RateLimit: RateLimitPolicy{
			Name:     "default",
			Requests: 100,
			Window:   time.Minute,
			Burst:    200,
			Scope:    ScopePerIP,
			Enabled:  true,
		},
		CircuitBreaker: CircuitBreakerSettings{
			MaxRequests:      3,
			Interval:         60 * time.Second,
			Timeout:          30 * time.Second,
			FailureThreshold: 0.6,
		},
		Auth: AuthConfig{
			ServiceURL: "http://localhost:8001",
			Timeout:    5 * time.Second,
			CacheTTL:   5 * time.Minute,
			SkipPaths: []string{
				"/health",
				"/health/ready",
				"/gateway/services",
				"/gateway/routes",
				"/gateway/metrics",
			},
		},
		Logging: LoggingConfig{
			Level:  "info",
			Format: "json",
		},
	}
}