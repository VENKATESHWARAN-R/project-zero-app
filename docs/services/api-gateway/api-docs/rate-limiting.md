# API Gateway Rate Limiting

**Author**: Platform Engineering Team  
**Created**: 2025-09-29  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0  
**Owner**: Platform Engineering Team  
**Related**: [Routing Rules](./routing-rules.md) | [Authentication](./authentication.md)  
**Review Date**: 2025-12-29  

## Summary

Rate limiting configuration and implementation in the API Gateway using token bucket algorithm for request throttling and abuse prevention.

## Rate Limiting Strategy

### Token Bucket Algorithm

The gateway implements a token bucket algorithm with the following characteristics:
- **Bucket Capacity**: Maximum number of tokens (burst capacity)
- **Refill Rate**: Tokens added per time window
- **Token Cost**: Each request consumes 1 token
- **Overflow**: Excess tokens are discarded

### Rate Limit Tiers

| Tier | Requests/Minute | Burst Capacity | Applied To |
|------|-----------------|----------------|------------|
| Public | 60 | 100 | Unauthenticated users (by IP) |
| Authenticated | 120 | 200 | Authenticated users (by user ID) |
| Premium | 300 | 500 | Premium account users |
| Admin | 1000 | 2000 | Admin users |
| Internal | Unlimited | N/A | Service-to-service calls |

### Configuration

```bash
# Default rate limiting
GATEWAY_RATE_LIMIT_REQUESTS=100      # Requests per window
GATEWAY_RATE_LIMIT_WINDOW=1m         # Time window
GATEWAY_RATE_LIMIT_BURST=200         # Burst capacity

# Advanced configuration
GATEWAY_RATE_LIMIT_STRATEGY=token_bucket
GATEWAY_RATE_LIMIT_KEY_GENERATOR=composite  # ip+user_id
GATEWAY_RATE_LIMIT_SKIP_SUCCESSFUL_REQUESTS=false
```

## Rate Limiting Implementation

### Request Classification

```go
type RateLimitKey struct {
    Type    string // "ip", "user", "api_key"
    Value   string // IP address, user ID, or API key
    Tier    string // "public", "authenticated", "premium", "admin"
}

func (g *Gateway) generateRateLimitKey(r *http.Request, user *User) RateLimitKey {
    if user != nil {
        return RateLimitKey{
            Type:  "user",
            Value: user.ID,
            Tier:  user.Tier,
        }
    }
    
    return RateLimitKey{
        Type:  "ip",
        Value: getClientIP(r),
        Tier:  "public",
    }
}
```

### Token Bucket Implementation

```go
type TokenBucket struct {
    capacity     int64
    tokens       int64
    refillRate   int64
    lastRefill   time.Time
    mutex        sync.Mutex
}

func (tb *TokenBucket) AllowRequest() bool {
    tb.mutex.Lock()
    defer tb.mutex.Unlock()
    
    now := time.Now()
    elapsed := now.Sub(tb.lastRefill)
    
    // Refill tokens based on elapsed time
    tokensToAdd := int64(elapsed.Seconds()) * tb.refillRate
    tb.tokens = min(tb.capacity, tb.tokens+tokensToAdd)
    tb.lastRefill = now
    
    // Check if request can be served
    if tb.tokens > 0 {
        tb.tokens--
        return true
    }
    
    return false
}
```

## Rate Limit Response Headers

### Standard Headers

All responses include rate limit information:

```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 60
```

### Rate Limited Response

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 30
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 120,
      "window": "1m",
      "retry_after": 30
    }
  },
  "correlation_id": "req-123456789"
}
```

## Rate Limiting Policies

### Endpoint-Specific Limits

```yaml
endpoint_policies:
  - path: "/api/auth/login"
    limit: 5
    window: "5m"
    burst: 10
    description: "Login attempt throttling"
    
  - path: "/api/products/search"
    limit: 30
    window: "1m" 
    burst: 50
    description: "Search query throttling"
    
  - path: "/api/cart/*"
    limit: 60
    window: "1m"
    burst: 100
    description: "Cart operation throttling"
    
  - path: "/api/orders"
    method: "POST"
    limit: 10
    window: "1h"
    burst: 15
    description: "Order creation throttling"
