# Testing Guide - Project Zero App

## Overview

This directory contains comprehensive integration tests for the Project Zero e-commerce application. The tests validate service health, API documentation, gateway routing, and end-to-end workflows.

## Architecture

Project Zero App is a microservices-based e-commerce platform with the following components:

### Backend Services
- **Auth Service** (Port 8001) - User authentication and authorization
- **User Profile Service** (Port 8002) - User profile management
- **Product Catalog Service** (Port 8004) - Product management and search
- **Cart Service** (Port 8007) - Shopping cart operations
- **Order Service** (Port 8008) - Order processing and management
- **Payment Service** (Port 8009) - Payment processing simulation
- **Notification Service** (Port 8011) - Email, SMS, and in-app notifications

### Infrastructure
- **API Gateway** (Port 8000) - Request routing and load balancing
- **Frontend** (Port 3000) - Next.js React application
- **PostgreSQL** (Port 5432) - Primary database
- **Redis** (Port 6379) - Caching and session storage

## Prerequisites

### Required Software
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ with uv (for backend services)
- curl and jq (for API testing)

### Environment Setup

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are healthy:**
   ```bash
   # Check all service health endpoints
   for port in 8001 8002 8004 8007 8008 8009 8011; do
     echo "Testing port $port:"
     curl -s http://localhost:$port/health | jq
   done
   ```

3. **Access frontend:**
   ```bash
   # Open in browser
   open http://localhost:3000
   ```

## Test Suites

### 1. Health Check Tests
**File:** `tests/integration/simple_health_test.sh`

Tests basic service connectivity and health status.

```bash
./tests/integration/simple_health_test.sh
```

**Expected Result:** All 8 services should report healthy status.

### 2. Documentation Tests
**File:** `tests/integration/docs_tests.sh`

Validates Swagger/OpenAPI documentation accessibility.

```bash
./tests/integration/docs_tests.sh
```

**Expected Result:** 5/7 services expose documentation endpoints (71% success rate).

### 3. Gateway Routing Tests
**File:** `tests/integration/gateway_tests.sh`

Tests API Gateway routing to backend services.

```bash
./tests/integration/gateway_tests.sh
```

**Current Status:** Gateway health working, routing configuration needs adjustment.

### 4. Authentication Flow Tests
**File:** `tests/integration/auth_flow_test.sh`

Tests complete authentication workflow.

```bash
./tests/integration/auth_flow_test.sh
```

**Expected Result:** 100% success rate for register, login, verify, and refresh operations.

### 5. E-commerce Flow Tests
**File:** `tests/integration/ecommerce_flow_test.sh`

Tests service-to-service communication and cart operations.

```bash
./tests/integration/ecommerce_flow_test.sh
```

### 6. Order Flow Tests
**File:** `tests/integration/order_flow_tests.sh`

Tests complete end-to-end order workflow.

```bash
./tests/integration/order_flow_tests.sh
```

**Current Status:** 33% success rate - authentication and products working.

## Running All Tests

### Quick Test Suite
```bash
# Run core health and authentication tests
cd tests/integration
./simple_health_test.sh
./auth_flow_test.sh
```

### Complete Test Suite
```bash
# Run all integration tests
for test in tests/integration/*.sh; do
  echo "Running $test..."
  chmod +x "$test"
  "$test"
  echo "---"
done
```

### Test Runner (if available)
```bash
# Comprehensive test execution with reporting
./tests/integration/test-runner.sh
```

## Service Endpoints

### Authentication Service (8001)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/verify` - Token verification
- `GET /health` - Health check
- `GET /docs` - API documentation

### Product Catalog Service (8004)
- `GET /products` - List products
- `GET /products/{id}` - Get product details
- `GET /products/search` - Search products
- `GET /products/category/{category}` - Products by category
- `GET /health` - Health check
- `GET /docs` - API documentation

### Cart Service (8007)
- `GET /cart` - Get cart contents
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{id}` - Update cart item
- `DELETE /cart/items/{id}` - Remove cart item
- `GET /health` - Health check

### Additional Services
See individual service documentation in their respective `/docs` endpoints.

## Common Issues and Troubleshooting

### Service Connection Issues
```bash
# Check if services are running
docker-compose ps

# Check service logs
docker-compose logs <service-name>

# Restart a specific service
docker-compose restart <service-name>
```

### Database Connection Issues
```bash
# Check PostgreSQL connection
docker-compose logs postgres

# Verify database is accepting connections
docker-compose exec postgres psql -U projectzero -d project_zero -c "SELECT 1;"
```

### Authentication Issues
```bash
# Test user registration
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test User"}'

# Test user login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
```

### Frontend Issues
```bash
# Check frontend service
curl -s http://localhost:3000 | head -20

# View frontend logs
docker-compose logs frontend
```

## Test Data

### Sample User Account
- Email: `test-order@example.com`
- Password: `TestPass123!`

### Sample Products
The product catalog service is seeded with 20+ products across categories:
- Electronics
- Clothing  
- Books
- Home & Garden

### Test Scenarios

1. **User Registration and Login**
2. **Product Browsing and Search**
3. **Cart Management (Add/Update/Remove)**
4. **User Profile Management**
5. **Order Creation and Processing**
6. **Service-to-Service Authentication**

## Development Guidelines

### Adding New Tests
1. Create test file in `tests/integration/`
2. Follow naming convention: `*_test.sh` or `*_tests.sh`
3. Make executable: `chmod +x test_file.sh`
4. Include proper error handling and output formatting
5. Update this README with test description

### Test Standards
- Use HTTP status codes for validation
- Include response time measurements where relevant
- Provide clear pass/fail indicators
- Include troubleshooting information in failure messages
- Test both positive and negative scenarios

## Continuous Integration

The test suite is designed to be used in CI/CD pipelines:

```yaml
# Example CI step
- name: Run Integration Tests
  run: |
    docker-compose up -d
    sleep 30  # Wait for services to be ready
    ./tests/integration/simple_health_test.sh
    ./tests/integration/auth_flow_test.sh
```

## Performance Benchmarks

Expected response times for healthy services:
- Health endpoints: < 100ms
- Authentication: < 500ms
- Product queries: < 1000ms
- Cart operations: < 500ms

## Security Considerations

- All API endpoints require proper authentication except health checks
- JWT tokens expire after 15 minutes (access) / 30 days (refresh)
- Passwords must meet complexity requirements
- HTTPS should be used in production environments

## Support and Debugging

For issues with the test suite:
1. Check service logs: `docker-compose logs <service>`
2. Verify environment variables in docker-compose.yml
3. Ensure all services show "healthy" status
4. Check network connectivity between containers
5. Validate test data and credentials

---

**Last Updated:** September 2025  
**Test Suite Version:** 1.0  
**Project:** Project Zero App