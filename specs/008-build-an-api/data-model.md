# Data Model: API Gateway Service

**Feature**: API Gateway Service
**Date**: 2025-09-27
**Status**: Design Phase

## Overview

The API Gateway service primarily manages routing, rate limiting, and service health information. As a stateless service, most data structures are in-memory and configuration-driven rather than persisted to databases.

## Core Entities

### 1. Service Registry Entry

Represents a backend service in the gateway's routing table.

```go
type ServiceConfig struct {
    Name         string            `json:"name" yaml:"name" validate:"required"`
    URL          string            `json:"url" yaml:"url" validate:"required,url"`
    Timeout      time.Duration     `json:"timeout" yaml:"timeout" validate:"required"`
    HealthPath   string            `json:"health_path" yaml:"health_path"`
    Headers      map[string]string `json:"headers,omitempty" yaml:"headers,omitempty"`
    Enabled      bool              `json:"enabled" yaml:"enabled"`
    LastChecked  time.Time         `json:"last_checked"`
    Status       ServiceStatus     `json:"status"`
}

type ServiceStatus string

const (
    ServiceHealthy   ServiceStatus = "healthy"
    ServiceUnhealthy ServiceStatus = "unhealthy"
    ServiceUnknown   ServiceStatus = "unknown"
)
```

**Business Rules**:
- Service name must be unique within the registry
- URL must be valid and accessible
- Timeout must be between 1-60 seconds
- Health path defaults to "/health" if not specified
- Services start in "unknown" status until first health check

### 2. Route Configuration

Defines URL path routing patterns to backend services.

```go
type RouteConfig struct {
    Path        string            `json:"path" yaml:"path" validate:"required"`
    Method      string            `json:"method" yaml:"method"`
    ServiceName string            `json:"service_name" yaml:"service_name" validate:"required"`
    StripPrefix bool              `json:"strip_prefix" yaml:"strip_prefix"`
    Headers     map[string]string `json:"headers,omitempty" yaml:"headers,omitempty"`
    AuthRequired bool             `json:"auth_required" yaml:"auth_required"`
}
```

**Business Rules**:
- Path must start with "/" and be unique per method
- Method defaults to "*" (all methods) if not specified
- ServiceName must reference an existing service in the registry
- StripPrefix removes the matched path prefix before forwarding
- AuthRequired determines if JWT validation is enforced

### 3. Rate Limit Policy

Defines rate limiting rules for client requests.

```go
type RateLimitPolicy struct {
    Name         string        `json:"name" yaml:"name" validate:"required"`
    Requests     int           `json:"requests" yaml:"requests" validate:"required,min=1"`
    Window       time.Duration `json:"window" yaml:"window" validate:"required"`
    Burst        int           `json:"burst" yaml:"burst" validate:"required,min=1"`
    Scope        LimitScope    `json:"scope" yaml:"scope"`
    Enabled      bool          `json:"enabled" yaml:"enabled"`
}

type LimitScope string

const (
    ScopeGlobal LimitScope = "global"
    ScopePerIP  LimitScope = "per_ip"
    ScopePerUser LimitScope = "per_user"
)
```

**Business Rules**:
- Requests must be positive integer
- Window must be at least 1 second
- Burst must be at least equal to requests per window
- Global scope applies to all requests
- Per-IP scope tracks by client IP address
- Per-user scope tracks by authenticated user ID

### 4. Circuit Breaker State

Tracks failure patterns and circuit breaker status for services.

```go
type CircuitBreakerState struct {
    ServiceName    string                `json:"service_name"`
    State          CircuitState          `json:"state"`
    FailureCount   int                   `json:"failure_count"`
    SuccessCount   int                   `json:"success_count"`
    LastFailure    time.Time             `json:"last_failure"`
    NextRetry      time.Time             `json:"next_retry"`
    Settings       CircuitBreakerSettings `json:"settings"`
}

type CircuitState string

const (
    CircuitClosed   CircuitState = "closed"
    CircuitOpen     CircuitState = "open"
    CircuitHalfOpen CircuitState = "half_open"
)

type CircuitBreakerSettings struct {
    MaxRequests     uint32        `json:"max_requests" yaml:"max_requests"`
    Interval        time.Duration `json:"interval" yaml:"interval"`
    Timeout         time.Duration `json:"timeout" yaml:"timeout"`
    FailureThreshold float64      `json:"failure_threshold" yaml:"failure_threshold"`
}
```

**State Transitions**:
- **Closed → Open**: When failure rate exceeds threshold
- **Open → Half-Open**: After timeout period expires
- **Half-Open → Closed**: When max requests succeed
- **Half-Open → Open**: When any request fails

### 5. Request Log Entry

Captures request/response metadata for monitoring and debugging.

```go
type RequestLogEntry struct {
    Timestamp     time.Time         `json:"timestamp"`
    CorrelationID string            `json:"correlation_id"`
    Method        string            `json:"method"`
    Path          string            `json:"path"`
    ServiceName   string            `json:"service_name,omitempty"`
    ClientIP      string            `json:"client_ip"`
    UserID        string            `json:"user_id,omitempty"`
    StatusCode    int               `json:"status_code"`
    Duration      time.Duration     `json:"duration"`
    RequestSize   int64             `json:"request_size"`
    ResponseSize  int64             `json:"response_size"`
    Error         string            `json:"error,omitempty"`
    Headers       map[string]string `json:"headers,omitempty"`
}
```

