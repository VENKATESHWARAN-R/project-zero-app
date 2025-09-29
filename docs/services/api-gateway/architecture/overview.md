# API Gateway Architecture Overview

**Author**: Michael Rodriguez, Platform Technical Lead  
**Created**: 2025-09-29  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0  
**Owner**: Platform Engineering Team  
**Related**: [Technology Choices](./technology-choices.md) | [Routing Rules](../api-docs/routing-rules.md)  
**Review Date**: 2025-12-29  

## Summary

Comprehensive architecture documentation for the Project Zero App API Gateway, built with Go and designed for high performance, scalability, and reliability in a microservices environment.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Frontend App  │  Mobile Apps  │  External APIs  │  Admin UI  │
└─────────────┬───┴───────┬─────────┴────────┬──────────┴─────────┘
              │           │                  │
              ▼           ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Load Balancer                               │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API Gateway Cluster                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Gateway   │  │   Gateway   │  │   Gateway   │            │
│  │ Instance 1  │  │ Instance 2  │  │ Instance N  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Service Mesh                                  │
├───────┬─────────┬─────────┬─────────┬─────────┬─────────┬───────┤
│ Auth  │Profile  │Product  │  Cart   │ Order   │Payment  │Notify │
│Service│Service  │Catalog  │Service  │Service  │Service  │Service│
│:8001  │:8002    │:8004    │:8007    │:8008    │:8009    │:8011  │
└───────┴─────────┴─────────┴─────────┴─────────┴─────────┴───────┘
```

### Core Components

#### 1. Request Router
```go
type Router struct {
    routes      map[string]*Route
    middleware  []Middleware
    notFound    http.HandlerFunc
    methodNotAllowed http.HandlerFunc
}

type Route struct {
    Pattern     string
    Handler     http.HandlerFunc
    Methods     []string
    Middleware  []Middleware
    Service     *BackendService
}
```

#### 2. Authentication Middleware
```go
type AuthMiddleware struct {
    authService *AuthServiceClient
    skipPaths   []string
    cache       *TokenCache
}

func (a *AuthMiddleware) Authenticate(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // JWT token validation logic
    })
}
```

#### 3. Rate Limiter
```go
type RateLimiter struct {
    buckets map[string]*TokenBucket
    config  *RateLimitConfig
    mutex   sync.RWMutex
}

type TokenBucket struct {
    capacity   int64
    tokens     int64
    refillRate int64
    lastRefill time.Time
}
```

#### 4. Circuit Breaker
```go
type CircuitBreaker struct {
    state           State
    failureCount    int64
    lastFailureTime time.Time
    config          *CircuitBreakerConfig
}

type State int
const (
    Closed State = iota
    Open
    HalfOpen
)
```

## Request Processing Pipeline

### Request Flow

1. **Request Reception**
   - HTTP request received on port 8000
   - Connection pooling and keep-alive management
   - Request parsing and validation

2. **Middleware Chain**
   ```go
   func (g *Gateway) ServeHTTP(w http.ResponseWriter, r *http.Request) {
       ctx := context.WithValue(r.Context(), "correlation_id", generateCorrelationID())
       r = r.WithContext(ctx)
       
       // Middleware chain execution
       handler := g.router
       for i := len(g.middlewares) - 1; i >= 0; i-- {
           handler = g.middlewares[i](handler)
       }
       
       handler.ServeHTTP(w, r)
   }
   ```

3. **Authentication Check**
   - Extract JWT token from Authorization header or cookies
   - Validate token with Auth Service
   - Cache valid tokens for performance
   - Inject user context into request

4. **Rate Limiting**
   - Determine rate limit key (IP, user ID, API key)
   - Check token bucket for available tokens
   - Apply endpoint-specific or user-tier limits
   - Return 429 if rate limited

5. **Service Discovery**
   - Match request path to backend service
   - Check service health and circuit breaker state
   - Select healthy service instance (load balancing)

6. **Request Proxying**
   - Modify request headers (add correlation ID, user context)
   - Forward request to backend service
   - Handle timeouts and retries
   - Stream response back to client

7. **Response Processing**
   - Add standard response headers
   - Log request metrics and performance data
   - Handle errors and format error responses

## Scalability Architecture

### Horizontal Scaling

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    spec:
      containers:
      - name: gateway
        image: api-gateway:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### Load Balancing Strategies

1. **Round Robin**: Default strategy for backend services
2. **Weighted Round Robin**: For canary deployments
3. **Least Connections**: For long-lived connections
4. **Health-Based**: Exclude unhealthy instances

### Performance Characteristics

| Metric | Target | Current |
|--------|--------|---------|
| Throughput | 10k req/sec | 12k req/sec |
| Latency (P50) | < 10ms | 8ms |
| Latency (P95) | < 50ms | 35ms |
| Latency (P99) | < 100ms | 75ms |
| Memory Usage | < 512MB | 320MB |
| CPU Usage | < 50% | 25% |

## High Availability Design

### Fault Tolerance

```go
type HealthChecker struct {
    services map[string]*ServiceHealth
    interval time.Duration
    timeout  time.Duration
}

