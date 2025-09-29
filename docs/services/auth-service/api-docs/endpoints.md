# Auth Service API Documentation

**Service**: Auth Service  
**Base URL**: `http://localhost:8001` (Development)  
**API Gateway Path**: `/api/auth/*`  
**Version**: 1.0.0  
**Last Updated**: 2025-09-29

## Overview

The Auth Service provides comprehensive authentication and authorization capabilities for the Project Zero App ecosystem. It offers JWT-based authentication with secure token management, user credential validation, and service-to-service authentication verification.

## Authentication

All endpoints except health checks and token verification require proper authentication. The service uses JWT tokens for authentication and authorization.

### Token Types

- **Access Token**: Short-lived token (15 minutes) for API access
- **Refresh Token**: Long-lived token (30 days) for access token renewal

### Authentication Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Base URLs

| Environment | Base URL | Notes |
|-------------|----------|-------|
| Development | `http://localhost:8001` | Local development |
| Production | `https://api.projectzero.com/auth` | Production environment |
| API Gateway | `/api/auth/*` | Proxied through gateway |

## Endpoints

### POST /auth/login

Authenticate user with email and password credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "created_at": "2025-09-29T10:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Rate Limiting:**
- 5 requests per minute per IP address
- Account lockout after 5 failed attempts

---

### POST /auth/logout

Invalidate refresh token and end user session.

**Request Headers:**
```http
Authorization: Bearer <refresh_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out",
  "logged_out_at": "2025-09-29T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid refresh token
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Server error

---

### POST /auth/refresh

Exchange refresh token for new access token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "issued_at": "2025-09-29T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Missing refresh token
- `401 Unauthorized`: Invalid or expired refresh token
- `422 Unprocessable Entity`: Malformed token
- `500 Internal Server Error`: Server error

**Token Rotation:**
- New access tokens are issued with each refresh
- Refresh tokens may be rotated for enhanced security

---

### GET /auth/verify

Verify access token validity (used by other services).

**Request Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user_id": "user123",
  "email": "user@example.com",
  "exp": 1696000000,
  "iat": 1695999100,
  "roles": ["user"]
}
```

**Response (401 Unauthorized):**
```json
{
  "valid": false,
  "error": "Token expired",
  "error_code": "TOKEN_EXPIRED"
}
```

**Error Responses:**
- `400 Bad Request`: Missing authorization header
- `401 Unauthorized`: Invalid or expired token
- `422 Unprocessable Entity`: Malformed token
- `500 Internal Server Error`: Server error

**Service Integration:**
This endpoint is primarily used by other microservices to validate user tokens.

---

### POST /auth/register *(Planned)*

Register new user account.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securePassword123",
  "confirm_password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "user456",
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2025-09-29T10:45:00Z"
  },
  "message": "User created successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request format
- `409 Conflict`: Email already exists
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

---

### GET /health

Basic service health check.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-29T10:00:00Z",
  "service": "auth-service",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "response_time_ms": 5
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-29T10:00:00Z",
  "service": "auth-service",
  "version": "1.0.0",
  "database": {
    "status": "disconnected",
    "error": "Connection timeout"
  }
}
```

---

### GET /health/ready

Comprehensive readiness check with dependencies.

**Response (200 OK):**
```json
{
  "status": "ready",
  "timestamp": "2025-09-29T10:00:00Z",
  "service": "auth-service",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5
    },
    "jwt_secret": {
      "status": "configured"
    },
    "bcrypt": {
      "status": "available"
    }
  }
}
```

## Data Models

### User Model

```json
{
  "id": "string",
  "email": "string",
  "password_hash": "string",
  "first_name": "string",
  "last_name": "string",
  "is_active": "boolean",
  "is_admin": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime"
}
```

### Token Model

```json
{
  "id": "string",
  "user_id": "string",
  "token_type": "string",
  "token_hash": "string",
  "expires_at": "datetime",
  "created_at": "datetime",
  "revoked_at": "datetime"
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | Email or password incorrect | 401 |
| `TOKEN_EXPIRED` | Access or refresh token expired | 401 |
| `TOKEN_INVALID` | Malformed or tampered token | 401 |
| `ACCOUNT_LOCKED` | Account locked due to failed attempts | 423 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `EMAIL_EXISTS` | Email already registered | 409 |
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `INTERNAL_ERROR` | Server error | 500 |

## Rate Limiting

### Login Endpoint
- **Limit**: 5 requests per minute per IP
- **Burst**: 10 requests per minute
- **Lockout**: Account locked after 5 failed attempts for 15 minutes

### Token Refresh
- **Limit**: 60 requests per hour per user
- **Burst**: 10 requests per minute

### General Endpoints
- **Limit**: 100 requests per minute per IP
- **Burst**: 200 requests per minute

## Security Considerations

### Password Security
- **Hashing**: bcrypt with 12 rounds (configurable)
- **Requirements**: Minimum 8 characters (configurable)
- **Validation**: Server-side validation and sanitization

### Token Security
- **Algorithm**: HMAC SHA-256 (HS256)
- **Secret**: Strong 256-bit secret key
- **Expiration**: Short-lived access tokens (15 minutes)
- **Refresh**: Secure refresh token rotation

### Network Security
- **HTTPS**: All communications over TLS 1.3
- **CORS**: Configured for frontend origins
- **Headers**: Security headers (HSTS, CSP, etc.)

## SDK and Client Examples

### cURL Examples

**Login:**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

**Token Verification:**
```bash
curl -X GET http://localhost:8001/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const authClient = {
  baseURL: 'http://localhost:8001',
  
  async login(email, password) {
    const response = await axios.post(`${this.baseURL}/auth/login`, {
      email,
      password
    });
    return response.data;
  },
  
  async verifyToken(token) {
    const response = await axios.get(`${this.baseURL}/auth/verify`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  }
};
```

### Python Example

```python
import requests

class AuthClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
    
    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        return response.json()
    
    def verify_token(self, token):
        response = requests.get(
            f"{self.base_url}/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## Testing

### Test Accounts

| Email | Password | Role | Notes |
|-------|----------|------|-------|
| `admin@projectzero.com` | `AdminPass123!` | Admin | Full administrative access |
| `user@projectzero.com` | `UserPass123!` | User | Standard user account |
| `test@projectzero.com` | `TestPass123!` | User | Test user for development |

### Health Check

```bash
curl http://localhost:8001/health
curl http://localhost:8001/health/ready
```

## Related Documentation

- [JWT Token Documentation](./jwt-tokens.md) - Token format and lifecycle
- [Service Architecture](../architecture/overview.md) - Auth service architecture
- [Security Model](../security/security-model.md) - Security implementation
- [Integration Guide](../integration/token-verification.md) - Service integration

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**API Version**: 1.0.0