# User Profile Service

User profile management service for the Project Zero App e-commerce platform. Handles user profiles, shipping/billing addresses, user preferences, and activity logging with comprehensive authentication and authorization.

## Features

- **Profile Management**: Complete CRUD operations for user profiles
- **Address Management**: Multi-address support with default address selection
- **User Preferences**: Notification settings, language/currency preferences, privacy controls
- **Activity Logging**: Comprehensive audit trail of user actions
- **Authentication**: JWT integration with auth service
- **Admin Support**: Administrative access to user data with proper logging
- **API Documentation**: Interactive Swagger/OpenAPI documentation

## Quick Start

### Local Development

```bash
# Clone the repository and navigate to the service
cd services/user-profile-service

# Install dependencies
uv sync

# Start the development server
uv run uvicorn main:app --reload --port 8002

# Access the API documentation
open http://localhost:8002/docs
```

### Docker Deployment

```bash
# Build the container
docker build -t user-profile-service .

# Run the container
docker run -p 8002:8002 \
  -e JWT_SECRET_KEY="your-secret-key" \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  user-profile-service

# Health check
curl http://localhost:8002/health
```

### Docker Compose

The service is integrated into the main `docker-compose.yml` file:

```bash
# Start all services
docker-compose up -d

# Start only user-profile-service and its dependencies
docker-compose up -d user-profile-service
```

## API Endpoints

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check with dependency verification

### Profile Management
- `GET /profiles` - Get current user's profile
- `POST /profiles` - Create user profile
- `PUT /profiles` - Update user profile
- `DELETE /profiles` - Delete user profile
- `GET /profiles/completion` - Get profile completion status

### Address Management
- `GET /addresses` - Get user's addresses (optional type filter)
- `POST /addresses` - Add new address
- `GET /addresses/{id}` - Get specific address
- `PUT /addresses/{id}` - Update address
- `DELETE /addresses/{id}` - Delete address
- `PUT /addresses/{id}/default` - Set address as default

### Preferences Management
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update user preferences
- `POST /preferences/reset` - Reset preferences to defaults

### Activity Logs
- `GET /activity` - Get user activity history (with pagination)
- `GET /activity/summary` - Get activity summary for specified days
- `GET /activity/types` - Get available activity types

### Admin Endpoints
- `GET /admin/profiles/{user_id}` - Get user profile (admin only)
- `GET /admin/profiles/{user_id}/addresses` - Get user addresses (admin only)
- `GET /admin/profiles/{user_id}/preferences` - Get user preferences (admin only)
- `GET /admin/profiles/{user_id}/activity` - Get user activity (admin only)
- `DELETE /admin/profiles/{user_id}` - Delete user profile (admin only)

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./user_profile_service.db` | No |
| `JWT_SECRET_KEY` | Secret key for JWT verification | Auto-generated | Recommended |
| `AUTH_SERVICE_URL` | Auth service URL for token verification | `http://localhost:8001` | Yes |
| `HOST` | Server bind host | `0.0.0.0` | No |
| `PORT` | Server port | `8002` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

## Database Schema

### UserProfile
- Personal information (name, phone, date of birth, profile picture)
- Links to auth service user via `user_id`
- Audit fields (created_at, updated_at)

### Address
- Complete address information (street, city, state, postal code, country)
- Address type (shipping/billing)
- Default address selection
- Optional label (Home, Work, etc.)

### UserPreferences
- Notification preferences (email marketing, order updates, security alerts, SMS)
- Localization settings (language, currency, timezone)
- Privacy settings (profile visibility, data sharing consent)

### ActivityLog
- Comprehensive audit trail of user actions
- Request context (IP address, user agent, correlation ID)
- Change tracking (old/new values in JSON format)
- Entity references for affected data

## Authentication

The service integrates with the auth service using JWT tokens:

1. **Local Verification**: Decode JWT tokens using shared secret key
2. **Remote Fallback**: Verify tokens with auth service if local verification fails
3. **Admin Access**: Special handling for admin users with enhanced logging

### Required Headers

```http
Authorization: Bearer <jwt_token>
```

### Optional Headers

```http
X-Correlation-ID: <correlation_id>  # For request tracing
```

## Error Handling

The service provides structured error responses:

```json
{
  "error": "Validation failed",
  "message": "Phone number format is invalid",
  "timestamp": "2025-09-27T10:30:00Z",
  "details": {
    "field": "phone",
    "value": "invalid-phone"
  }
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate data, address in use)
- `422` - Unprocessable Entity (validation errors)
- `500` - Internal Server Error

## Validation Rules

### Profile Validation
- Phone numbers: E.164 format
- Names: Alphanumeric characters, spaces, hyphens, apostrophes
- Date of birth: Valid date, not in future, age 13-120
- Profile picture URL: Valid HTTP/HTTPS URL

### Address Validation
- Country: ISO 3166-1 alpha-2 codes
- Postal codes: Format validation by country
- Default addresses: Only one per user per type

### Preferences Validation
- Language: Supported locale codes (e.g., en-US, fr-CA)
- Currency: Supported ISO 4217 codes (e.g., USD, EUR, GBP)
- Timezone: Valid IANA timezone identifiers

## Performance

- **Response Time**: Target <200ms for all profile operations
- **Database**: Optimized queries with proper indexing
- **Caching**: Ready for Redis integration
- **Monitoring**: Structured logging with correlation IDs

## Security

- **Input Validation**: Comprehensive validation and sanitization
- **User Isolation**: Strict user_id filtering in queries
- **Activity Logging**: Full audit trail of user actions
- **No Sensitive Data**: Passwords and tokens excluded from logs
- **Admin Access Control**: Special permissions with audit logging

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test categories
uv run pytest tests/contract/
uv run pytest tests/integration/
uv run pytest tests/unit/
```

### Code Quality

```bash
# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .

# Type checking (if mypy is configured)
uv run mypy src/
```

### Database Management

```bash
# SQLite (development)
# Database file: user_profile_service.db

# PostgreSQL (production)
export DATABASE_URL="postgresql://user:pass@localhost:5432/user_profile_db"
```

## Integration

### With Auth Service
- Token verification for all protected endpoints
- User identification via JWT payload
- Admin privilege checking

### With Order Service
- Provides shipping and billing addresses during checkout
- Address validation before order placement
- User preference data for order processing

### With Frontend
- Complete profile management UI integration
- Address book functionality
- Preference management interface
- Activity history viewing

## Monitoring and Observability

### Health Checks
- `/health` - Basic liveness check
- `/health/ready` - Readiness with dependency checks

### Logging
- Structured JSON logging
- Correlation ID tracking
- Request/response logging
- Performance metrics

### Metrics (Ready for Integration)
- Request count and duration
- Error rates by endpoint
- Database query performance
- Authentication success/failure rates

## Architecture

The service follows a clean architecture pattern:

```
├── src/
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic layer
│   ├── routers/         # FastAPI route handlers
│   ├── auth/            # Authentication utilities
│   ├── middleware/      # Custom middleware components
│   ├── config.py        # Configuration management
│   ├── database.py      # Database session management
│   ├── dependencies.py  # FastAPI dependencies
│   └── app.py           # FastAPI application setup
├── tests/
│   ├── contract/        # API contract tests
│   ├── integration/     # Integration tests
│   └── unit/            # Unit tests
└── main.py              # Application entry point
```

## Contributing

1. Follow the existing code style and patterns
2. Write tests for new functionality
3. Update documentation for API changes
4. Ensure all tests pass before submitting

## License

This project is part of the Project Zero App demonstration platform.