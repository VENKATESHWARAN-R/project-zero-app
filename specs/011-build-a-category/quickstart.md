# Quickstart: Category Management Service

**Feature**: Category Management Service
**Date**: 2025-09-29
**Phase**: 1 - Quickstart Guide

This quickstart guide provides step-by-step instructions to validate the category management service implementation against the functional requirements from the feature specification.

## Prerequisites

- Node.js 18+ installed
- Yarn package manager
- Docker and Docker Compose
- Auth Service running on port 8001
- Product Catalog Service running on port 8004

## Quick Setup

### 1. Service Setup

```bash
# Navigate to the service directory
cd services/category-service

# Install dependencies
yarn install

# Set up environment variables
cp .env.example .env

# Start the service in development mode
yarn dev

# Verify service is running
curl http://localhost:8005/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-29T10:00:00Z",
  "version": "1.0.0",
  "uptime": 30.5
}
```

### 2. Database Initialization

```bash
# Run database migrations
yarn db:migrate

# (Optional) Seed sample categories
yarn db:seed

# Verify database connection
curl http://localhost:8005/health/ready
```

**Expected Response**:
```json
{
  "status": "ready",
  "timestamp": "2025-09-29T10:00:00Z",
  "dependencies": {
    "database": {
      "status": "connected",
      "response_time": 5.2
    },
    "auth_service": {
      "status": "available",
      "response_time": 12.5
    }
  }
}
```

## Functional Requirement Validation

### FR-001: Create Categories (Admin Only)

**Test**: Create a new root category

```bash
# First, get admin JWT token from auth service
export ADMIN_TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | \
  jq -r '.access_token')

# Create root category
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "image_url": "https://example.com/electronics.jpg"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "description": "Electronic devices and accessories",
  "image_url": "https://example.com/electronics.jpg",
  "parent_id": null,
  "sort_order": 0,
  "is_active": true,
  "metadata": null,
  "created_at": "2025-09-29T10:00:00Z",
  "updated_at": "2025-09-29T10:00:00Z"
}
```

### FR-002: Hierarchical Category Structures

**Test**: Create nested categories up to 5 levels

```bash
# Level 1: Electronics (already created)

# Level 2: Computers
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computers",
    "parent_id": 1,
    "description": "Desktop and laptop computers"
  }'

# Level 3: Laptops
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptops",
    "parent_id": 2,
    "description": "Portable computers"
  }'

# Level 4: Gaming Laptops
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptops",
    "parent_id": 3,
    "description": "High-performance gaming laptops"
  }'

# Level 5: High-End Gaming Laptops
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High-End Gaming Laptops",
    "parent_id": 4,
    "description": "Premium gaming laptops"
  }'
```

**Validation**: Verify 5-level hierarchy created successfully.

### FR-003: Prevent Circular Hierarchies

**Test**: Attempt to create circular reference

```bash
# Try to make Electronics (ID: 1) a child of High-End Gaming Laptops (ID: 5)
curl -X PUT http://localhost:8005/categories/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": 5
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "error": {
    "code": "CIRCULAR_HIERARCHY",
    "message": "Cannot create circular hierarchy",
    "details": {
      "field": "parent_id",
      "reason": "Category cannot be moved to become its own descendant"
    }
  },
  "timestamp": "2025-09-29T10:00:00Z",
  "request_id": "req_12345"
}
```

### FR-006: Category Listings with Product Counts

**Test**: Get category hierarchy with product counts

```bash
# Get root categories with children and product counts
curl "http://localhost:8005/categories?include_children=true&include_product_count=true"
```

**Expected Response**:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices and accessories",
      "parent_id": null,
      "product_count": 15,
      "children": [
        {
          "id": 2,
          "name": "Computers",
          "slug": "computers",
          "parent_id": 1,
          "product_count": 8,
          "children": [
            {
              "id": 3,
              "name": "Laptops",
              "slug": "laptops",
              "parent_id": 2,
              "product_count": 5
            }
          ]
        }
      ]
    }
  ],
  "total": 1,
  "filters": {
    "parent_id": null,
    "include_children": true,
    "include_product_count": true,
    "active_only": true
  }
}
```

### FR-007: Retrieve Products by Category

**Test**: Get products for a category including subcategories

```bash
# Get products in Electronics category including subcategories
curl "http://localhost:8005/categories/1/products?include_subcategories=true&limit=10"
```

**Expected Response**:
```json
{
  "products": [
    {
      "id": 101,
      "name": "Gaming Laptop Pro",
      "price": 1299.99,
      "image_url": "https://example.com/laptop-pro.jpg",
      "category_ids": [1, 2, 3, 4]
    },
    {
      "id": 102,
      "name": "Wireless Mouse",
      "price": 29.99,
      "image_url": "https://example.com/mouse.jpg",
      "category_ids": [1, 6]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 15,
    "pages": 2,
    "has_next": true,
    "has_prev": false
  },
  "category": {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics"
  },
  "filters": {
    "include_subcategories": true
  }
}
```

### FR-008: Product Catalog Integration

**Test**: Verify integration with Product Catalog Service

```bash
# Test category creation triggers product catalog notification
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smartphones",
    "parent_id": 1,
    "description": "Mobile phones and accessories"
  }'

