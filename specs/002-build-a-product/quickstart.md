# Quickstart Guide: Product Catalog Service

**Date**: 2025-09-23
**Service**: Product Catalog Service
**Port**: 8004

## Overview

This quickstart guide walks you through setting up, running, and testing the Product Catalog Service. The service provides REST API endpoints for managing and browsing products in an e-commerce catalog.

## Prerequisites

- Python 3.13+
- `uv` package manager installed
- Auth Service running on port 8001 (for admin operations testing)
- Optional: Docker for containerized setup

## Quick Setup

### 1. Navigate to Service Directory
```bash
cd services/product-catalog-service
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Run the Service
```bash
uv run uvicorn main:app --reload --port 8004
```

The service will start on http://localhost:8004

### 4. Verify Installation
```bash
curl http://localhost:8004/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-23T10:30:00Z"
}
```

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8004/docs
- **ReDoc Documentation**: http://localhost:8004/redoc
- **OpenAPI Schema**: http://localhost:8004/openapi.json

## Testing the API

### Public Endpoints (No Authentication)

#### 1. List All Products
```bash
curl "http://localhost:8004/products?limit=5&offset=0"
```

Expected response structure:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Smartphone Pro Max",
      "description": "Latest smartphone with advanced features",
      "price": 999.99,
      "category": "electronics",
      "image_url": "https://example.com/smartphone.jpg",
      "stock_quantity": 50,
      "is_active": true,
      "created_at": "2025-09-23T10:00:00Z",
      "updated_at": "2025-09-23T10:00:00Z"
    }
  ],
  "total": 25,
  "offset": 0,
  "limit": 5,
  "has_more": true
}
```

#### 2. Get Product by ID
```bash
curl http://localhost:8004/products/1
```

#### 3. Filter by Category
```bash
curl "http://localhost:8004/products/category/electronics?limit=3"
```

#### 4. Search Products
```bash
curl "http://localhost:8004/products/search?q=smartphone&limit=3"
```

### Admin Endpoints (Authentication Required)

First, obtain a JWT token from the Auth Service:

#### 1. Get Authentication Token
```bash
# Login to auth service (assumes user exists)
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}')

# Extract token
TOKEN=$(echo $AUTH_RESPONSE | jq -r '.access_token')
```

#### 2. Create New Product
```bash
curl -X POST http://localhost:8004/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "A product created via API",
    "price": 29.99,
    "category": "electronics",
    "image_url": "https://example.com/test.jpg",
    "stock_quantity": 10
  }'
```

#### 3. Update Product
```bash
curl -X PUT http://localhost:8004/products/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product Name",
    "price": 39.99
  }'
```

## Sample Data

The service comes with 20+ pre-loaded sample products across 4 categories:

### Electronics (6 products)
- Smartphone Pro Max ($999.99)
- Gaming Laptop ($1299.99)
- Wireless Headphones ($199.99)
- Tablet Pro ($599.99)
- Smartwatch ($299.99)
- Digital Camera ($799.99)

### Clothing (6 products)
- Premium Cotton T-Shirt ($29.99)
- Designer Jeans ($89.99)
- Running Sneakers ($149.99)
- Winter Jacket ($199.99)
- Summer Dress ($79.99)
- Casual Hoodie ($59.99)

### Books (4 products)
- Python Programming Guide ($49.99)
- Science Fiction Novel ($14.99)
- Physics Textbook ($129.99)
- Cooking Masterclass ($34.99)

### Home Goods (4 products)
- Modern Coffee Table ($299.99)
- LED Desk Lamp ($79.99)
- Kitchen Utensil Set ($149.99)
- Premium Bedding Set ($199.99)

## Testing Scenarios

### Scenario 1: Customer Browsing Experience
```bash
# 1. Browse all products with pagination
curl "http://localhost:8004/products?limit=10"

# 2. Filter by electronics category
curl "http://localhost:8004/products/category/electronics"

# 3. Search for laptops
curl "http://localhost:8004/products/search?q=laptop"

# 4. View specific product details
curl "http://localhost:8004/products/2"
```

