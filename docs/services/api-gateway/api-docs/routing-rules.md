# API Gateway Routing Rules

**Author**: Platform Engineering Team  
**Created**: 2025-09-29  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0  
**Owner**: Platform Engineering Team  
**Related**: [Architecture Overview](../architecture/overview.md)  
**Review Date**: 2025-12-29  

## Summary

Detailed routing configuration and rules for the Project Zero App API Gateway, including path patterns, service mappings, and routing logic.

## Routing Configuration

### Route Mapping Table

| Route Pattern | HTTP Methods | Target Service | Port | Auth Required | Description |
|---------------|--------------|----------------|------|---------------|-------------|
| `/api/auth/*` | GET, POST | Auth Service | 8001 | No | Authentication endpoints |
| `/api/profile/*` | GET, POST, PUT, DELETE | User Profile | 8002 | Yes | User profile management |
| `/api/products/*` | GET | Product Catalog | 8004 | No | Product catalog (public) |
| `/api/cart/*` | GET, POST, PUT, DELETE | Cart Service | 8007 | Yes | Shopping cart operations |
| `/api/orders/*` | GET, POST, PUT | Order Service | 8008 | Yes | Order management |
| `/api/payments/*` | POST | Payment Service | 8009 | Yes | Payment processing |
| `/api/notifications/*` | GET, POST | Notification | 8011 | Yes | Notification management |
| `/gateway/health` | GET | Gateway | N/A | No | Gateway health check |
| `/gateway/ready` | GET | Gateway | N/A | No | Gateway readiness check |
| `/gateway/services` | GET | Gateway | N/A | Admin | Service status |
| `/gateway/routes` | GET | Gateway | N/A | Admin | Route configuration |
| `/gateway/metrics` | GET | Gateway | N/A | Admin | Performance metrics |

### Route Processing Logic

1. **Request Received**: Incoming HTTP request to gateway
2. **Path Analysis**: Extract path and determine target service
3. **Authentication Check**: Validate JWT token if required
4. **Rate Limiting**: Apply rate limits based on user/IP
5. **Circuit Breaker**: Check backend service health
6. **Request Forwarding**: Proxy request to target service
7. **Response Processing**: Return response to client
8. **Logging**: Record request metrics and logs

## Authentication Routing

### Public Routes (No Authentication)
```
GET  /api/auth/health
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/verify (used by services)
GET  /api/products/*
GET  /gateway/health
GET  /gateway/ready
```

### Protected Routes (Authentication Required)
```
POST /api/auth/logout
POST /api/auth/refresh
ALL  /api/profile/*
ALL  /api/cart/*
ALL  /api/orders/*
ALL  /api/payments/*
ALL  /api/notifications/*
```

### Admin Routes (Admin Authentication)
```
GET  /gateway/services
GET  /gateway/routes
GET  /gateway/metrics
```

## Request Flow Examples

### Example 1: Product Catalog Request
```
Client Request:
GET /api/products/123
Host: api.projectzero.com

Gateway Processing:
1. Match route: /api/products/* → Product Service (8004)
2. No authentication required
3. Rate limit check: PASS
4. Circuit breaker: CLOSED (healthy)
5. Forward to: http://product-service:8004/products/123

Backend Response:
200 OK
{"id": "123", "name": "Product Name", ...}

Client Response:
200 OK
{"id": "123", "name": "Product Name", ...}
```

### Example 2: Cart Management Request
```
Client Request:
POST /api/cart/items
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
{"productId": "123", "quantity": 2}

Gateway Processing:
1. Match route: /api/cart/* → Cart Service (8007)
2. Authentication: JWT token validated with Auth Service
3. Rate limit check: PASS (user-specific limit)
4. Circuit breaker: CLOSED (healthy)
5. Add headers: X-User-ID, X-Correlation-ID
6. Forward to: http://cart-service:8007/cart/items

Backend Response:
201 Created
{"cartId": "cart-456", "items": [...], "total": 29.99}

Client Response:
201 Created
{"cartId": "cart-456", "items": [...], "total": 29.99}
```

## Error Handling

### Route Not Found
```
Client Request: GET /api/unknown/endpoint

Gateway Response:
404 Not Found
{
  "error": {
    "code": "ROUTE_NOT_FOUND",
    "message": "The requested endpoint was not found"
  }
}
```

### Service Unavailable
```
Circuit Breaker State: OPEN for Cart Service

Client Request: GET /api/cart

Gateway Response:
503 Service Unavailable
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Cart service is temporarily unavailable"
  }
}
```

---
**Routing Owner**: Platform Engineering Team  
**Next Review**: 2025-12-29