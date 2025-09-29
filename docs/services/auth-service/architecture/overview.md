# Auth Service Architecture Overview

**Service**: Auth Service  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0

## Overview

The Auth Service implements a secure, scalable authentication and authorization system for the Project Zero App ecosystem. Built with FastAPI and following industry best practices, it provides JWT-based authentication, secure password management, and comprehensive token lifecycle management.

## Architecture Principles

### Security First
- Industry-standard password hashing (bcrypt)
- Short-lived access tokens with secure refresh mechanism
- Rate limiting and account protection
- Comprehensive audit logging

### Microservice Design
- Stateless service design for horizontal scaling
- Clean separation of concerns
- RESTful API with OpenAPI documentation
- Health monitoring and observability

### Service Integration
- Token verification endpoint for other services
- Minimal external dependencies
- Graceful failure handling

## System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Auth Service                         │
├─────────────────────────────────────────────────────────┤
│                   API Layer                             │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │ Login/Logout  │  │ Token Mgmt   │  │ User Verify │   │
│  │ Endpoints     │  │ Endpoints    │  │ Endpoints   │   │
│  └───────────────┘  └──────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────┤
│                 Middleware Layer                        │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │ Rate Limiting │  │ Input Valid. │  │ CORS Config │   │
│  └───────────────┘  └──────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────┤
│                 Business Logic                          │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │ Authentication│  │ Token Mgmt   │  │ User Mgmt   │   │
│  │ Service       │  │ Service      │  │ Service     │   │
│  └───────────────┘  └──────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────┤
│                  Data Access Layer                      │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │ User Repository│  │ Token Repo   │  │ Audit Repo  │   │
│  └───────────────┘  └──────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────┤
│                    Data Storage                         │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │ PostgreSQL    │  │ Redis Cache  │  │ File Logs   │   │
│  │ (Production)  │  │ (Planned)    │  │ (Audit)     │   │
│  └───────────────┘  └──────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Architecture

### API Layer Components

**FastAPI Application**
- High-performance ASGI application
- Automatic OpenAPI documentation generation
- Built-in data validation with Pydantic
- Exception handling middleware

**Route Handlers**
- `/auth/login` - User authentication
- `/auth/logout` - Session termination
- `/auth/refresh` - Token renewal
- `/auth/verify` - Token validation
- `/health/*` - Health monitoring

### Business Logic Components

**Authentication Service**
```python
class AuthService:
    def authenticate_user(email, password) -> User
    def create_access_token(user) -> str
    def create_refresh_token(user) -> str
    def verify_token(token) -> TokenPayload
    def revoke_token(token) -> bool
```

**Password Service**
```python
class PasswordService:
    def hash_password(password) -> str
    def verify_password(password, hash) -> bool
    def validate_strength(password) -> bool
```

**Token Service**
```python
class TokenService:
    def generate_token(payload, expiry) -> str
    def decode_token(token) -> dict
    def is_token_expired(token) -> bool
    def blacklist_token(token) -> bool
```

### Data Access Components

**User Repository**
- User CRUD operations
- Email uniqueness validation
- Account status management
- Login attempt tracking

**Token Repository**
- Token storage and retrieval
- Token blacklist management
- Cleanup of expired tokens

**Audit Repository**
- Authentication event logging
- Security event tracking
- Compliance audit trails

## Security Architecture

### Password Security

**Hashing Strategy**
```text
User Password ─→ bcrypt(password, salt, rounds=12) ─→ Stored Hash
```

- **Algorithm**: bcrypt with configurable rounds (default: 12)
- **Salt**: Automatically generated per password
- **Rounds**: Adjustable for performance vs security balance

### JWT Token Architecture

