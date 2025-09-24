# Authentication API Contract

**Base URL**: `http://localhost:8001`
**Service**: Auth Service
**Version**: v1

## Endpoints

### POST /auth/login
Authenticate user with email and password.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "user-uuid-123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2025-09-24T10:00:00Z",
    "updated_at": "2025-09-24T10:00:00Z"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limiting

### POST /auth/register
Register a new user account.

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response (201 Created)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "user-uuid-456",
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "created_at": "2025-09-24T10:00:00Z",
    "updated_at": "2025-09-24T10:00:00Z"
  }
}
```

**Error Responses**:
- `409 Conflict`: Email already exists
- `422 Unprocessable Entity`: Validation errors

### POST /auth/refresh
Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

### POST /auth/logout
Logout user and invalidate refresh token.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

### GET /auth/verify
Verify access token validity (used by other services).

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "user": {
    "id": "user-uuid-123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "valid": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token

## Error Response Format
All error responses follow this format:

```json
{
  "detail": "Error message description",
  "code": "ERROR_CODE",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

## Rate Limiting
- Login attempts: 5 per minute per IP
- Registration: 3 per hour per IP
- Token refresh: 10 per minute per user

## Security Headers
All responses include:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`