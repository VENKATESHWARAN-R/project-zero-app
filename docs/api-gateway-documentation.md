# API Gateway Service - Comprehensive API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Authentication](#authentication)
4. [Rate Limiting](#rate-limiting)
5. [Health & Management Endpoints](#health--management-endpoints)
6. [Proxy Endpoints](#proxy-endpoints)
7. [Configuration](#configuration)
8. [Error Responses](#error-responses)
9. [Client Examples](#client-examples)
10. [Service Integration](#service-integration)

## Overview

The API Gateway serves as the single entry point for all client requests to the Project Zero App microservices ecosystem. Built with Go and the Gin web framework, it provides intelligent routing, authentication, rate limiting, circuit breaking, and comprehensive observability features.

**Base URL**: `http://localhost:8000`
**Protocol**: HTTP/1.1
**Content-Type**: `application/json`
**CORS**: Enabled for all origins (development configuration)

### Key Features

- **Request Routing**: Intelligent routing to backend microservices based on URL patterns
- **Service Discovery**: Automatic registration and health monitoring of backend services
- **Rate Limiting**: Token bucket algorithm for request throttling
- **Circuit Breaking**: Automatic failure detection and recovery
- **Authentication Proxy**: JWT token validation with auth service integration
- **CORS Support**: Cross-origin request handling for web frontends
- **Structured Logging**: JSON logging with correlation IDs
- **Health Monitoring**: Continuous health checking of registered services

## Architecture

### Request Flow

```
Client Request
    ↓
CORS Middleware
    ↓
Rate Limiting Middleware (planned)
    ↓
Authentication Middleware (planned)
    ↓
Circuit Breaker Middleware (planned)
    ↓
Logging Middleware
    ↓
Route Resolution
    ↓
Reverse Proxy Handler (planned)
    ↓
Backend Service
```

### Service Registry

The gateway maintains an in-memory service registry that:
- Registers services from configuration
- Performs health checks every 30 seconds
- Routes requests based on URL patterns
- Provides service status information

## Authentication

### Current Implementation

Authentication is currently configured but not fully implemented in the middleware chain. The gateway is designed to integrate with the Auth Service for JWT token validation.

### Planned Authentication Flow

1. Client includes JWT token in `Authorization` header
2. Gateway validates token with Auth Service (`/auth/verify`)
3. Gateway forwards request with validated user context
4. Backend service receives authenticated request

### Headers

```http
Authorization: Bearer <jwt_token>
X-Correlation-ID: <optional_correlation_id>
```

## Rate Limiting

### Configuration

Rate limiting is configured but not yet implemented in the middleware chain. The planned implementation uses a token bucket algorithm.

**Default Limits**:
- **Requests**: 100 per window
- **Window**: 1 minute
- **Burst**: 200 requests
- **Scope**: Per IP address

### Headers (Planned)

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Health & Management Endpoints

### GET /health

Returns the health status of the gateway itself.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-09-27T10:30:00Z",
  "version": "1.0.0",
  "uptime": "1m"
}
```

### GET /health/ready

Returns readiness status including all dependent services.

**Response** (200 OK when all services healthy):
```json
{
  "status": "ready",
  "timestamp": "2025-09-27T10:30:00Z",
  "services": {
    "auth-service": {
      "name": "auth-service",
      "status": "healthy",
      "url": "http://localhost:8001",
      "last_checked": "2025-09-27T10:29:45Z",
      "response_time": 25.5
    },
    "product-service": {
      "name": "product-service",
      "status": "healthy",
      "url": "http://localhost:8004",
      "last_checked": "2025-09-27T10:29:45Z",
      "response_time": 15.2
    }
  }
}
```

**Response** (503 Service Unavailable when services unhealthy):
```json
{
  "status": "not_ready",
  "timestamp": "2025-09-27T10:30:00Z",
  "services": {
    "auth-service": {
      "name": "auth-service",
      "status": "unhealthy",
      "url": "http://localhost:8001",
      "last_checked": "2025-09-27T10:29:45Z"
    }
  }
}
```

### GET /gateway/services

Lists all registered services and their health status.

**Response** (200 OK):
```json
{
  "services": [
    {
      "name": "auth-service",
      "status": "healthy",
      "url": "http://localhost:8001",
      "last_checked": "2025-09-27T10:29:45Z",
      "response_time": 25.5
    },
    {
      "name": "product-service",
      "status": "healthy",
      "url": "http://localhost:8004",
      "last_checked": "2025-09-27T10:29:45Z",
      "response_time": 15.2
    }
  ],
  "total": 2
}
```

### GET /gateway/routes

Lists all configured routing rules.

**Response** (200 OK):
```json
{
  "routes": [
    {
      "path": "/api/auth/*",
      "service_name": "auth-service",
      "auth_required": false
    },
    {
      "path": "/api/products/*",
      "service_name": "product-service",
      "method": "GET",
      "strip_prefix": true,
      "auth_required": true
    }
  ],
  "total": 2
}
```

### GET /gateway/metrics

Returns performance and usage metrics.

**Response** (200 OK):
```json
{
  "timestamp": "2025-09-27T10:30:00Z",
  "requests": {
    "total": 0,
    "success": 0,
    "errors": 0,
    "avg_response_time": 0.0
  },
  "rate_limits": {
    "active_limiters": 0,
    "blocked_requests": 0
  },
  "circuit_breakers": {},
  "services": {
    "auth-service": {
      "name": "auth-service",
      "status": "healthy",
      "url": "http://localhost:8001",
      "last_checked": "2025-09-27T10:29:45Z",
      "response_time": 25.5
    }
  }
}
```

## Proxy Endpoints

### ANY /api/*proxyPath

Routes requests to appropriate backend services based on configured routing rules.

**Current Implementation**: Returns route resolution information (proxy logic planned).

**Request**:
```http
GET /api/auth/verify HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (200 OK):
```json
{
  "message": "Proxy endpoint found",
  "route": "/api/auth/*",
  "service": "auth-service",
  "target_url": "http://localhost:8001",
  "method": "GET",
  "path": "/api/auth/verify"
}
```

**Response** (404 Not Found):
```json
{
  "error": "Route not found",
  "message": "No route found for GET /api/unknown"
}
```

### Planned Proxy Behavior

When fully implemented, the gateway will:
1. Resolve route based on path pattern matching
2. Apply authentication middleware if required
3. Apply rate limiting
4. Forward request to backend service
5. Return backend response transparently
6. Log request/response for observability

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_SERVER_HOST` | `0.0.0.0` | Server bind address |
| `GATEWAY_SERVER_PORT` | `8000` | Server port |
| `GATEWAY_RATE_LIMIT_REQUESTS` | `100` | Requests per window |
| `GATEWAY_RATE_LIMIT_WINDOW` | `1m` | Rate limiting window |
| `GATEWAY_RATE_LIMIT_BURST` | `200` | Burst capacity |
| `GATEWAY_AUTH_SERVICE_URL` | `http://localhost:8001` | Auth service URL |
| `GATEWAY_LOGGING_LEVEL` | `info` | Log level (debug, info, warn, error) |

### Configuration File

The gateway supports YAML configuration files:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  read_timeout: "30s"
  write_timeout: "30s"
  idle_timeout: "60s"

services:
  auth-service:
    name: "auth-service"
    url: "http://localhost:8001"
    timeout: "30s"
    health_path: "/health"
    enabled: true

  product-service:
    name: "product-service"
    url: "http://localhost:8004"
    timeout: "30s"
    health_path: "/health"
    enabled: true

routes:
  - path: "/api/auth/*"
    service_name: "auth-service"
    auth_required: false

  - path: "/api/products/*"
    service_name: "product-service"
    method: "GET"
    strip_prefix: true
    auth_required: true

rate_limit:
  requests: 100
  window: "1m"
  burst: 200
  scope: "per_ip"
  enabled: true

circuit_breaker:
  max_requests: 3
  interval: "60s"
  timeout: "30s"
  failure_threshold: 0.6

auth:
  service_url: "http://localhost:8001"
  timeout: "5s"
  cache_ttl: "5m"

logging:
  level: "info"
  format: "json"
```

## Error Responses

### Standard Error Format

All error responses follow a consistent format:

```json
{
  "error": "Error Type",
  "message": "Detailed error description",
  "timestamp": "2025-09-27T10:30:00Z",
  "path": "/api/example"
}
```

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Route or resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Gateway internal error |
| 502 | Bad Gateway | Backend service error |
| 503 | Service Unavailable | Backend service unavailable |
| 504 | Gateway Timeout | Backend service timeout |

### Rate Limiting Error

```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Try again in 60 seconds.",
  "timestamp": "2025-09-27T10:30:00Z",
  "retry_after": 60
}
```

### Service Unavailable Error

```json
{
  "error": "Service Unavailable",
  "message": "Backend service is currently unavailable",
  "timestamp": "2025-09-27T10:30:00Z",
  "service": "auth-service"
}
```

## Client Examples

### JavaScript/Fetch

```javascript
// Health check
const healthResponse = await fetch('http://localhost:8000/health');
const health = await healthResponse.json();
console.log('Gateway health:', health);

// Service registry
const servicesResponse = await fetch('http://localhost:8000/gateway/services');
const services = await servicesResponse.json();
console.log('Registered services:', services);

// Proxy request (with auth)
const apiResponse = await fetch('http://localhost:8000/api/auth/verify', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});
const result = await apiResponse.json();
```

### cURL

```bash
# Health check
curl -X GET http://localhost:8000/health

# Service status
curl -X GET http://localhost:8000/gateway/services

# Metrics
curl -X GET http://localhost:8000/gateway/metrics

# Proxy request
curl -X GET http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# POST request through proxy
curl -X POST http://localhost:8000/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": "123", "quantity": 2}]}'
```

### Python/Requests

```python
import requests

# Gateway client
class GatewayClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def set_auth_token(self, token):
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def health_check(self):
        response = self.session.get(f"{self.base_url}/health")
        return response.json()

    def get_services(self):
        response = self.session.get(f"{self.base_url}/gateway/services")
        return response.json()

    def proxy_request(self, method, path, **kwargs):
        url = f"{self.base_url}/api{path}"
        response = self.session.request(method, url, **kwargs)
        return response

# Usage
client = GatewayClient()
client.set_auth_token("your-jwt-token")

# Check health
health = client.health_check()
print(f"Gateway status: {health['status']}")

# Make proxy request
response = client.proxy_request("GET", "/auth/verify")
print(f"Auth verification: {response.json()}")
```

## Service Integration

### Backend Service Requirements

For a service to be registered with the gateway:

1. **Health Endpoint**: Must expose `/health` endpoint returning 200 status
2. **CORS Headers**: Should support CORS if accessed directly by frontend
3. **JSON Responses**: Should return JSON formatted responses
4. **Error Handling**: Should return appropriate HTTP status codes

### Health Check Response Format

Backend services should return health status in this format:

```json
{
  "status": "healthy",
  "timestamp": "2025-09-27T10:30:00Z",
  "service": "service-name",
  "version": "1.0.0"
}
```

### Service Registration

Services are registered via configuration file or environment variables:

```yaml
services:
  my-service:
    name: "my-service"
    url: "http://localhost:8010"
    timeout: "30s"
    health_path: "/health"
    enabled: true
```

### Route Configuration

Routes define how requests are forwarded to services:

```yaml
routes:
  - path: "/api/myservice/*"
    service_name: "my-service"
    method: "*"  # or specific method like "GET"
    strip_prefix: true  # removes /api/myservice from forwarded path
    auth_required: true  # requires valid JWT token
    headers:
      X-Service-Name: "my-service"
```

### Circuit Breaker Integration

The gateway implements circuit breaker patterns:

- **Closed**: Normal operation, requests forwarded
- **Open**: Service failing, requests rejected immediately
- **Half-Open**: Testing if service recovered

Circuit breaker states are tracked per service and exposed via `/gateway/metrics`.

---

**Note**: This documentation reflects the current implementation status. Some features like full proxy functionality, authentication middleware, and rate limiting are designed but not yet fully implemented. The gateway currently provides service registry, health checking, and route resolution capabilities.