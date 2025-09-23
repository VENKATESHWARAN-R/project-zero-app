# Project Zero App - Product Catalog Service

A high-performance, RESTful product catalog microservice for the Project Zero App e-commerce platform.

## 🎯 Overview

The Product Catalog Service provides comprehensive product management and discovery functionality for the Project Zero App ecosystem. It implements modern API design principles with robust search, filtering, and pagination capabilities.

### Key Features

- **📦 Product Management**: Full CRUD operations for products with category organization
- **🔍 Advanced Search**: Text-based search across product names and descriptions
- **📂 Category Filtering**: Organized product browsing by category (electronics, clothing, books, home goods)
- **📄 Pagination**: Efficient large dataset handling with offset/limit pagination
- **🔒 Security**: JWT authentication integration for admin operations
- **🚀 High Performance**: Async FastAPI with SQLAlchemy ORM (all endpoints < 200ms)
- **📊 Monitoring**: Health checks, structured logging, comprehensive error handling
- **🧪 Test Coverage**: 45+ tests across contract, integration, and unit test suites
- **🐳 Cloud Ready**: Docker containerized with database migration support
- **🔄 Microservice Architecture**: Designed for distributed systems with external auth

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│ Product Catalog  │────│   Database      │
│  (React/Next)   │    │   Service        │    │  (SQLite/PG)    │
└─────────────────┘    │   (FastAPI)      │    └─────────────────┘
                       └──────────────────┘
                              │
                       ┌──────────────────┐
                       │   Auth Service   │
                       │ (Token Verify)   │
                       └──────────────────┘
```

## 🚀 API Endpoints

### Public Endpoints (No Authentication)
- `GET /products` - List all products with pagination
- `GET /products/{id}` - Get product by ID
- `GET /products/category/{category}` - Filter by category
- `GET /products/search?q=query` - Search products
- `GET /health` - Service health check
- `GET /health/ready` - Readiness probe

### Admin Endpoints (JWT Authentication Required)
- `POST /products` - Create new product
- `PUT /products/{id}` - Update existing product

## 📊 API Reference

### Product Schema
```json
{
  "id": 1,
  "name": "Smartphone Pro Max",
  "description": "Latest flagship smartphone...",
  "price": 999.99,
  "category": "electronics",
  "image_url": "https://...",
  "stock_quantity": 50,
  "is_active": true,
  "created_at": "2025-09-23T14:15:26.038798",
  "updated_at": "2025-09-23T14:15:26.038803"
}
```

### Categories
- `electronics` - Smartphones, laptops, cameras, etc.
- `clothing` - Apparel, shoes, accessories
- `books` - Fiction, textbooks, cookbooks
- `home_goods` - Furniture, kitchenware, lighting

### Pagination Response
```json
{
  "items": [...],
  "total": 100,
  "offset": 0,
  "limit": 20,
  "has_more": true
}
```

## 🛠️ Environment Variables

| Name | Purpose | Default | Required |
|------|---------|---------|----------|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./product_catalog.db` | No |
| `AUTH_SERVICE_URL` | Authentication service base URL | `http://auth-service:8001` | Yes (prod) |
| `HOST` | Bind host | `0.0.0.0` | No |
| `PORT` | Service port | `8002` | No |

## 🏃 Quick Start

### Prerequisites
- Python 3.13+
- `uv` package manager
- Optional: Docker, PostgreSQL

### Local Development

```bash
cd services/product-catalog-service
uv sync                    # Install dependencies
uv run uvicorn src.main:app --reload --port 8002
# Visit: http://localhost:8002/docs
```

### Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Specific test suites
uv run pytest tests/contract/     # Contract tests
uv run pytest tests/integration/ # Integration tests
uv run pytest tests/unit/        # Unit tests
```

### Code Quality

```bash
# Format and lint
uv run ruff format .
uv run ruff check .
```

## 🐳 Docker

### Build Image
```bash
cd services/product-catalog-service
docker build -t product-catalog-service:latest .
```

### Run Container (SQLite)
```bash
docker run -p 8002:8002 \
    -e AUTH_SERVICE_URL="http://auth-service:8001" \
    product-catalog-service:latest