# Verify products can be retrieved for new category
curl "http://localhost:8005/categories/6/products"
```

**Validation**: Service should handle product catalog service availability gracefully.

### FR-012: Move Categories Between Parents

**Test**: Move category to different parent

```bash
# Move Smartphones from Electronics to a new Mobile Devices category
# First create Mobile Devices
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile Devices",
    "parent_id": 1,
    "description": "Portable mobile devices"
  }'

# Move Smartphones to Mobile Devices
curl -X PUT http://localhost:8005/categories/6 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": 7
  }'

# Verify hierarchy updated correctly
curl "http://localhost:8005/categories/6/hierarchy"
```

**Expected Response**:
```json
{
  "category": {
    "id": 6,
    "name": "Smartphones",
    "parent_id": 7
  },
  "ancestors": [
    {
      "id": 1,
      "name": "Electronics",
      "parent_id": null
    },
    {
      "id": 7,
      "name": "Mobile Devices",
      "parent_id": 1
    }
  ],
  "descendants": [],
  "depth": 2,
  "max_depth": 5
}
```

## Integration Testing

### Auth Service Integration

**Test**: Verify JWT token validation

```bash
# Test with invalid token
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Category"}'
```

**Expected Response** (401 Unauthorized):
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired authentication token"
  },
  "timestamp": "2025-09-29T10:00:00Z",
  "request_id": "req_12346"
}
```

### Product Catalog Service Integration

**Test**: Handle product service unavailability

```bash
# Stop product catalog service temporarily
docker-compose stop product-catalog-service

# Try to get products for category
curl "http://localhost:8005/categories/1/products"
```

**Expected Response** (503 Service Unavailable):
```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Product catalog service is currently unavailable",
    "details": {
      "service": "product-catalog",
      "retry_after": "30s"
    }
  },
  "timestamp": "2025-09-29T10:00:00Z",
  "request_id": "req_12347"
}
```

## Docker Validation

### Build and Run Container

```bash
# Build Docker image
docker build -t category-service:latest .

# Run container with dependencies
docker-compose up -d category-service

# Verify container health
docker-compose ps category-service
curl http://localhost:8005/health
```

### Integration with Docker Compose

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run integration tests
curl http://localhost:8005/health/ready

# Test category creation through gateway
curl -X POST http://localhost:8000/api/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Category",
    "description": "Test category via API Gateway"
  }'
```

## Swagger Documentation Validation

**Test**: Verify Swagger documentation is accessible

```bash
# Access Swagger UI
curl -I http://localhost:8005/docs

# Download swagger.json
curl http://localhost:8005/swagger.json -o swagger.json

# Verify swagger.json is valid
npx swagger-parser validate swagger.json
```

**Expected**:
- Swagger UI accessible at http://localhost:8005/docs
- swagger.json file generated in service folder
- All API endpoints documented with examples

## Performance Testing

### Basic Load Test

```bash
# Install dependencies for load testing
npm install -g autocannon

# Test category listing performance
autocannon -c 10 -d 30 http://localhost:8005/categories

# Test single category retrieval
autocannon -c 10 -d 30 http://localhost:8005/categories/1
```

**Performance Targets**:
- Response time <200ms p95
- Handle 1000+ requests/second for read operations
- Support hierarchies up to 5 levels deep

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove test data
rm -f services/category-service/category_service.db

# Clean up environment
unset ADMIN_TOKEN
```

## Success Criteria Checklist

- [ ] Service starts successfully on port 8005
- [ ] Health checks return proper status
- [ ] Category creation requires admin authentication
- [ ] Hierarchical categories work up to 5 levels
- [ ] Circular hierarchy prevention works
- [ ] Product-category integration functional
- [ ] Category moving preserves relationships
- [ ] Swagger documentation generated and accessible
- [ ] Docker container builds and runs
- [ ] Integration with existing services works
- [ ] Performance targets met
- [ ] Error handling works correctly

This quickstart guide validates all major functional requirements and ensures the category management service integrates properly with the existing Project Zero App infrastructure.