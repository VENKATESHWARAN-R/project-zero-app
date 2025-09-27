package config

import (
	"fmt"
	"os"
	"strings"
	"time"

	"gateway/internal/models"

	"github.com/spf13/viper"
)

type Manager struct {
	config *models.GatewayConfig
	viper  *viper.Viper
}

func NewManager() *Manager {
	v := viper.New()

	// Set defaults
	v.SetDefault("server.host", "0.0.0.0")
	v.SetDefault("server.port", 8000)
	v.SetDefault("server.read_timeout", "30s")
	v.SetDefault("server.write_timeout", "30s")
	v.SetDefault("server.idle_timeout", "60s")

	v.SetDefault("rate_limit.name", "default")
	v.SetDefault("rate_limit.requests", 100)
	v.SetDefault("rate_limit.window", "1m")
	v.SetDefault("rate_limit.burst", 200)
	v.SetDefault("rate_limit.scope", "per_ip")
	v.SetDefault("rate_limit.enabled", true)

	v.SetDefault("circuit_breaker.max_requests", 3)
	v.SetDefault("circuit_breaker.interval", "60s")
	v.SetDefault("circuit_breaker.timeout", "30s")
	v.SetDefault("circuit_breaker.failure_threshold", 0.6)

	v.SetDefault("auth.service_url", "http://localhost:8001")
	v.SetDefault("auth.timeout", "5s")
	v.SetDefault("auth.cache_ttl", "5m")

	v.SetDefault("logging.level", "info")
	v.SetDefault("logging.format", "json")

	// Configure environment variable support (but not for complex structures)
	v.SetEnvPrefix("GATEWAY")
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	// Don't use AutomaticEnv() as it can interfere with complex structures
	// Instead, bind specific variables we want to support
	v.BindEnv("server.host", "GATEWAY_SERVER_HOST")
	v.BindEnv("server.port", "GATEWAY_SERVER_PORT")
	v.BindEnv("rate_limit.requests", "GATEWAY_RATE_LIMIT_REQUESTS")
	v.BindEnv("rate_limit.window", "GATEWAY_RATE_LIMIT_WINDOW")
	v.BindEnv("rate_limit.burst", "GATEWAY_RATE_LIMIT_BURST")
	v.BindEnv("auth.service_url", "GATEWAY_AUTH_SERVICE_URL")
	v.BindEnv("logging.level", "GATEWAY_LOGGING_LEVEL")

	return &Manager{
		viper: v,
	}
}

func (m *Manager) LoadConfig(configPath string) error {
	// Try to load from file if provided
	if configPath != "" {
		m.viper.SetConfigFile(configPath)
	} else {
		// Look for config in working directory and /etc
		m.viper.SetConfigName("config")
		m.viper.SetConfigType("yaml")
		m.viper.AddConfigPath(".")
		m.viper.AddConfigPath("./config")
		m.viper.AddConfigPath("/etc/gateway")
	}

	// Read config file (optional)
	if err := m.viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return fmt.Errorf("failed to read config file: %w", err)
		}
		// Config file not found is not an error - we can use defaults and env vars
	}

	// Unmarshal into our config struct
	config := models.NewDefaultGatewayConfig()
	if err := m.viper.Unmarshal(config); err != nil {
		return fmt.Errorf("failed to unmarshal config: %w", err)
	}


	// Parse duration strings
	if err := m.parseDurations(config); err != nil {
		return fmt.Errorf("failed to parse durations: %w", err)
	}

	m.config = config
	return nil
}