**Business Rules**:
- Timestamp recorded at request start
- CorrelationID must be unique per request
- Duration measured from request start to response completion
- Error field populated only for failed requests
- Sensitive headers (Authorization) excluded from logging

### 6. Gateway Configuration

Root configuration structure for the entire gateway.

```go
type GatewayConfig struct {
    Server      ServerConfig               `json:"server" yaml:"server"`
    Services    map[string]ServiceConfig   `json:"services" yaml:"services"`
    Routes      []RouteConfig              `json:"routes" yaml:"routes"`
    RateLimit   RateLimitPolicy           `json:"rate_limit" yaml:"rate_limit"`
    CircuitBreaker CircuitBreakerSettings `json:"circuit_breaker" yaml:"circuit_breaker"`
    Auth        AuthConfig                 `json:"auth" yaml:"auth"`
    Logging     LoggingConfig              `json:"logging" yaml:"logging"`
}

type ServerConfig struct {
    Host         string        `json:"host" yaml:"host"`
    Port         int           `json:"port" yaml:"port" validate:"required,min=1000,max=65535"`
    ReadTimeout  time.Duration `json:"read_timeout" yaml:"read_timeout"`
    WriteTimeout time.Duration `json:"write_timeout" yaml:"write_timeout"`
    IdleTimeout  time.Duration `json:"idle_timeout" yaml:"idle_timeout"`
}

type AuthConfig struct {
    ServiceURL    string        `json:"service_url" yaml:"service_url" validate:"required,url"`
    Timeout       time.Duration `json:"timeout" yaml:"timeout"`
    CacheTTL      time.Duration `json:"cache_ttl" yaml:"cache_ttl"`
    SkipPaths     []string      `json:"skip_paths,omitempty" yaml:"skip_paths,omitempty"`
}

type LoggingConfig struct {
    Level       string `json:"level" yaml:"level"`
    Format      string `json:"format" yaml:"format"`
    OutputFile  string `json:"output_file,omitempty" yaml:"output_file,omitempty"`
    MaxSize     int    `json:"max_size,omitempty" yaml:"max_size,omitempty"`
    MaxBackups  int    `json:"max_backups,omitempty" yaml:"max_backups,omitempty"`
}
```

## Data Flow Patterns

### 1. Request Processing Flow

```
Incoming Request
    ↓
Correlation ID Assignment
    ↓
Rate Limiting Check
    ↓
Authentication (if required)
    ↓
Route Resolution
    ↓
Service Health Check
    ↓
Circuit Breaker Check
    ↓
Request Forwarding
    ↓
Response Processing
    ↓
Logging & Metrics
```

### 2. Health Check Flow

```
Periodic Health Checker
    ↓
Service Registry Iteration
    ↓
Health Endpoint Request
    ↓
Status Update
    ↓
Circuit Breaker Notification
    ↓
Service Registry Update
```

### 3. Configuration Management Flow

```
Configuration Source (File/Env)
    ↓
Configuration Validation
    ↓
Service Registry Update
    ↓
Route Table Rebuild
    ↓
Health Check Restart
    ↓
Circuit Breaker Reset
```

## Validation Rules

### Service Configuration
- URL must be reachable and return valid HTTP responses
- Timeout must be reasonable (1-60 seconds)
- Health path must return 200 OK when service is healthy

### Route Configuration
- Path patterns must not overlap ambiguously
- Service references must exist in service registry
- Authentication requirements must be consistently applied

### Rate Limiting
- Rate limits must be positive and achievable
- Burst limits must accommodate normal traffic patterns
- Rate limit policies must not create denial of service

### Circuit Breaker
- Failure thresholds must be between 0.0 and 1.0
- Timeouts must allow for service recovery
- Max requests in half-open state must be conservative

## Memory Management

### In-Memory Data Structures

1. **Service Registry**: Map of service name to ServiceConfig
2. **Route Table**: Sorted array of RouteConfig for O(log n) lookup
3. **Rate Limiters**: Map of client identifier to rate.Limiter
4. **Circuit Breakers**: Map of service name to CircuitBreakerState
5. **Token Cache**: LRU cache of JWT validation results

### Memory Optimization Strategies

1. **Rate Limiter Cleanup**: Periodic removal of inactive rate limiters
2. **Token Cache Size**: Limited to 1000 entries with TTL-based eviction
3. **Request Logs**: Buffered writes with configurable batch size
4. **Health Check Results**: Keep only current status, not historical data

## Configuration Examples

### Default Service Configuration
```yaml
services:
  auth:
    name: "auth-service"
    url: "http://localhost:8001"
    timeout: "30s"
    health_path: "/health"
    enabled: true

  orders:
    name: "order-service"
    url: "http://localhost:8008"
    timeout: "30s"
    health_path: "/health"
    enabled: true
```

### Route Configuration
```yaml
routes:
  - path: "/api/auth/*"
    service_name: "auth"
    strip_prefix: false
    auth_required: false

  - path: "/api/orders/*"
    service_name: "orders"
    strip_prefix: false
    auth_required: true
```

### Rate Limiting Configuration
```yaml
rate_limit:
  name: "default"
  requests: 100
  window: "1m"
  burst: 200
  scope: "per_ip"
  enabled: true
```

This data model provides the foundation for implementing a robust, configurable API gateway that can handle the routing, security, and resilience requirements of the Project Zero App microservices architecture.