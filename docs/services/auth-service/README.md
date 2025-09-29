# Auth Service Documentation

**Service Type**: Backend Authentication Service  
**Technology**: FastAPI (Python 3.13+)  
**Port**: 8001  
**Repository Path**: `services/auth-service/`

## Overview

The Auth Service is the central authority for user identity management, credential validation, and JWT token lifecycle management in the Project Zero App ecosystem. It provides secure authentication endpoints, token issuance and verification, and implements enterprise-grade security measures including bcrypt password hashing, rate limiting, and failed login protection.

## Purpose and Responsibilities

### Core Functions
- **User Authentication**: Email/password-based login with secure credential verification
- **Token Management**: JWT access and refresh token issuance, rotation, and revocation
- **Security Enforcement**: bcrypt password hashing (12 rounds), rate limiting, and account lockout
- **Service Integration**: Token verification endpoint for other microservices
- **Health Monitoring**: Comprehensive health checks with database connectivity validation

### In-Scope Features
- Email/password authentication with secure bcrypt hashing
- JWT access token issuance (15-minute lifetime)
- JWT refresh token management (30-day lifetime with rotation)
- Token verification endpoint (`GET /auth/verify`) for microservice authentication
- Rate limiting and failed login lockout mechanisms
- User account creation and basic profile management
- Health and readiness monitoring endpoints

### Out-of-Scope (Future Considerations)
- OAuth/OIDC social login integration
- Multi-factor authentication (MFA/TOTP)
- Password reset workflows with email verification
- Advanced user profile management beyond authentication
- Event publishing for authentication activities

## Architecture Overview

The Auth Service follows a layered architecture pattern with clear separation between API routes, business logic, data access, and security middleware:

```
┌─── FastAPI Application ───┐
│  ├── /auth/* endpoints    │
│  ├── JWT middleware       │
│  ├── Rate limiting        │
│  └── Health checks        │
├─── Business Logic ────────┤
│  ├── Authentication       │
│  ├── Token management     │
│  ├── Password validation  │
│  └── User operations      │
├─── Data Access Layer ─────┤
│  ├── SQLAlchemy ORM       │
│  ├── User models          │
│  ├── Token storage        │
│  └── Database migrations  │
└─── Infrastructure ────────┘
   ├── PostgreSQL/SQLite
   ├── bcrypt hashing
   ├── JWT libraries
   └── Redis (planned)
```

## API Endpoints

### Authentication Endpoints
- `POST /auth/login` - User authentication with email/password
- `POST /auth/logout` - Token invalidation and session cleanup
- `POST /auth/refresh` - Access token refresh using refresh token
- `GET /auth/verify` - Token verification for microservice integration

### Administrative Endpoints
- `GET /health` - Basic liveness check with database connectivity
- `GET /health/ready` - Comprehensive readiness check with dependencies

### Planned Endpoints
- `POST /auth/register` - User self-registration (implementation exists)
- `PUT /auth/password` - Password change functionality
- `DELETE /auth/sessions` - Session management and cleanup

## Technology Stack

### Core Technologies
- **FastAPI**: Modern, fast web framework with automatic OpenAPI documentation
- **Python 3.13+**: Latest Python version with enhanced performance and typing
- **SQLAlchemy**: Object-relational mapping with declarative models
- **Pydantic**: Data validation and serialization with type hints
- **bcrypt**: Industry-standard password hashing with configurable rounds

### Security Libraries
- **python-jose[cryptography]**: JWT token creation and verification
- **passlib[bcrypt]**: Password hashing and verification utilities
- **python-multipart**: Form data handling for authentication requests

### Database Support
- **SQLite**: Development and testing (default configuration)
- **PostgreSQL**: Production database (via DATABASE_URL configuration)
- **Alembic**: Database migration management (future implementation)

