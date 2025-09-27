# Quickstart Guide: API Gateway Service

**Feature**: API Gateway Service
**Date**: 2025-09-27
**Estimated Duration**: 15-20 minutes

This quickstart guide walks through setting up, configuring, and testing the API Gateway service for the Project Zero App platform.

## Prerequisites

- Go 1.21+ installed
- Docker and Docker Compose available
- Auth Service and Order Service running (ports 8001, 8008)
- Basic understanding of REST APIs and microservices

## Quick Setup

### 1. Clone and Navigate to Project

```bash
cd /path/to/project-zero-app
git checkout 008-build-an-api
```

### 2. Build the Gateway Service

```bash
cd services/api-gateway-service
go mod init gateway
go mod tidy
go build -o gateway ./cmd/gateway
```

### 3. Configuration Setup

Create `config.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  read_timeout: "30s"
  write_timeout: "30s"
  idle_timeout: "60s"

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

routes:
  - path: "/api/auth/*"
    service_name: "auth"
    strip_prefix: false
    auth_required: false

  - path: "/api/orders/*"
    service_name: "orders"
    strip_prefix: false
    auth_required: true

rate_limit:
  name: "default"
  requests: 100
  window: "1m"
  burst: 200
  scope: "per_ip"
  enabled: true

auth:
  service_url: "http://localhost:8001"
  timeout: "5s"
  cache_ttl: "5m"
  skip_paths:
    - "/health"
    - "/health/ready"
    - "/api/auth/login"
    - "/api/auth/register"

logging:
  level: "info"
  format: "json"
```

### 4. Start the Gateway

```bash
./gateway
```

Expected output:
```
INFO[2025-09-27T10:30:00Z] Starting API Gateway service
INFO[2025-09-27T10:30:00Z] Loading configuration from config.yaml
INFO[2025-09-27T10:30:00Z] Registered service: auth-service at http://localhost:8001
INFO[2025-09-27T10:30:00Z] Registered service: order-service at http://localhost:8008
INFO[2025-09-27T10:30:00Z] Health checker started with 30s interval
INFO[2025-09-27T10:30:00Z] Server listening on :8000
```

## Basic Testing

### 1. Gateway Health Check

Test that the gateway is responding:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-27T10:30:00Z",
  "version": "1.0.0",
  "uptime": "30s"
}
```

### 2. Service Discovery Test

Check registered services:

```bash
curl http://localhost:8000/gateway/services
```

Expected response:
```json
{
  "services": [
    {
      "name": "auth-service",
      "status": "healthy",
      "url": "http://localhost:8001",
      "last_checked": "2025-09-27T10:30:00Z",
      "response_time": 25.5
    },
    {
      "name": "order-service",
      "status": "healthy",
      "url": "http://localhost:8008",
      "last_checked": "2025-09-27T10:30:00Z",
      "response_time": 32.1
    }
  ],
  "total": 2
}
```

### 3. Authentication Flow Test

First, authenticate with the auth service through the gateway:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 900
}
```

### 4. Authenticated Request Test

Use the access token to make an authenticated request:

```bash
export ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:8000/api/orders \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-Correlation-ID: $(uuidgen)"
```

Expected response:
```json
{
  "orders": [],
  "total": 0,
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 5. Rate Limiting Test

Test rate limiting by making rapid requests:

```bash
for i in {1..105}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health
done
```

Expected output (last few requests):
```
200
200
429
429
429
```

### 6. Circuit Breaker Test

Simulate service failure by stopping the auth service:

```bash
# Stop auth service
docker stop auth-service

# Try to access auth endpoint
curl http://localhost:8000/api/auth/login
```

Expected response:
```json
{
  "error": "Service temporarily unavailable",
  "message": "The auth service is currently experiencing issues",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-09-27T10:30:00Z"
}
```

## Docker Integration

### 1. Build Docker Image

```bash
docker build -t api-gateway:latest .
```

### 2. Run with Docker Compose

Update `docker-compose.yml` to include the gateway:

```yaml
version: '3.8'
services:
  api-gateway:
    build: ./services/api-gateway-service
    ports:
      - "8000:8000"
    environment:
      - SERVER_PORT=8000
      - SERVICES_AUTH_URL=http://auth-service:8001
      - SERVICES_ORDERS_URL=http://order-service:8008
    depends_on:
      - auth-service
      - order-service
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  auth-service:
    # existing auth service config

  order-service:
    # existing order service config