```

### User Tier-Based Limits

```go
var tierLimits = map[string]RateLimit{
    "public": {
        Requests: 60,
        Window:   time.Minute,
        Burst:    100,
    },
    "authenticated": {
        Requests: 120,
        Window:   time.Minute,
        Burst:    200,
    },
    "premium": {
        Requests: 300,
        Window:   time.Minute,
        Burst:    500,
    },
    "admin": {
        Requests: 1000,
        Window:   time.Minute,
        Burst:    2000,
    },
}
```

## Monitoring and Alerting

### Rate Limit Metrics

- **Request Volume**: Total requests per endpoint
- **Rate Limit Hits**: Number of rate-limited requests
- **Rate Limit Ratio**: Percentage of requests rate-limited
- **Top Rate-Limited IPs**: Most frequently rate-limited IP addresses
- **Top Rate-Limited Users**: Most frequently rate-limited users

### Alerting Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Rate Limit Ratio | > 5% | > 15% | Investigate traffic patterns |
| Unique Rate-Limited IPs | > 100 | > 500 | Check for DDoS attack |
| Single IP Rate Limits | > 1000/hour | > 5000/hour | Consider IP blocking |
| Authentication Failures | > 10/min | > 50/min | Check for brute force |

## Bypass and Whitelisting

### Service-to-Service Calls

```go
// Internal service authentication bypass
if isInternalServiceCall(r) {
    // Skip rate limiting for service-to-service calls
    return next.ServeHTTP(w, r)
}

// Check for internal service token
func isInternalServiceCall(r *http.Request) bool {
    token := r.Header.Get("X-Internal-Service-Token")
    return validateInternalToken(token)
}
```

### IP Whitelisting

```yaml
rate_limit_whitelist:
  ips:
    - "10.0.0.0/8"      # Internal network
    - "172.16.0.0/12"   # Docker networks
    - "192.168.0.0/16"  # Private networks
  
  user_agents:
    - "HealthCheck/1.0"  # Health check bots
    - "Monitoring/2.0"   # Monitoring systems
```

## Rate Limit Strategies

### Adaptive Rate Limiting

```go
type AdaptiveRateLimit struct {
    baseLimit    int64
    currentLimit int64
    errorRate    float64
    lastUpdate   time.Time
}

func (arl *AdaptiveRateLimit) adjustLimit() {
    if arl.errorRate > 0.05 { // 5% error rate
        // Reduce limit during high error rates
        arl.currentLimit = int64(float64(arl.baseLimit) * 0.8)
    } else if arl.errorRate < 0.01 { // 1% error rate
        // Increase limit during stable periods
        arl.currentLimit = int64(float64(arl.baseLimit) * 1.2)
    }
}
```

### Geographic Rate Limiting

```go
// Different limits based on geographic region
var geoLimits = map[string]int64{
    "US": 120,  // Higher limit for US traffic
    "EU": 100,  // Standard limit for EU traffic  
    "AS": 80,   // Lower limit for Asian traffic
    "XX": 60,   // Lowest limit for unknown regions
}
```

## Testing Rate Limits

### Load Testing Script

```bash
#!/bin/bash
# Test rate limiting with curl

echo "Testing rate limiting..."
for i in {1..150}; do
    response=$(curl -s -w ",%{http_code}" http://localhost:8000/api/products)
    status_code=$(echo $response | cut -d',' -f2)
    
    if [ $status_code -eq 429 ]; then
        echo "Request $i: Rate limited (429)"
        break
    else
        echo "Request $i: Success ($status_code)"
    fi
    
    sleep 0.1
done
```

### Rate Limit Testing

```go
// Test rate limiting functionality
func TestRateLimiting(t *testing.T) {
    gateway := setupTestGateway()
    
    // Configure low rate limit for testing
    gateway.RateLimit = &RateLimit{
        Requests: 5,
        Window:   time.Minute,
        Burst:    5,
    }
    
    // Make requests up to the limit
    for i := 0; i < 5; i++ {
        resp := makeRequest(gateway, "/api/products")
        assert.Equal(t, 200, resp.StatusCode)
    }
    
    // Next request should be rate limited
    resp := makeRequest(gateway, "/api/products")
    assert.Equal(t, 429, resp.StatusCode)
    
    // Check rate limit headers
    assert.Equal(t, "5", resp.Header.Get("X-RateLimit-Limit"))
    assert.Equal(t, "0", resp.Header.Get("X-RateLimit-Remaining"))
}
```

---
**Rate Limiting Owner**: Platform Engineering Team  
**Next Review**: 2025-12-29