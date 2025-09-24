# Cart Service

Shopping cart microservice for Project Zero App. Provides cart management functionality including adding, updating, removing items, and cart persistence.

## Quick Start

```bash
# Install dependencies
yarn install

# Set up environment
cp .env.example .env

# Initialize database
yarn db:migrate

# Start development server
yarn dev
```

The service will be available at `http://localhost:8007`.

## Features

- **Cart Management**: Add, update, remove, and clear cart items
- **Product Integration**: Validates products with catalog service
- **User Authentication**: JWT-based authentication via auth service
- **Data Persistence**: SQLite (dev) / PostgreSQL (prod) storage
- **Health Monitoring**: Health and readiness endpoints
- **Performance Optimized**: Sub-200ms response times
- **Comprehensive Testing**: Contract, integration, unit, and performance tests

## API Endpoints

### Health Checks
- `GET /health` - Service health status
- `GET /health/ready` - Service readiness check

### Cart Operations (Authentication Required)
- `POST /cart/add` - Add item to cart
- `GET /cart` - Get cart contents
- `PUT /cart/items/:product_id` - Update item quantity
- `DELETE /cart/items/:product_id` - Remove item from cart
- `DELETE /cart` - Clear entire cart

## API Testing with curl

### 1. Health Checks (No Authentication Required)

```bash
# Check service health
curl http://localhost:8007/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-09-23T19:10:51.421Z",
#   "database": "connected"
# }

# Check service readiness
curl http://localhost:8007/health/ready

# Response:
# {
#   "status": "ready",
#   "checks": {
#     "database": true,
#     "auth_service": true,
#     "product_service": true
#   }
# }
```

### 2. Authentication Setup

**Note:** All cart operations require authentication. The cart service validates JWT tokens with the auth service.

#### Option A: With Auth Service Running (Full Integration)

```bash
# First, start the auth service on port 8001
# Then get authentication token
AUTH_TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"SecurePass123"}' \
  | jq -r '.access_token')

# Set up authorization header for subsequent requests
AUTH_HEADER="Authorization: Bearer $AUTH_TOKEN"
```

#### Option B: Development/Testing (Without Auth Service)

If you don't have the auth service running, you'll get authentication errors:

```bash
# This will fail with 401 Unauthorized
curl -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-token" \
  -d '{"product_id": "prod-123", "quantity": 1}'

# Response:
# {
#   "error": "Authentication service unavailable",
#   "timestamp": "2025-09-23T19:33:30.347Z"
# }
```

#### Option C: Using Tests (With Mocks)

To see the cart service working with mock data, run the tests:

```bash
# Run integration tests that use mocks
yarn test tests/integration/test_shopping_flow.js

# Run contract tests
yarn test tests/contract/test_cart_add.js
```

### 3. Quick Testing (Health Checks Only)

These work without any dependencies:

```bash
# Test service health
curl http://localhost:8007/health

# Test readiness (will show false for missing services)
curl http://localhost:8007/health/ready
```

### 4. Cart Operations (Requires Auth & Product Services)

**Prerequisites:** Both auth service (port 8001) and product service (port 8004) must be running.

#### Add Item to Cart
```bash
curl -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "product_id": 2,
    "quantity": 2
  }'

# Response:
# {
#   "cart_id": "550e8400-e29b-41d4-a716-446655440000",
#   "user_id": "user-123",
#   "items": [
#     {
#       "product_id": 2,
#       "quantity": 2,
#       "product": {
#         "id": 2,
#         "name": "Gaming Laptop Ultra",
#         "price": 1299.99,
#         "description": "High-performance gaming laptop with RTX graphics, 16GB RAM, and 1TB SSD. Perfect for gaming, content creation, and professional work."
#       },
#       "subtotal": 2599.98,
#       "added_at": "2025-09-23T19:00:00Z"
#     }
#   ],
#   "totals": {
#     "item_count": 2,
#     "total_price": 2599.98,
#     "currency": "USD"
#   },
#   "created_at": "2025-09-23T19:00:00Z",
#   "updated_at": "2025-09-23T19:00:00Z"
# }
```

#### Get Cart Contents
```bash
curl -H "$AUTH_HEADER" http://localhost:8007/cart

# Response: Same structure as add item response
# If cart is empty, returns 404 with:
# {
#   "message": "Cart is empty",
#   "cart_id": null,
#   "items": [],
#   "totals": {
#     "item_count": 0,
#     "total_price": 0.00,
#     "currency": "USD"
#   }
# }
```

#### Update Item Quantity
```bash
curl -X PUT http://localhost:8007/cart/items/2 \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"quantity": 3}'

# Response: Updated cart with new quantity
```

#### Remove Item from Cart
```bash
curl -X DELETE http://localhost:8007/cart/items/2 \
  -H "$AUTH_HEADER"

# Response: Updated cart without the removed item
```

#### Clear Entire Cart
```bash
curl -X DELETE http://localhost:8007/cart \
  -H "$AUTH_HEADER"

# Response:
# {
#   "message": "Cart cleared successfully",
#   "cart_id": "550e8400-e29b-41d4-a716-446655440000"
# }
```

### 4. Error Responses

The API returns structured error responses:

```bash
# Invalid request (400)
curl -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"quantity": 2}'  # Missing product_id

# Response:
# {
#   "error": "Validation failed",
#   "details": [
#     {
#       "field": "product_id",
#       "message": "Product ID is required"
#     }
#   ],
#   "timestamp": "2025-09-23T19:00:00Z",
#   "correlation_id": "req-123"
# }

# Unauthorized (401)
curl -X GET http://localhost:8007/cart
# Response:
# {
#   "error": "Unauthorized - missing or invalid authorization header",
#   "timestamp": "2025-09-23T19:00:00Z",
#   "correlation_id": "req-124"
# }

# Product not found (404)
curl -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"product_id": 999, "quantity": 1}'

# Quantity limit exceeded (422)
curl -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"product_id": 2, "quantity": 15}'
```

