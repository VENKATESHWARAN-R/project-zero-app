# Quickstart: User Profile Management Service

**Service**: User Profile Service | **Port**: 8002 | **Status**: Implementation Ready
**Prerequisites**: Auth service running on port 8001

## Quick Validation Test Scenarios

### 1. Service Health Verification
```bash
# Start the service
cd services/user-profile-service
uv run uvicorn main:app --reload --port 8002

# Test health endpoints
curl http://localhost:8002/health
curl http://localhost:8002/health/ready

# Expected Response:
# {"status": "healthy", "service": "user-profile-service", "version": "1.0.0", ...}
```

### 2. Profile Creation Flow
```bash
# Step 1: Get JWT token from auth service
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  | jq -r '.access_token')

# Step 2: Create user profile
curl -X POST http://localhost:8002/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-123-4567",
    "date_of_birth": "1990-05-15"
  }'

# Expected Response:
# {"id": 1, "user_id": 42, "first_name": "John", "last_name": "Doe", ...}
```

### 3. Address Management Flow
```bash
# Add shipping address
curl -X POST http://localhost:8002/addresses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address_type": "shipping",
    "street_address": "123 Main St",
    "city": "San Francisco",
    "state_province": "CA",
    "postal_code": "94105",
    "country": "US",
    "label": "Home",
    "is_default": true
  }'

# Get all addresses
curl -X GET http://localhost:8002/addresses \
  -H "Authorization: Bearer $TOKEN"

# Set different address as default
curl -X PUT http://localhost:8002/addresses/1/default \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Preferences Management
```bash
# Update notification preferences
curl -X PUT http://localhost:8002/preferences \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_marketing": false,
    "email_order_updates": true,
    "sms_notifications": true,
    "preferred_language": "en-US",
    "preferred_currency": "USD"
  }'

# Get current preferences
curl -X GET http://localhost:8002/preferences \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Activity History Verification
```bash
# View recent activity
curl -X GET "http://localhost:8002/activity?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Filter by activity type
curl -X GET "http://localhost:8002/activity?activity_type=profile_updated" \
  -H "Authorization: Bearer $TOKEN"
```

## Integration Test Scenarios

### Auth Service Integration
```bash
# Test with expired token (should fail)
curl -X GET http://localhost:8002/profiles \
  -H "Authorization: Bearer expired_token"
# Expected: 401 Unauthorized

# Test without token (should fail)
curl -X GET http://localhost:8002/profiles
# Expected: 401 Unauthorized
```

### Order Service Integration
```bash
# Simulate order service requesting address data
curl -X GET "http://localhost:8002/addresses?type=shipping" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Service-Name: order-service"
# Expected: List of shipping addresses for checkout
```

### Admin Access Testing
```bash
# Test admin access to other user's profile
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}' \
  | jq -r '.access_token')

curl -X GET http://localhost:8002/admin/profiles/42 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
# Expected: User profile data (admin access)
```

## Error Handling Validation

### Validation Errors
```bash
# Invalid phone number format
curl -X POST http://localhost:8002/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "invalid-phone"}'
# Expected: 422 Validation Error

# Invalid country code
curl -X POST http://localhost:8002/addresses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address_type": "shipping",
    "street_address": "123 Main St",
    "city": "San Francisco",
    "postal_code": "94105",
    "country": "INVALID"
  }'
# Expected: 422 Validation Error
```

### Business Logic Errors
```bash
# Try to delete address used in active order
curl -X DELETE http://localhost:8002/addresses/1 \
  -H "Authorization: Bearer $TOKEN"
# Expected: 409 Conflict (if address is in use)

# Try to access non-existent profile
curl -X GET http://localhost:8002/admin/profiles/99999 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
# Expected: 404 Not Found
```

## Performance Validation

### Response Time Testing
```bash
# Test profile retrieval performance
time curl -X GET http://localhost:8002/profiles \
  -H "Authorization: Bearer $TOKEN"
# Expected: Response time < 200ms

# Test address listing performance
time curl -X GET http://localhost:8002/addresses \
  -H "Authorization: Bearer $TOKEN"
# Expected: Response time < 200ms
```