**Access Token Structure**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user123",
    "email": "user@example.com",
    "exp": 1696000000,
    "iat": 1695999100,
    "roles": ["user"]
  },
  "signature": "HMAC-SHA256(header.payload, secret)"
}
```

**Refresh Token Structure**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user123",
    "type": "refresh",
    "exp": 1698591100,
    "iat": 1695999100,
    "jti": "refresh_token_id"
  },
  "signature": "HMAC-SHA256(header.payload, secret)"
}
```

### Security Measures

**Rate Limiting**
- Login attempts: 5 per minute per IP
- Token refresh: 60 per hour per user
- Account lockout: 15 minutes after 5 failed attempts

**Token Security**
- Short-lived access tokens (15 minutes)
- Secure refresh token rotation
- Token blacklist support (planned)
- Cryptographically secure random generation

## Data Model Architecture

### Core Entities

**User Entity**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Token Entity**
```sql
CREATE TABLE tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    token_type VARCHAR(20) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP
);
```

**Audit Log Entity**
```sql
CREATE TABLE auth_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Relationships

```text
User ──┬── Token (1:many)
       └── AuditLog (1:many)
```

## Service Integration Architecture

### Internal Dependencies

**Database Connection**
- SQLAlchemy ORM for database operations
- Connection pooling for performance
- Automatic migration support (planned)

**Configuration Management**
- Environment-based configuration
- Secure secret management
- Runtime configuration validation

### External Dependencies

**Minimal External Dependencies**
- Database (PostgreSQL/SQLite)
- Redis (planned for token blacklist)
- No external authentication providers

**Service Consumers**
```text
Auth Service ←─── Order Service (token verification)
             ←─── Cart Service (token verification)
             ←─── Product Service (admin operations)
             ←─── Payment Service (token verification)
             ←─── User Profile Service (token verification)
             ←─── Notification Service (token verification)
```

## Performance Architecture

### Scalability Design

**Stateless Service**
- No session state stored in service
- JWT tokens contain all necessary information
- Horizontal scaling capability

**Database Optimization**
- Indexed queries for user lookup
- Connection pooling
- Query optimization with SQLAlchemy

**Caching Strategy (Planned)**
```text
Token Verification ─→ Redis Cache ─→ Database Fallback
Rate Limiting Data ─→ Redis Store
User Session Data ─→ Redis Cache
```

### Performance Monitoring

**Key Metrics**
- Authentication request latency
- Token verification response time
- Database query performance
- Error rates by endpoint

**Health Checks**
- Database connectivity
- JWT secret configuration
- Service dependencies
- Memory and CPU usage

## Deployment Architecture

### Development Environment

```yaml
services:
  auth-service:
    build: ./services/auth-service
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=sqlite:///./auth_service.db
      - JWT_SECRET_KEY=dev-secret
    volumes:
      - ./data:/app/data
```

### Production Environment

```yaml
services:
  auth-service:
    image: auth-service:latest
    replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/authdb
      - JWT_SECRET_KEY=${JWT_SECRET}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - database
      - redis
```

## Error Handling Architecture

### Exception Hierarchy

```python
class AuthException(Exception):
    """Base authentication exception"""
    pass

class InvalidCredentialsException(AuthException):
    """Invalid email or password"""
    pass

class TokenExpiredException(AuthException):
    """Access or refresh token expired"""
    pass

class AccountLockedException(AuthException):
    """Account locked due to failed attempts"""
    pass
```

### Error Response Format

```json
{
  "error": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS",
  "timestamp": "2025-09-29T10:00:00Z",
  "request_id": "req_123456"
}
```

## Future Architecture Considerations

### Planned Enhancements

**Multi-Factor Authentication**
- TOTP integration
- SMS verification
- Backup codes

**OAuth/OIDC Integration**
- Social login providers
- Enterprise SSO
- OpenID Connect compliance

**Enhanced Security**
- Device fingerprinting
- Anomaly detection
- Advanced threat protection

**Scalability Improvements**
- Redis token storage
- Distributed rate limiting
- Microservice decomposition

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Architecture Version**: 1.0.0