# Product Catalog Service Documentation

**Service Type**: Backend Product Management Service  
**Technology**: FastAPI (Python 3.13+)  
**Port**: 8004  
**Repository Path**: `services/product-catalog-service/`

## Overview

The Product Catalog Service provides comprehensive product management capabilities for the Project Zero App e-commerce platform. It offers public product browsing, search functionality, and administrative product management with a focus on performance, scalability, and data consistency.

## Purpose and Responsibilities

### Core Functions

- **Product Catalog**: Public product browsing with filtering, sorting, and search
- **Product Management**: Administrative CRUD operations for product lifecycle
- **Search and Discovery**: Advanced search functionality with category support
- **Data Seeding**: Deterministic product data for development and testing
- **Performance Optimization**: Efficient querying and caching strategies

### In-Scope Features

- Public product catalog with pagination and filtering
- Product search functionality with text and category filtering
- Administrative product CRUD operations (JWT protected)
- Product category management and organization
- Deterministic product seeding (20 products across categories)
- Health monitoring and readiness checks
- OpenAPI documentation for all endpoints

### Out-of-Scope (Future Considerations)

- Inventory management and stock tracking
- Product reviews and ratings
- Product recommendations and personalization
- Image upload and media management
- Advanced search with Elasticsearch integration

## Architecture Overview

```text
┌─── FastAPI Application ───┐
│  ├── /products/* routes   │
│  ├── Search endpoints     │
│  ├── Admin middleware     │
│  └── Health monitoring    │
├─── Business Logic ────────┤
│  ├── Product operations   │
│  ├── Search algorithms    │
│  ├── Category management  │
│  └── Validation logic     │
├─── Data Access Layer ─────┤
│  ├── SQLAlchemy ORM       │
│  ├── Product models       │
│  ├── Category models      │
│  └── Database indexing    │
├─── External Integration ──┤
│  ├── Auth service         │
│  └── Future: Search engine│
└─── Infrastructure ────────┘
   ├── PostgreSQL/SQLite
   ├── Database migrations
   └── Performance monitoring
```

## API Endpoints

### Public Product Endpoints

- `GET /products` - List all products with pagination and filtering
- `GET /products/{id}` - Get detailed product information
- `GET /products/search` - Search products by text and category
- `GET /products/category/{category}` - Get products by category

### Administrative Endpoints (JWT Required)

- `POST /products` - Create new product (admin only)
- `PUT /products/{id}` - Update existing product (admin only)
- `DELETE /products/{id}` - Delete product (admin only)

### Category Management

- `GET /categories` - List all product categories
- `GET /categories/{category}/products` - Get products in category

### Health and Monitoring

- `GET /health` - Basic service health check
- `GET /health/ready` - Readiness check with database validation

## Technology Stack

### Core Technologies

- **FastAPI**: High-performance web framework with automatic OpenAPI generation
- **Python 3.13+**: Latest Python with enhanced performance and type system
- **SQLAlchemy**: Advanced ORM with relationship management and query optimization
- **Pydantic**: Data validation and serialization with comprehensive type safety

### Database and Performance

- **SQLite**: Development and testing with in-memory optimization
- **PostgreSQL**: Production database with advanced indexing and full-text search
- **Database Indexing**: Optimized indexes for search and category filtering

### Development and Testing

- **pytest**: Comprehensive testing framework with fixtures
- **ruff**: Fast Python linting and formatting
- **uv**: Modern Python package management

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required | Notes |
|----------|---------|---------|----------|-------|
| `DATABASE_URL` | Database connection | `sqlite:///./product_catalog.db` | No | PostgreSQL for production |
| `JWT_SECRET_KEY` | JWT verification | Auto-generated | Recommended | Must match auth service |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | No | Admin endpoint verification |
| `HOST` | Service bind address | `0.0.0.0` | No | Container-friendly |
| `PORT` | Service port | `8004` | No | Service mesh configuration |
| `DATABASE_ECHO` | SQL query logging | `false` | No | Development debugging |

## Product Data Model

### Product Schema

```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "price": "decimal",
  "category": "string",
  "weight": "decimal",
  "in_stock": "boolean",
  "image_url": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Categories

- **Electronics**: Computers, phones, accessories
- **Clothing**: Apparel and fashion items
- **Books**: Literature and educational materials
- **Home & Garden**: Household and outdoor items
- **Sports**: Athletic equipment and gear

### Product Seeding Data

The service includes 20 deterministic products across all categories:

- **Electronics** (4 products): Laptop, smartphone, headphones, tablet
- **Clothing** (4 products): T-shirt, jeans, sneakers, jacket
- **Books** (4 products): Novel, cookbook, textbook, biography
- **Home & Garden** (4 products): Coffee maker, plant, toolset, lamp
- **Sports** (4 products): Basketball, yoga mat, running shoes, bicycle

## Search and Filtering

### Search Capabilities

- **Text Search**: Product name and description matching
- **Category Filtering**: Filter by product category
- **Price Range**: Filter by minimum and maximum price
- **Stock Status**: Filter by availability
- **Combined Filters**: Multiple filter criteria support

### Search Optimization

- Database indexes on searchable fields
- Efficient query construction with SQLAlchemy
- Pagination support for large result sets
- Case-insensitive text matching

## Performance Considerations

### Database Optimization

- Indexes on frequently queried fields (category, price, name)
- Query optimization with SQLAlchemy relationship loading
- Connection pooling for concurrent requests
- Database query monitoring and profiling

### Caching Strategy (Planned)

- Redis integration for frequently accessed products
- Category-based cache invalidation
- Search result caching with TTL
- Product detail page caching

## Integration Patterns

### Authentication Integration

```text
Product Service ──► Auth Service (/auth/verify)
                        │
                        └─── Admin endpoint protection
```

### API Gateway Integration

- Public endpoints accessible without authentication
- Admin endpoints require JWT token validation
- Consistent error handling and response formats

## Deployment and Operations

### Local Development

```bash
cd services/product-catalog-service
uv sync
uv run uvicorn src.main:app --reload --port 8004
```

### Docker Deployment

```bash
docker build -t product-catalog-service:latest services/product-catalog-service
docker run -p 8004:8004 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/productdb" \
  product-catalog-service:latest
```

### Database Initialization

```bash
# Run database seeding
uv run python -m src.database.seed
```

## Security Considerations

### Access Control

- Public read access for product browsing
- JWT-protected administrative operations
- Input validation and sanitization
- Rate limiting on search endpoints (planned)

### Data Protection

- Secure handling of product data
- Protection against SQL injection via ORM
- Input validation using Pydantic models

## Monitoring and Observability

### Logging

- Structured logging for all operations
- Search query logging and analytics
- Administrative action audit trails
- Performance metrics collection

### Metrics (Planned)

- Product view and search analytics
- API endpoint performance monitoring
- Database query performance tracking
- Cache hit/miss ratios

## Related Documentation

### Service Documentation

- [API Documentation](./api-docs/endpoints.md) - Complete API reference
- [Search API](./api-docs/search-api.md) - Search functionality details
- [Architecture Overview](./architecture/overview.md) - Technical design
- [Data Model](./architecture/data-model.md) - Database schema

### Operational Documentation

- [Data Management](./operations/data-management.md) - Product lifecycle procedures
- [Performance Monitoring](./monitoring/performance-metrics.md) - Monitoring setup
- [Integration Guide](./integration/service-integration.md) - Service integration
- [Troubleshooting](./troubleshooting/common-issues.md) - Issue resolution

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Service Version**: 1.0.0  
**Documentation Version**: 1.0.0