```

### Run with PostgreSQL
```bash
docker network create project-zero-net || true

# Start PostgreSQL
docker run -d --name catalog-db --network project-zero-net \
    -e POSTGRES_DB=catalogdb \
    -e POSTGRES_USER=cataloguser \
    -e POSTGRES_PASSWORD=catalogpass \
    postgres:15

# Start service
docker run -p 8002:8002 --network project-zero-net \
    -e DATABASE_URL="postgresql://cataloguser:catalogpass@catalog-db:5432/catalogdb" \
    -e AUTH_SERVICE_URL="http://auth-service:8001" \
    product-catalog-service:latest
```

### Health Check
```bash
curl http://localhost:8002/health
```

## 🔐 Authentication Integration

Admin operations require JWT tokens from the Auth Service:

```bash
# Get token from auth service
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}' \
  | jq -r '.access_token')

# Create product
curl -X POST http://localhost:8002/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "price": 99.99,
    "category": "electronics",
    "image_url": "https://example.com/image.jpg",
    "stock_quantity": 50
  }'
```

## 🧪 Testing Strategy

### Contract Tests
Verify API specification compliance:
- Response schemas and structure
- HTTP status codes
- Error handling
- Input validation

### Integration Tests
End-to-end workflow testing:
- Product lifecycle (CRUD)
- Search and filtering
- Admin authentication flows
- Error scenarios

### Unit Tests
Component-level testing:
- Service layer business logic
- Schema validation
- Authentication dependencies
- Database operations

## 📈 Performance

All endpoints perform under 200ms:
- Health: ~6ms
- Product list: ~41ms
- Search: ~57ms
- Category filter: ~5ms
- Single product: ~4ms

Performance tested with:
- 20 sample products across 4 categories
- Concurrent request handling
- SQLite (dev) and PostgreSQL (production) ready

## 🔧 Database Schema

### Products Table
- `id` - Primary key (auto-increment)
- `name` - Product name (unique, indexed)
- `description` - Product description (text)
- `price` - Decimal price (precision: 10,2)
- `category` - Enum category
- `image_url` - Product image URL
- `stock_quantity` - Integer stock count
- `is_active` - Boolean active status
- `created_at` - Timestamp
- `updated_at` - Timestamp

### Indexes
- Primary key on `id`
- Unique index on `name`
- Index on `category` for filtering
- Index on `is_active` for public queries

## 🚨 Error Handling

Standard HTTP error responses:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `404` - Not Found
- `422` - Unprocessable Entity (schema validation)
- `429` - Too Many Requests (rate limiting)
- `500` - Internal Server Error

## 📝 Development Notes

### Route Order
Search routes (`/search`) must be defined before parameterized routes (`/{id}`) to avoid routing conflicts.

### Database Seeding
Service automatically seeds 20 sample products on startup for development and testing.

### Category Management
Categories are defined as enums in the codebase. To add new categories:
1. Update `CategoryEnum` in `src/models/product.py`
2. Update category validation in schemas
3. Run database migrations if needed

## 🔄 Service Dependencies

### Runtime Dependencies
- **Auth Service** - JWT token verification for admin operations
- **Database** - SQLite (dev) / PostgreSQL (prod) for data persistence

### Development Dependencies
- **uv** - Python package management
- **ruff** - Code formatting and linting
- **pytest** - Testing framework
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM and database toolkit

## 📚 Related Documentation

- [Project Zero App - CLAUDE.md](../../CLAUDE.md) - Main project documentation
- [Auth Service README](../auth-service/README.md) - Authentication service docs
- [API Contract Specification](../../specs/002-build-a-product/) - Detailed API specs
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework reference

---

**Last Updated:** 2025-09-23
**Service Version:** 1.0.0
**API Version:** 1.0.0