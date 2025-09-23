# Quickstart: Shopping Cart Service

**Date**: 2025-09-23
**Service**: Cart Service (Node.js/Express)
**Port**: 8007

## Prerequisites

- Node.js 18+ installed
- Yarn package manager installed
- Auth service running on port 8001
- Product catalog service running on port 8002

## Quick Setup

```bash
# Navigate to cart service directory
cd services/cart-service

# Install dependencies
yarn install

# Set up environment
cp .env.example .env

# Initialize database
yarn run db:migrate

# Start development server
yarn dev
```

## Environment Configuration

### Required Environment Variables
```bash
# .env file
PORT=8007
DATABASE_URL=sqlite:./cart.db
AUTH_SERVICE_URL=http://localhost:8001
PRODUCT_SERVICE_URL=http://localhost:8002
LOG_LEVEL=info
CART_TTL_HOURS=24
MAX_QUANTITY_PER_ITEM=10
```

### Optional Environment Variables
```bash
JWT_SECRET=your-jwt-secret  # For local JWT validation (optional)
CORS_ORIGIN=*              # CORS configuration
REQUEST_TIMEOUT=5000       # Service request timeout (ms)
```

## Service Dependencies

### 1. Auth Service (Required)
- **URL**: http://localhost:8001
- **Endpoints Used**:
  - `GET /auth/verify` - Token validation
- **Required**: Service must be running for authentication

### 2. Product Catalog Service (Required)
- **URL**: http://localhost:8002
- **Endpoints Used**:
  - `GET /products/{id}` - Product details
  - `GET /products/validate` - Bulk product validation
- **Required**: Service must be running for product operations

## API Usage Examples

### 1. Health Check
```bash
curl http://localhost:8007/health

# Expected Response:
{
  "status": "healthy",
  "timestamp": "2025-09-23T10:00:00Z",
  "database": "connected"
}
```

### 2. Authentication Setup
```bash
# First, get a token from auth service
AUTH_TOKEN=$(curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Use token in cart requests
export AUTH_HEADER="Authorization: Bearer $AUTH_TOKEN"
```

### 3. Add Item to Cart
```bash
curl -X POST http://localhost:8007/cart/add \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "product_id": "prod-123",
    "quantity": 2
  }'

# Expected Response:
{
  "cart_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-456",
  "items": [
    {
      "product_id": "prod-123",
      "quantity": 2,
      "product": {
        "id": "prod-123",
        "name": "Sample Product",
        "price": 29.99,
        "description": "A great product"
      },
      "subtotal": 59.98,
      "added_at": "2025-09-23T10:00:00Z"
    }
  ],
  "totals": {
    "item_count": 2,
    "total_price": 59.98,
    "currency": "USD"
  }
}
```

### 4. Get Cart Contents
```bash
curl http://localhost:8007/cart \
  -H "$AUTH_HEADER"

# Returns same structure as add item response
```

### 5. Update Item Quantity
```bash
curl -X PUT http://localhost:8007/cart/items/prod-123 \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{"quantity": 3}'
```

### 6. Remove Item from Cart
```bash
curl -X DELETE http://localhost:8007/cart/items/prod-123 \
  -H "$AUTH_HEADER"
```

### 7. Clear Entire Cart
```bash
curl -X DELETE http://localhost:8007/cart \
  -H "$AUTH_HEADER"

# Expected Response:
{
  "message": "Cart cleared successfully",
  "cart_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing the Service

### Unit Tests
```bash
# Run all tests
yarn test

# Run with coverage
yarn test:coverage

# Run specific test file
yarn test src/routes/cart.test.js
```

### Integration Tests
```bash
# Run integration tests (requires running services)
yarn test:integration

# Test specific user story
yarn test tests/integration/cart-workflow.test.js
```

### API Contract Tests
```bash
# Validate API against OpenAPI spec
yarn test:contract

# Test all endpoints
yarn test:api
```

## Common Workflows

### Complete Shopping Flow
```bash
# 1. Authenticate user
TOKEN=$(curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Add multiple items
curl -X POST http://localhost:8007/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod-123", "quantity": 2}'

curl -X POST http://localhost:8007/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod-456", "quantity": 1}'

# 3. View cart
curl http://localhost:8007/cart \
  -H "Authorization: Bearer $TOKEN"

# 4. Update quantity
curl -X PUT http://localhost:8007/cart/items/prod-123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 3}'

# 5. Remove one item
curl -X DELETE http://localhost:8007/cart/items/prod-456 \
  -H "Authorization: Bearer $TOKEN"

# 6. Final cart check
curl http://localhost:8007/cart \
  -H "Authorization: Bearer $TOKEN"
```

## Development Commands

```bash
# Start development server with hot reload
yarn dev

# Run linting
yarn lint

# Fix linting issues
yarn lint:fix

# Run type checking (if using TypeScript)
yarn type-check

# Database operations
yarn db:migrate       # Run migrations
yarn db:seed          # Seed test data
yarn db:reset         # Reset database

# Build for production
yarn build

# Start production server
yarn start
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check if port 8007 is available
   - Verify auth and product services are running
   - Check environment variables

2. **Authentication errors**
   - Verify auth service is accessible
   - Check token format and expiration
   - Validate AUTH_SERVICE_URL

3. **Product validation fails**
   - Ensure product service is running
   - Check PRODUCT_SERVICE_URL
   - Verify product IDs exist in catalog

4. **Database errors**
   - Run `yarn db:migrate` to update schema
   - Check DATABASE_URL format
   - Verify file permissions for SQLite

### Debug Logging
```bash
# Enable debug logging
LOG_LEVEL=debug yarn dev

# View logs in structured format
yarn logs | jq '.'

# Filter logs by level
yarn logs | jq 'select(.level == "error")'
```

## Performance Testing

### Load Testing
```bash
# Install artillery
npm install -g artillery

# Run basic load test
artillery run tests/load/cart-load-test.yml

# Custom load test
artillery quick --count 10 --num 5 http://localhost:8007/health
```

### Memory and Performance
```bash
# Monitor memory usage
yarn run profile

# Generate performance report
yarn run perf-test
```

This quickstart guide provides everything needed to get the cart service running and test its functionality with the existing auth and product catalog services.