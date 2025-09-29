# API Gateway Service Documentation

**Service**: API Gateway  
**Technology**: Go 1.20+, Gorilla Mux, net/http  
**Port**: 8000  
**Owner**: Platform Engineering Team  
**On-Call**: [See contacts/engineering-teams.md]  
**Status**: Production Ready  
**Last Updated**: 2025-09-29  

## Quick Links

- [Routing Rules](./api-docs/routing-rules.md)
- [Rate Limiting](./api-docs/rate-limiting.md)
- [Authentication Flow](./api-docs/authentication.md)
- [Architecture Overview](./architecture/overview.md)
- [Deployment Runbook](./operations/deployment-runbook.md)
- [Troubleshooting Guide](./troubleshooting/common-issues.md)
- [Monitoring Dashboard](./monitoring/metrics-and-alerts.md)

## Service Overview

The API Gateway serves as the single entry point for all client requests to the Project Zero App platform. It provides intelligent request routing, authentication middleware, rate limiting, circuit breaking, and observability for the entire microservices ecosystem.

### Key Responsibilities

- **Request Routing**: Route incoming requests to appropriate backend services based on URL patterns
- **Authentication Middleware**: Validate JWT tokens and enforce authentication requirements
- **Rate Limiting**: Implement configurable rate limiting using token bucket algorithm
- **Circuit Breaking**: Prevent cascade failures with automatic circuit breaker patterns
- **Service Discovery**: Monitor backend service health and route traffic accordingly
- **CORS Handling**: Manage cross-origin requests for browser-based clients
- **Logging & Observability**: Structured logging with correlation IDs for distributed tracing
- **Graceful Shutdown**: Clean resource handling during deployment and maintenance

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Client Apps   │◄──►│   API Gateway    │◄──►│  Backend Services   │
│  (Frontend/API) │    │   (Port 8000)    │    │   (Multiple Ports)  │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                ▲
                                │
                       ┌────────┼────────┐
                       ▼        ▼        ▼
                   ┌─────┐  ┌─────┐  ┌─────┐
                   │Auth │  │Logs │  │Metrics│
                   └─────┘  └─────┘  └─────┘