### Scenario 2: Admin Product Management
```bash
# 1. Authenticate (get token as shown above)

# 2. Create new product
curl -X POST http://localhost:8004/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Gadget",
    "description": "Latest tech gadget",
    "price": 199.99,
    "category": "electronics",
    "image_url": "https://example.com/gadget.jpg",
    "stock_quantity": 25
  }'

# 3. Update product price and stock
curl -X PUT http://localhost:8004/products/21 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 179.99,
    "stock_quantity": 30
  }'

# 4. Deactivate product
curl -X PUT http://localhost:8004/products/21 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

### Scenario 3: Error Handling
```bash
# 1. Invalid product ID
curl http://localhost:8004/products/999
# Expected: 404 Not Found

# 2. Invalid category
curl http://localhost:8004/products/category/invalid
# Expected: 400 Bad Request

# 3. Unauthorized admin operation
curl -X POST http://localhost:8004/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Test","price":10.00,"category":"electronics","image_url":"http://test.com","stock_quantity":5}'
# Expected: 401 Unauthorized

# 4. Invalid product data
curl -X POST http://localhost:8004/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"","price":-10}'
# Expected: 422 Validation Error
```

## Database

### Development Database
- **Type**: SQLite
- **Location**: `./product_catalog.db`
- **Auto-created**: Yes, with sample data

### Production Database
Set `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/product_catalog"
uv run uvicorn main:app --port 8004
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./product_catalog.db` | Database connection string |
| `AUTH_SERVICE_URL` | `http://localhost:8001` | Auth service endpoint |
| `PORT` | `8004` | Service port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Docker Setup

### Build and Run
```bash
# Build image
docker build -t product-catalog-service .

# Run container
docker run -p 8004:8004 \
  -e AUTH_SERVICE_URL=http://host.docker.internal:8001 \
  product-catalog-service
```

### With Database
```bash
# Run with PostgreSQL
docker network create project-zero-net || true

docker run -d --name product-db --network project-zero-net \
  -e POSTGRES_DB=product_catalog \
  -e POSTGRES_USER=catalog_user \
  -e POSTGRES_PASSWORD=catalog_pass \
  postgres:15

docker run -p 8004:8004 --network project-zero-net \
  -e DATABASE_URL=postgresql://catalog_user:catalog_pass@product-db:5432/product_catalog \
  -e AUTH_SERVICE_URL=http://host.docker.internal:8001 \
  product-catalog-service
```

## Testing

### Run All Tests
```bash
uv run pytest
```

### Test Categories
```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Contract tests only
uv run pytest tests/contract/

# With coverage
uv run pytest --cov=src --cov-report=term-missing
```

### Test Health Endpoints
```bash
curl http://localhost:8004/health
curl http://localhost:8004/health/ready
```

## Troubleshooting

### Common Issues

1. **Port 8004 already in use**
   ```bash
   # Use different port
   uv run uvicorn main:app --reload --port 8005
   ```

2. **Database connection error**
   ```bash
   # Check DATABASE_URL format
   echo $DATABASE_URL
   ```

3. **Auth service not reachable**
   ```bash
   # Test auth service connectivity
   curl http://localhost:8001/health
   ```

4. **Import errors**
   ```bash
   # Reinstall dependencies
   uv sync --refresh
   ```

### Log Files
- Service logs: Console output with structured JSON
- Database logs: Included in service logs
- Access logs: HTTP request/response logging

## Next Steps

1. **Frontend Integration**: Use the API endpoints in a React/Next.js frontend
2. **Performance Testing**: Load test with realistic product catalogs
3. **Production Deployment**: Deploy with PostgreSQL and proper monitoring
4. **Advanced Features**: Add full-text search, product ratings, inventory tracking

## API Reference

For complete API documentation, visit http://localhost:8004/docs when the service is running.

Key endpoints summary:
- `GET /products` - List products with pagination
- `GET /products/{id}` - Get product details
- `GET /products/category/{category}` - Filter by category
- `GET /products/search?q={query}` - Search products
- `POST /products` - Create product (admin)
- `PUT /products/{id}` - Update product (admin)
- `GET /health` - Health check
- `GET /health/ready` - Readiness check