func (m *Manager) parseDurations(config *models.GatewayConfig) error {
	var err error

	// Parse server timeouts
	if timeoutStr := m.viper.GetString("server.read_timeout"); timeoutStr != "" {
		if config.Server.ReadTimeout, err = time.ParseDuration(timeoutStr); err != nil {
			return fmt.Errorf("invalid read_timeout: %w", err)
		}
	}

	if timeoutStr := m.viper.GetString("server.write_timeout"); timeoutStr != "" {
		if config.Server.WriteTimeout, err = time.ParseDuration(timeoutStr); err != nil {
			return fmt.Errorf("invalid write_timeout: %w", err)
		}
	}

	if timeoutStr := m.viper.GetString("server.idle_timeout"); timeoutStr != "" {
		if config.Server.IdleTimeout, err = time.ParseDuration(timeoutStr); err != nil {
			return fmt.Errorf("invalid idle_timeout: %w", err)
		}
	}

	// Parse rate limit window
	if windowStr := m.viper.GetString("rate_limit.window"); windowStr != "" {
		if config.RateLimit.Window, err = time.ParseDuration(windowStr); err != nil {
			return fmt.Errorf("invalid rate_limit.window: %w", err)
		}
	}

	// Parse circuit breaker durations
	if intervalStr := m.viper.GetString("circuit_breaker.interval"); intervalStr != "" {
		if config.CircuitBreaker.Interval, err = time.ParseDuration(intervalStr); err != nil {
			return fmt.Errorf("invalid circuit_breaker.interval: %w", err)
		}
	}

	if timeoutStr := m.viper.GetString("circuit_breaker.timeout"); timeoutStr != "" {
		if config.CircuitBreaker.Timeout, err = time.ParseDuration(timeoutStr); err != nil {
			return fmt.Errorf("invalid circuit_breaker.timeout: %w", err)
		}
	}

	// Parse auth timeouts
	if timeoutStr := m.viper.GetString("auth.timeout"); timeoutStr != "" {
		if config.Auth.Timeout, err = time.ParseDuration(timeoutStr); err != nil {
			return fmt.Errorf("invalid auth.timeout: %w", err)
		}
	}

	if ttlStr := m.viper.GetString("auth.cache_ttl"); ttlStr != "" {
		if config.Auth.CacheTTL, err = time.ParseDuration(ttlStr); err != nil {
			return fmt.Errorf("invalid auth.cache_ttl: %w", err)
		}
	}

	// Parse service timeouts
	for name, service := range config.Services {
		if timeoutStr := m.viper.GetString(fmt.Sprintf("services.%s.timeout", name)); timeoutStr != "" {
			if service.Timeout, err = time.ParseDuration(timeoutStr); err != nil {
				return fmt.Errorf("invalid timeout for service %s: %w", name, err)
			}
			config.Services[name] = service
		}
	}

	return nil
}

func (m *Manager) GetConfig() *models.GatewayConfig {
	if m.config == nil {
		return models.NewDefaultGatewayConfig()
	}
	return m.config
}

func (m *Manager) GetServerAddress() string {
	return fmt.Sprintf("%s:%d", m.config.Server.Host, m.config.Server.Port)
}

func (m *Manager) Reload() error {
	configFile := m.viper.ConfigFileUsed()
	return m.LoadConfig(configFile)
}

func (m *Manager) ValidateConfig() error {
	config := m.GetConfig()

	// Validate server config
	if config.Server.Port < 1000 || config.Server.Port > 65535 {
		return fmt.Errorf("invalid server port: %d", config.Server.Port)
	}

	// Validate rate limit config
	if config.RateLimit.Enabled {
		if config.RateLimit.Requests <= 0 {
			return fmt.Errorf("rate limit requests must be positive")
		}
		if config.RateLimit.Burst < config.RateLimit.Requests {
			return fmt.Errorf("rate limit burst must be >= requests")
		}
		if config.RateLimit.Window <= 0 {
			return fmt.Errorf("rate limit window must be positive")
		}
	}

	// Validate circuit breaker config
	if config.CircuitBreaker.FailureThreshold < 0 || config.CircuitBreaker.FailureThreshold > 1 {
		return fmt.Errorf("circuit breaker failure threshold must be between 0 and 1")
	}

	// Validate services
	for name, service := range config.Services {
		if service.Name == "" {
			return fmt.Errorf("service %s has empty name", name)
		}
		if service.URL == "" {
			return fmt.Errorf("service %s has empty URL", name)
		}
		if service.Timeout <= 0 {
			return fmt.Errorf("service %s has invalid timeout", name)
		}
	}

	// Validate routes (skip if no routes configured)
	if len(config.Routes) > 0 {
		for i, route := range config.Routes {
			if route.Path == "" {
				return fmt.Errorf("route %d has empty path", i)
			}
			if route.ServiceName == "" {
				return fmt.Errorf("route %d has empty service name", i)
			}
			if _, exists := config.Services[route.ServiceName]; !exists {
				return fmt.Errorf("route %d references non-existent service: %s", i, route.ServiceName)
			}
		}
	}

	return nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}