### 5. Complete Shopping Flow Example

```bash
#!/bin/bash
# Complete cart workflow example

# 1. Get authentication token
echo "Getting auth token..."
AUTH_TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

AUTH_HEADER="Authorization: Bearer $AUTH_TOKEN"

# 2. Add first item
echo "Adding laptop to cart..."
curl -s -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"product_id": 2, "quantity": 1}' | jq '.'

# 3. Add second item
echo "Adding headphones to cart..."
curl -s -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"product_id": 3, "quantity": 2}' | jq '.'

# 4. View cart
echo "Current cart contents:"
curl -s -H "$AUTH_HEADER" http://localhost:8007/cart | jq '.'

# 5. Update laptop quantity
echo "Updating laptop quantity to 2..."
curl -s -X PUT http://localhost:8007/cart/items/2 \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"quantity": 2}' | jq '.'

# 6. Remove headphones
echo "Removing headphones from cart..."
curl -s -X DELETE http://localhost:8007/cart/items/3 \
  -H "$AUTH_HEADER" | jq '.'

# 7. Final cart state
echo "Final cart:"
curl -s -H "$AUTH_HEADER" http://localhost:8007/cart | jq '.'

# 8. Clear cart
echo "Clearing cart..."
curl -s -X DELETE http://localhost:8007/cart \
  -H "$AUTH_HEADER" | jq '.'
```

### 6. Testing Without jq

If you don't have `jq` installed, you can use these alternatives:

```bash
# Pretty print JSON with Python
curl -s http://localhost:8007/health | python -m json.tool

# Just view raw response
curl -v http://localhost:8007/health

# Save response to file
curl -s http://localhost:8007/health > health_response.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8007` |
| `DATABASE_URL` | Database connection string | `sqlite:./cart.db` |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` |
| `PRODUCT_SERVICE_URL` | Product service URL | `http://localhost:8004` |
| `LOG_LEVEL` | Logging level | `info` |
| `CART_TTL_HOURS` | Cart expiration time | `24` |
| `MAX_QUANTITY_PER_ITEM` | Max quantity per item | `10` |

## Development

### Running Tests

```bash
# All tests
yarn test

# Contract tests
yarn test:contract

# Integration tests
yarn test:integration

# Unit tests
yarn test tests/unit

# Performance tests
yarn perf-test

# With coverage
yarn test:coverage
```

### Code Quality

```bash
# Linting
yarn lint

# Fix linting issues
yarn lint:fix

# Format code
yarn format
```

### Database

```bash
# Run migrations
yarn db:migrate

# Seed test data
yarn db:seed

# Reset database
yarn db:reset
```

## Architecture

### Technology Stack
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Database**: Sequelize ORM (SQLite/PostgreSQL)
- **Testing**: Jest + Supertest
- **Logging**: Winston
- **Validation**: Express-validator

### Service Dependencies
- **Auth Service** (port 8001): Token validation
- **Product Catalog Service** (port 8004): Product validation and details

### Data Model
- **Cart**: User cart container with metadata
- **CartItem**: Individual items within a cart with quantity
- **Relationships**: One-to-many (Cart → CartItems)

## Docker

### Build Image
```bash
docker build -t cart-service:latest .
```

### Run Container
```bash
docker run -p 8007:8007 \
  -e AUTH_SERVICE_URL=http://auth-service:8001 \
  -e PRODUCT_SERVICE_URL=http://product-service:8004 \
  cart-service:latest
```

### With Docker Compose
```bash
docker-compose up cart-service
```

## Business Rules

### Cart Limits
- Maximum 10 items per product
- Maximum 50 different products per cart
- Cart expires after 24 hours of inactivity

### Validation
- Products must exist in catalog service
- Products must be available for purchase
- User must be authenticated for all operations

### Data Consistency
- Prices are fetched real-time from product service
- Cart timestamps updated on every modification
- Concurrent operations handled safely

## Performance

### Response Time Targets
- Cart operations: < 200ms
- Health checks: < 100ms
- Readiness checks: < 300ms

### Optimization Features
- Efficient database queries with proper indexing
- Product data enrichment with minimal API calls
- Connection pooling for external services

## Monitoring

### Health Endpoints
- `/health`: Basic service and database connectivity
- `/health/ready`: Full dependency health check

### Logging
- Structured JSON logging with Winston
- Request correlation IDs for tracing
- Error logging with stack traces
- Performance metrics logging

### Metrics
- Response times for all operations
- Database query performance
- External service call metrics
- Error rates and types

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check if port 8007 is available
   - Verify database connection
   - Ensure dependencies are installed

2. **Authentication failures**
   - Verify auth service is running
   - Check AUTH_SERVICE_URL configuration
   - Validate JWT token format

3. **Product validation errors**
   - Ensure product service is running
   - Check PRODUCT_SERVICE_URL configuration
   - Verify product IDs exist in catalog

4. **Database errors**
   - Run `yarn db:migrate` to update schema
   - Check DATABASE_URL format
   - Verify file permissions for SQLite

### Debug Mode
```bash
LOG_LEVEL=debug yarn dev
```

## Contributing

1. Follow existing code style and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure all tests pass before submitting
5. Follow commit message conventions

## License

MIT License - see LICENSE file for details.