### Development Tools
- **uvicorn**: ASGI server for FastAPI applications
- **pytest**: Comprehensive testing framework with fixtures
- **ruff**: Fast Python linter and formatter
- **coverage**: Test coverage reporting and analysis

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required | Notes |
|----------|---------|---------|----------|-------|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./auth_service.db` | No | Use PostgreSQL in production |
| `JWT_SECRET_KEY` | HMAC secret for JWT signing | Auto-generated | Recommended | 256-bit value for production |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | No | Keep consistent across services |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `15` | No | Security vs usability balance |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `30` | No | Supports token rotation |
| `BCRYPT_ROUNDS` | Password hashing cost | `12` | No | Adjust based on performance |
| `HOST` | Service bind address | `0.0.0.0` | No | Container-friendly default |
| `PORT` | Service port number | `8001` | No | Consistent with service mesh |

### Security Configuration
- **Password Requirements**: Minimum 8 characters, complexity validation planned
- **Rate Limiting**: Configurable request limits per IP address and user
- **Token Security**: Short-lived access tokens with secure refresh mechanism
- **Database Security**: Prepared statements, connection pooling, transaction management

## Dependencies and Integration

### External Dependencies
- **Database**: SQLite (development) or PostgreSQL (production)
- **Redis**: Planned for token blacklist and rate limiting data
- **System**: Python 3.13+ runtime environment

### Service Dependencies
- **None**: Auth Service operates independently without upstream dependencies
- **Downstream Consumers**: All other services call `/auth/verify` for token validation

### API Gateway Integration
- Auth endpoints exposed through API Gateway at `/api/auth/*`
- Direct service-to-service token verification bypasses gateway
- Health check endpoints available for service mesh monitoring

## Deployment and Operations

### Local Development
```bash
cd services/auth-service
uv sync
uv run uvicorn main:app --reload --port 8001
```

### Docker Deployment
```bash
docker build -t auth-service:latest services/auth-service
docker run -p 8001:8001 \
  -e JWT_SECRET_KEY="strong-production-secret" \
  -e DATABASE_URL="postgresql://user:pass@db:5432/authdb" \
  auth-service:latest
```

### Health Monitoring
- **Liveness**: `GET /health` - Basic service and database connectivity
- **Readiness**: `GET /health/ready` - Comprehensive dependency validation
- **Metrics**: Planned integration with Prometheus for authentication metrics

## Security Considerations

### Password Security
- bcrypt hashing with 12 rounds (configurable)
- Secure password storage with salt generation
- Password complexity validation (planned)
- Account lockout after failed attempts

### Token Security
- Short-lived access tokens (15 minutes default)
- Secure refresh token rotation
- JWT signature verification
- Token blacklist capability (Redis-based, planned)

### API Security
- Rate limiting on authentication endpoints
- Request validation and sanitization
- HTTPS enforcement (TLS termination at gateway)
- CORS configuration for frontend integration

## Monitoring and Observability

### Logging
- Structured JSON logging for production environments
- Authentication event logging (login, logout, failures)
- Security event tracking and alerting
- Performance metrics and request tracing

### Metrics (Planned)
- Authentication request rates and success ratios
- Token issuance and verification metrics
- Password validation attempt tracking
- Database connection pool monitoring

### Alerting (Planned)
- Failed authentication threshold alerts
- Service health and availability monitoring
- Database connectivity failure alerts
- Token verification error rate tracking

## Related Documentation

### Service Documentation
- [API Documentation](./api-docs/endpoints.md) - Detailed endpoint specifications
- [JWT Documentation](./api-docs/jwt-tokens.md) - Token format and lifecycle
- [Architecture Overview](./architecture/overview.md) - Technical architecture details
- [Security Model](./security/security-model.md) - Comprehensive security design

### Operational Documentation
- [User Management SOPs](./operations/user-management-sops.md) - Administrative procedures
- [Deployment Guide](./deployment/deployment-guide.md) - Production deployment
- [Troubleshooting Guide](./troubleshooting/common-issues.md) - Issue resolution
- [Monitoring Setup](./monitoring/security-monitoring.md) - Observability configuration

### Integration Documentation
- [Token Verification](./integration/token-verification.md) - Service integration guide
- [API Gateway Integration](./integration/gateway-integration.md) - Gateway configuration
- [Disaster Recovery](./disaster-recovery/backup-procedures.md) - Backup and recovery

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Service Version**: 1.0.0  
**Documentation Version**: 1.0.0