```

### Service Routing Map

| Route Pattern | Target Service | Port | Authentication Required |
|---------------|----------------|------|------------------------|
| `/api/auth/*` | Auth Service | 8001 | No (handles auth itself) |
| `/api/profile/*` | User Profile Service | 8002 | Yes |
| `/api/products/*` | Product Catalog Service | 8004 | No (public catalog) |
| `/api/cart/*` | Cart Service | 8007 | Yes |
| `/api/orders/*` | Order Service | 8008 | Yes |
| `/api/payments/*` | Payment Service | 8009 | Yes |
| `/api/notifications/*` | Notification Service | 8011 | Yes |
| `/gateway/*` | Gateway Management | N/A | Admin only |

## Technology Stack Details

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Go | 1.20+ | High-performance HTTP handling |
| HTTP Router | Gorilla Mux | 1.8+ | Flexible HTTP request routing |
| HTTP Client | net/http | Native | Backend service communication |
| Rate Limiting | Token Bucket | Custom | Request rate control |
| Circuit Breaker | Custom Implementation | 1.0 | Fault tolerance |
| Logging | Structured JSON | Custom | Observability |
| Configuration | Environment Variables | Native | Runtime configuration |

### Performance Characteristics

- **Throughput**: 10,000+ requests per second under normal load
- **Latency**: < 50ms routing overhead (P95)
- **Memory Usage**: ~50MB base footprint
- **CPU Usage**: < 10% under normal load
- **Connection Pooling**: Persistent connections to backend services
- **Timeout Handling**: 30s request timeout, 10s backend timeout

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| `GATEWAY_SERVER_HOST` | Bind address | `0.0.0.0` | No |
| `GATEWAY_SERVER_PORT` | Service port | `8000` | No |
| `GATEWAY_AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | Yes |
| `GATEWAY_RATE_LIMIT_REQUESTS` | Requests per window | `100` | No |
| `GATEWAY_RATE_LIMIT_WINDOW` | Rate limit window | `1m` | No |
| `GATEWAY_RATE_LIMIT_BURST` | Burst capacity | `200` | No |
| `GATEWAY_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Circuit breaker trigger | `0.6` | No |
| `GATEWAY_LOGGING_LEVEL` | Log level | `info` | No |

### Service Discovery Configuration

Backend services are configured via environment variables:

```bash
# Service URLs
GATEWAY_AUTH_SERVICE_URL=http://localhost:8001
GATEWAY_PROFILE_SERVICE_URL=http://localhost:8002
GATEWAY_PRODUCT_SERVICE_URL=http://localhost:8004
GATEWAY_CART_SERVICE_URL=http://localhost:8007
GATEWAY_ORDER_SERVICE_URL=http://localhost:8008
GATEWAY_PAYMENT_SERVICE_URL=http://localhost:8009
GATEWAY_NOTIFICATION_SERVICE_URL=http://localhost:8011
```

## Key Features

### Request Routing

- **Pattern-Based Routing**: URL pattern matching with variable capture
- **Method-Based Routing**: HTTP method-specific routing rules
- **Header-Based Routing**: Route based on request headers (future enhancement)
- **Load Balancing**: Round-robin between multiple backend instances (when available)

### Authentication Middleware

```go
type AuthMiddleware struct {
    authServiceURL string
    skipPaths      []string
    client        *http.Client
}

// Validates JWT tokens by calling auth service
func (a *AuthMiddleware) ValidateToken(token string) (*User, error)

// Middleware function for protected routes
func (a *AuthMiddleware) Middleware(next http.Handler) http.Handler
```

### Rate Limiting

- **Algorithm**: Token bucket with configurable refill rate
- **Granularity**: Per-IP, per-user, and global rate limiting
- **Configuration**: Runtime configurable via environment variables
- **Response**: 429 Too Many Requests with Retry-After header

### Circuit Breaker

- **States**: Closed, Open, Half-Open
- **Failure Threshold**: Configurable failure percentage (default 60%)
- **Timeout**: 30-second timeout before attempting half-open
- **Monitoring**: Circuit breaker state changes logged and monitored

## Health Checks

### Gateway Health Endpoints

```
GET /health
Response: {"status": "healthy", "timestamp": "2025-09-29T10:00:00Z"}
Status: 200 OK (always returns healthy if gateway is responding)

GET /health/ready
Response: {
  "status": "ready",
  "dependencies": {
    "auth-service": "healthy",
    "profile-service": "healthy", 
    "product-service": "healthy",
    "cart-service": "degraded",
    "order-service": "healthy",
    "payment-service": "healthy",
    "notification-service": "healthy"
  },
  "timestamp": "2025-09-29T10:00:00Z"
}
Status: 200 OK (if majority of services healthy), 503 Service Unavailable (if critical services down)
```

### Backend Service Health Monitoring

- Health checks performed every 30 seconds
- Services marked as unhealthy after 3 consecutive failures
- Automatic recovery detection and traffic restoration
- Circuit breaker integration for failed services

## Monitoring and Observability

### Metrics Collection

- **Request Count**: Total requests by route, method, status code
- **Response Time**: Latency distribution (P50, P95, P99)
- **Error Rate**: 4xx and 5xx response rates
- **Circuit Breaker**: State changes and failure counts
- **Rate Limiting**: Request denials and quota utilization

### Structured Logging

```json
{
  "timestamp": "2025-09-29T10:00:00Z",
  "level": "info",
  "correlation_id": "req-123456789",
  "method": "POST",
  "path": "/api/orders",
  "user_id": "user-456",
  "backend_service": "order-service",
  "response_time_ms": 145,
  "status_code": 201,
  "error": null
}
```

### Correlation ID Tracking

- Unique correlation ID generated for each request
- Propagated to all backend services via `X-Correlation-ID` header
- Enables distributed tracing across the entire request lifecycle

## Security Features

### Authentication Enforcement

- JWT token validation for protected routes
- Automatic token refresh handling
- Configurable skip paths for public endpoints
- User context injection for downstream services

### CORS Configuration

```go
corsOptions := cors.Options{
    AllowedOrigins: []string{"https://projectzero.com", "http://localhost:3000"},
    AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
    AllowedHeaders: []string{"Content-Type", "Authorization"},
    AllowCredentials: true,
    MaxAge: 300,
}
```

### Request Validation

- Request size limits (10MB default)
- Content-Type validation
- Header size limits
- Request timeout enforcement

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after": 60,
      "limit": 100,
      "window": "1m"
    }
  },
  "correlation_id": "req-123456789",
  "timestamp": "2025-09-29T10:00:00Z"
}
```

### Common Error Codes

- `AUTHENTICATION_REQUIRED`: Missing or invalid authentication
- `RATE_LIMIT_EXCEEDED`: Rate limit quota exceeded
- `SERVICE_UNAVAILABLE`: Backend service unavailable
- `CIRCUIT_BREAKER_OPEN`: Circuit breaker protecting backend service
- `INVALID_REQUEST`: Malformed request
- `TIMEOUT`: Request timeout exceeded

## Development Environment

### Prerequisites

- Go 1.20 or higher
- Docker (optional, for containerized backends)
- Access to backend services

### Local Development Setup

```bash
# Clone repository and navigate to gateway
cd services/api-gateway-service

# Install dependencies
go mod tidy

# Set up environment variables
cp .env.example .env
# Edit .env with appropriate service URLs

# Build and run
go build -o gateway ./cmd/gateway
./gateway

# Gateway will be available at http://localhost:8000
```

### Testing

```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run contract tests
go test ./tests/contract/...

# Run integration tests (requires running backend services)
go test ./tests/integration/...
```

## Deployment Information

### Build Process

```bash
# Build for production
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gateway ./cmd/gateway

# Docker build
docker build -t api-gateway:latest .

# Multi-arch build
docker buildx build --platform linux/amd64,linux/arm64 -t api-gateway:latest .
```

### Deployment Strategies

- **Blue-Green Deployment**: Zero-downtime deployments with traffic switching
- **Rolling Updates**: Gradual instance replacement
- **Canary Deployment**: Gradual traffic shifting to new version

### Infrastructure Requirements

- **CPU**: 1-2 cores minimum, 4+ cores for high traffic
- **Memory**: 512MB minimum, 2GB recommended for high traffic
- **Network**: High bandwidth for request proxying
- **Storage**: Minimal (logs only)

## Emergency Procedures

### Incident Response

1. **Check Gateway Health**: Verify `/health` and `/health/ready` endpoints
2. **Review Metrics**: Check request volume, error rates, and latency
3. **Examine Logs**: Look for error patterns and correlation IDs
4. **Backend Service Health**: Verify backend service connectivity
5. **Circuit Breaker Status**: Check if circuit breakers are open

### Common Emergency Scenarios

- **Backend Service Failure**: Circuit breaker automatically protects, manual traffic routing if needed
- **Rate Limiting Issues**: Adjust rate limits via environment variables and restart
- **Authentication Failures**: Check auth service connectivity and JWT validation
- **High Latency**: Monitor backend services and consider circuit breaker tuning

### Rollback Procedure

1. Identify previous stable version
2. Update deployment to previous version
3. Verify all health checks pass
4. Monitor error rates and latency
5. Notify stakeholders of rollback completion

---

**Service Owner**: Platform Engineering Team  
**Technical Lead**: Michael Rodriguez <michael.rodriguez@projectzero.com>  
**On-Call Rotation**: [See contacts/on-call-schedule.md]  
**Last Health Check**: 2025-09-29 ✅ Healthy  
**Next Review**: 2025-12-29