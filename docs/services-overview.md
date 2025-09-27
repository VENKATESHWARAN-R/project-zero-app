# Project Zero App - Services Overview

## Backend Services Summary

| Service | Port | Status | Technology | Purpose |
|---------|------|--------|------------|---------|
| **Auth Service** | 8001 | ✅ Active | FastAPI + SQLite | User authentication & JWT management |
| **Product Service** | 8004 | ✅ Active | FastAPI + SQLite | Product catalog & inventory |
| **Cart Service** | 8007 | ✅ Active | Node.js + SQLite | Shopping cart management |
| **Order Service** | 8008 | ✅ Active | FastAPI + SQLite | Order processing & management |
| **Payment Service** | 8009 | ✅ Active | FastAPI + SQLite | Payment processing (mock) |

## Quick Health Check

```bash
# Check all services
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8004/health  # Product Service  
curl http://localhost:8007/health  # Cart Service
curl http://localhost:8008/health  # Order Service
curl http://localhost:8009/health  # Payment Service
```

## API Documentation Links

- **Auth Service**: http://localhost:8001/docs
- **Product Service**: http://localhost:8004/docs  
- **Cart Service**: http://localhost:8007/docs (if available)
- **Order Service**: http://localhost:8008/docs
- **Payment Service**: http://localhost:8009/docs

## Swagger Files

Each service has a `swagger.json` file in its directory containing the complete OpenAPI specification:

- `services/auth-service/swagger.json`
- `services/product-catalog-service/swagger.json`
- `services/cart-service/swagger.json`
- `services/order-service/swagger.json`
- `services/payment-service/swagger.json`

## Docker Integration

All services are fully integrated with Docker Compose:

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d auth-service order-service payment-service

# View service logs
docker-compose logs <service-name>

# Check running containers
docker ps
```

## Service Integration

Services communicate via HTTP APIs with JWT authentication:

```
Frontend (3000) → Auth Service (8001) → JWT Tokens
                ↓
Product Service (8004) ← JWT validation
                ↓
Cart Service (8007) ← JWT validation  
                ↓
Order Service (8008) ← JWT validation
                ↓
Payment Service (8009) ← JWT validation
```

## Testing the Complete Flow

```bash
# 1. Register user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!", "full_name": "Test User"}'

# 2. Login to get JWT
JWT_TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}' | jq -r '.access_token')

# 3. Browse products
curl http://localhost:8004/api/v1/products

# 4. Add to cart
curl -X POST http://localhost:8007/api/v1/cart/items \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "product-uuid", "quantity": 2}'

# 5. Create order
curl -X POST http://localhost:8008/orders/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": "product-uuid", "quantity": 2, "price": 2999}]}'

# 6. Process payment
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": "order-uuid", "payment_method_id": "method-uuid", "amount": 5998}'
```

For detailed API documentation, see [api-documentation.md](./api-documentation.md).