### Concurrent Request Testing
```bash
# Simulate multiple concurrent profile updates
for i in {1..10}; do
  curl -X PUT http://localhost:8002/profiles \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"John$i\"}" &
done
wait
# Expected: All requests succeed without conflicts
```

## Docker Integration Testing

### Container Health Check
```bash
# Build and run container
docker build -t user-profile-service .
docker run -p 8002:8002 -e AUTH_SERVICE_URL=http://host.docker.internal:8001 user-profile-service

# Test health check endpoint
curl http://localhost:8002/health
# Expected: Healthy response from containerized service
```

### Docker Compose Integration
```bash
# Start all services via docker-compose
docker-compose up -d

# Test service connectivity
curl http://localhost:8002/health
# Expected: All services healthy and connected
```

## Development Workflow Validation

### Code Quality Checks
```bash
# Run linting
uv run ruff check .
# Expected: No linting errors

# Run formatting
uv run ruff format .
# Expected: Code properly formatted

# Run type checking
uv run mypy src/
# Expected: No type errors
```

### Test Suite Execution
```bash
# Run all tests
uv run pytest
# Expected: All tests pass

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
# Expected: 80%+ test coverage

# Run specific test categories
uv run pytest tests/contract/
uv run pytest tests/integration/
uv run pytest tests/unit/
# Expected: All test categories pass
```

## API Documentation Validation

### OpenAPI Documentation
```bash
# Access interactive API docs
open http://localhost:8002/docs

# Access ReDoc documentation
open http://localhost:8002/redoc

# Validate OpenAPI spec
curl http://localhost:8002/openapi.json | jq '.'
# Expected: Valid OpenAPI 3.0.3 specification
```

### Contract Validation
```bash
# Run contract tests against live API
uv run pytest tests/contract/ --api-url=http://localhost:8002
# Expected: All API contracts validated successfully
```

## Monitoring and Observability

### Log Validation
```bash
# Check structured logging output
tail -f logs/user-profile-service.log | jq '.'
# Expected: Structured JSON logs with correlation IDs

# Test correlation ID propagation
curl -X GET http://localhost:8002/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Correlation-ID: test-123"
# Expected: Correlation ID in response headers and logs
```

### Metrics Collection
```bash
# Test metrics endpoint (if enabled)
curl http://localhost:8002/metrics
# Expected: Prometheus-compatible metrics

# Monitor request performance
curl -w "Response time: %{time_total}s\n" \
  -X GET http://localhost:8002/profiles \
  -H "Authorization: Bearer $TOKEN"
# Expected: Performance metrics logged
```

## Cleanup and Reset

### Test Data Cleanup
```bash
# Reset test database
rm -f user_profile_service.db
uv run python -c "from src.database import init_db; init_db()"
# Expected: Fresh database for testing
```

### Service Shutdown
```bash
# Graceful shutdown
curl -X POST http://localhost:8002/admin/shutdown \
  -H "Authorization: Bearer $ADMIN_TOKEN"
# Expected: Service shuts down gracefully

# Force shutdown via signal
pkill -f "uvicorn main:app"
# Expected: Service stops immediately
```

## Success Criteria

✅ **Health Checks**: All health endpoints return healthy status
✅ **Authentication**: JWT token validation working correctly
✅ **CRUD Operations**: All profile/address/preference operations functional
✅ **Validation**: Input validation prevents invalid data
✅ **Error Handling**: Appropriate HTTP status codes and error messages
✅ **Activity Logging**: All user actions logged appropriately
✅ **Admin Access**: Administrative endpoints accessible with proper permissions
✅ **Service Integration**: Auth service integration working correctly
✅ **Performance**: Response times under 200ms for normal operations
✅ **Docker**: Container builds and runs successfully
✅ **Documentation**: API documentation accessible and accurate
✅ **Testing**: All test suites pass with adequate coverage

## Next Steps

1. **Implementation**: Follow tasks.md for development execution
2. **Integration**: Add to docker-compose.yml for multi-service testing
3. **Documentation**: Update project README with service information
4. **Monitoring**: Configure observability stack integration
5. **Security**: Conduct security review and vulnerability assessment