type ServiceHealth struct {
    URL            string
    Status         HealthStatus
    LastCheck      time.Time
    FailureCount   int
    CircuitBreaker *CircuitBreaker
}
```

### Circuit Breaker Implementation

```go
func (cb *CircuitBreaker) Execute(fn func() error) error {
    if cb.state == Open {
        if time.Since(cb.lastFailureTime) > cb.config.Timeout {
            cb.state = HalfOpen
        } else {
            return ErrCircuitBreakerOpen
        }
    }
    
    err := fn()
    
    if err != nil {
        cb.recordFailure()
        return err
    }
    
    cb.recordSuccess()
    return nil
}
```

### Graceful Shutdown

```go
func (g *Gateway) Shutdown(ctx context.Context) error {
    // Stop accepting new connections
    g.server.SetKeepAlivesEnabled(false)
    
    // Gracefully shutdown with timeout
    return g.server.Shutdown(ctx)
}

// Signal handling
func main() {
    gateway := NewGateway()
    
    c := make(chan os.Signal, 1)
    signal.Notify(c, os.Interrupt, syscall.SIGTERM)
    
    go func() {
        <-c
        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()
        gateway.Shutdown(ctx)
    }()
    
    gateway.Start()
}
```

## Security Architecture

### Authentication Flow

```
Client Request
     |
     ▼
┌─────────────┐
│Extract Token│
└─────────────┘
     |
     ▼
┌─────────────┐    ┌─────────────┐
│Token Cache  │───▶│Auth Service │
│Lookup       │    │Validation   │
└─────────────┘    └─────────────┘
     |                    |
     ▼                    ▼
┌─────────────┐    ┌─────────────┐
│Cache Hit:   │    │Token Valid: │
│Allow Request│    │Cache & Allow│
└─────────────┘    └─────────────┘
```

### JWT Token Validation

```go
type TokenValidator struct {
    authServiceURL string
    cache         *TokenCache
    client        *http.Client
}

func (tv *TokenValidator) ValidateToken(token string) (*UserContext, error) {
    // Check cache first
    if user, found := tv.cache.Get(token); found {
        return user, nil
    }
    
    // Validate with auth service
    resp, err := tv.client.Post(tv.authServiceURL+"/verify", 
        "application/json", strings.NewReader(`{"token":"`+token+`"}`))
    
    if err != nil {
        return nil, err
    }
    
    if resp.StatusCode == 200 {
        var user UserContext
        json.NewDecoder(resp.Body).Decode(&user)
        
        // Cache valid token
        tv.cache.Set(token, &user, 15*time.Minute)
        return &user, nil
    }
    
    return nil, ErrInvalidToken
}
```

### CORS Configuration

```go
func (g *Gateway) setupCORS() {
    g.corsOptions = &cors.Options{
        AllowedOrigins: []string{
            "https://projectzero.com",
            "https://admin.projectzero.com", 
            "http://localhost:3000", // Development
        },
        AllowedMethods: []string{
            http.MethodGet,
            http.MethodPost,
            http.MethodPut,
            http.MethodDelete,
            http.MethodOptions,
        },
        AllowedHeaders: []string{
            "Content-Type",
            "Authorization", 
            "X-Correlation-ID",
        },
        AllowCredentials: true,
        MaxAge:          300,
    }
}
```

## Monitoring and Observability

### Metrics Collection

```go
type Metrics struct {
    requestCount    prometheus.Counter
    requestDuration prometheus.Histogram
    errorRate      prometheus.Gauge
    activeRequests prometheus.Gauge
}

func (m *Metrics) RecordRequest(method, path string, duration time.Duration, statusCode int) {
    m.requestCount.WithLabelValues(method, path, strconv.Itoa(statusCode)).Inc()
    m.requestDuration.WithLabelValues(method, path).Observe(duration.Seconds())
    
    if statusCode >= 400 {
        m.errorRate.Inc()
    }
}
```

### Distributed Tracing

```go
func (g *Gateway) addTracing(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Extract or generate correlation ID
        correlationID := r.Header.Get("X-Correlation-ID")
        if correlationID == "" {
            correlationID = generateCorrelationID()
        }
        
        // Add to request context
        ctx := context.WithValue(r.Context(), "correlation_id", correlationID)
        r = r.WithContext(ctx)
        
        // Add to response headers
        w.Header().Set("X-Correlation-ID", correlationID)
        
        // Propagate to backend services
        r.Header.Set("X-Correlation-ID", correlationID)
        
        next.ServeHTTP(w, r)
    })
}
```

### Logging Strategy

```go
type LogEntry struct {
    Timestamp     time.Time `json:"timestamp"`
    Level         string    `json:"level"`
    CorrelationID string    `json:"correlation_id"`
    Method        string    `json:"method"`
    Path          string    `json:"path"`
    UserID        string    `json:"user_id,omitempty"`
    Service       string    `json:"backend_service"`
    Duration      int64     `json:"response_time_ms"`
    StatusCode    int       `json:"status_code"`
    Error         string    `json:"error,omitempty"`
    UserAgent     string    `json:"user_agent"`
    ClientIP      string    `json:"client_ip"`
}
```

---
**Architecture Owner**: Platform Engineering Team  
**Next Architecture Review**: 2025-12-29  
**Related Documents**: [Technology Choices](./technology-choices.md) | [Deployment Guide](../operations/deployment-runbook.md)