```

### 3. Start All Services

```bash
docker-compose up -d
```

### 4. Test Gateway in Docker

```bash
# Wait for services to start
sleep 30

# Test gateway health
curl http://localhost:8000/health

# Test service routing
curl http://localhost:8000/gateway/services
```

## Advanced Configuration

### 1. Environment Variable Override

```bash
export SERVER_PORT=8080
export RATE_LIMIT_GLOBAL=50
export AUTH_SERVICE_URL=http://auth.internal:8001
./gateway
```

### 2. Production Configuration

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  read_timeout: "30s"
  write_timeout: "30s"
  idle_timeout: "120s"

rate_limit:
  requests: 1000
  window: "1m"
  burst: 2000
  scope: "per_ip"

circuit_breaker:
  max_requests: 5
  interval: "60s"
  timeout: "30s"
  failure_threshold: 0.6

logging:
  level: "warn"
  format: "json"
  output_file: "/var/log/gateway.log"
```

### 3. TLS Configuration

```yaml
server:
  tls_enabled: true
  cert_file: "/etc/ssl/certs/gateway.crt"
  key_file: "/etc/ssl/private/gateway.key"
```

## Monitoring and Observability

### 1. Metrics Endpoint

```bash
curl http://localhost:8000/gateway/metrics
```

### 2. Request Tracing

All requests include correlation IDs for distributed tracing:

```bash
curl -H "X-Correlation-ID: custom-trace-id" \
     http://localhost:8000/api/auth/login
```

### 3. Log Analysis

Gateway logs are structured JSON for easy parsing:

```bash
tail -f gateway.log | jq '.correlation_id, .path, .status_code, .duration'
```

## Troubleshooting

### Common Issues

1. **Service Discovery Failures**
   ```bash
   # Check service health
   curl http://localhost:8000/gateway/services

   # Verify backend service accessibility
   curl http://localhost:8001/health
   ```

2. **Authentication Issues**
   ```bash
   # Test auth service directly
   curl http://localhost:8001/auth/verify \
     -H "Authorization: Bearer $ACCESS_TOKEN"
   ```

3. **Rate Limiting Problems**
   ```bash
   # Check current rate limit status
   curl http://localhost:8000/gateway/metrics | jq '.rate_limits'
   ```

4. **Circuit Breaker Status**
   ```bash
   # Check circuit breaker states
   curl http://localhost:8000/gateway/metrics | jq '.circuit_breakers'
   ```

### Performance Tuning

1. **Memory Usage**: Monitor with `top` or `htop`
2. **Response Times**: Check metrics endpoint regularly
3. **Rate Limits**: Adjust based on traffic patterns
4. **Circuit Breaker**: Tune thresholds based on service reliability

## Next Steps

1. **Production Deployment**: Set up with proper TLS certificates
2. **Monitoring Integration**: Connect to Prometheus/Grafana
3. **Load Testing**: Use tools like `hey` or `ab` to test under load
4. **Security Hardening**: Implement additional security headers
5. **Service Mesh**: Consider integration with Istio or Linkerd

## API Documentation

Full API documentation is available at:
- OpenAPI Spec: `./contracts/gateway-api.yaml`
- Interactive Docs: `http://localhost:8000/docs` (when implemented)

## Support

For issues or questions:
1. Check the logs first: `docker logs api-gateway`
2. Review the configuration: `./gateway --check-config`
3. Test individual components: Use the troubleshooting commands above
4. Consult the full documentation in the service README

This quickstart guide provides a complete walkthrough of setting up and testing the API Gateway service. The gateway should now be successfully routing requests to your backend services with authentication, rate limiting, and circuit breaking capabilities.