# Category Management Service

Hierarchical category management service for the Project Zero App e-commerce platform. Provides REST API endpoints for creating, managing, and querying product categories with support for multi-level hierarchies up to 5 levels deep.

## Features

- ✅ **Hierarchical Categories**: Support for parent-child relationships up to 5 levels deep
- ✅ **Admin Authentication**: JWT-based authentication for category management operations
- ✅ **Circular Hierarchy Prevention**: Built-in validation to prevent circular references
- ✅ **Auto-generated Slugs**: URL-friendly slugs generated automatically from category names
- ✅ **Product Integration**: Seamless integration with product catalog service
- ✅ **Health Monitoring**: Comprehensive health and readiness endpoints
- ✅ **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- ✅ **Docker Support**: Containerized deployment with multi-stage builds
- ✅ **Structured Logging**: JSON logging with request correlation IDs
- ✅ **Rate Limiting**: Built-in rate limiting for API protection

## Quick Start

### Prerequisites

- Node.js 18+
- Yarn package manager
- Auth Service running on port 8001 (for admin operations)

### Local Development

```bash
# Clone and navigate to service directory
cd services/category-service

# Install dependencies
yarn install

# Set up environment variables
cp .env.example .env

# Run database migrations
yarn db:migrate

# (Optional) Seed sample categories
yarn db:seed

# Start development server
yarn dev

# Service runs on http://localhost:8005
```

### Docker Deployment

```bash
# Build Docker image
docker build -t category-service:latest .

# Run container
docker run -p 8005:8005 \
  -e AUTH_SERVICE_URL=http://host.docker.internal:8001 \
  category-service:latest
```

## API Endpoints

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health status |
| GET | `/health/ready` | Service readiness with dependencies |
| GET | `/categories` | List categories with filtering |
| GET | `/categories/{id}` | Get category by ID |
| GET | `/categories/{id}/hierarchy` | Get category hierarchy information |
| GET | `/categories/{id}/products` | Get products in category |
| GET | `/categories/search` | Search categories by name/description |
| GET | `/docs` | Interactive Swagger documentation |
| GET | `/swagger.json` | OpenAPI specification |

### Admin Endpoints (Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/categories` | Create new category |
| PUT | `/categories/{id}` | Update existing category |
| DELETE | `/categories/{id}` | Delete category |

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HOST` | Server bind address | `0.0.0.0` | No |
| `PORT` | Server port | `8005` | No |
| `NODE_ENV` | Environment mode | `development` | No |
| `DATABASE_URL` | Database connection string | `sqlite:///category_service.db` | No |
| `JWT_SECRET_KEY` | JWT secret (must match auth service) | Auto-generated | Recommended |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | Yes |
| `PRODUCT_SERVICE_URL` | Product catalog URL | `http://localhost:8004` | Yes |
| `LOG_LEVEL` | Logging level | `info` | No |
| `RATE_LIMIT_WINDOW_MS` | Rate limit window | `900000` (15 min) | No |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per window | `100` | No |
| `CORS_ORIGIN` | CORS allowed origin | `http://localhost:3000` | No |
| `MAX_HIERARCHY_DEPTH` | Maximum category depth | `5` | No |

### Database Configuration

**Development (SQLite)**:
```bash
DATABASE_URL=sqlite:///category_service.db
```

**Production (PostgreSQL)**:
```bash
DATABASE_URL=postgresql://username:password@host:5432/database
```

## Usage Examples

### List Root Categories

```bash
curl http://localhost:8005/categories
```

**Response**:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices and accessories",
      "parent_id": null,
      "sort_order": 10,
      "is_active": true,
      "created_at": "2025-09-29T10:00:00Z",
      "updated_at": "2025-09-29T10:00:00Z"
    }
  ],
  "total": 1,
  "filters": {
    "parent_id": null,
    "include_children": false,
    "include_product_count": false,
    "active_only": true
  }
}
```

### Create Category (Admin Only)

```bash
curl -X POST http://localhost:8005/categories \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptops",
    "description": "High-performance gaming laptops",
    "parent_id": 3,
    "image_url": "https://example.com/gaming-laptops.jpg"
  }'
```

### Get Category with Children

```bash
curl "http://localhost:8005/categories/1?include_children=true&include_product_count=true"
```

### Search Categories

```bash
curl "http://localhost:8005/categories/search?q=electronics&active_only=true"
```

### Get Category Hierarchy

```bash
curl http://localhost:8005/categories/4/hierarchy
```

**Response**:
```json
{
  "category": {
    "id": 4,
    "name": "Gaming Laptops"
  },
  "ancestors": [
    {"id": 1, "name": "Electronics"},
    {"id": 2, "name": "Computers"},
    {"id": 3, "name": "Laptops"}
  ],
  "descendants": [],
  "depth": 3,
  "max_depth": 5
}
```

## Database Schema

### Categories Table

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    parent_id INTEGER REFERENCES categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Key Constraints

- **Unique slug**: Auto-generated from name, ensures URL-friendly identifiers
- **Hierarchy depth**: Maximum 5 levels to prevent infinite nesting
- **Circular prevention**: Application-level validation prevents circular references
- **Name uniqueness**: Within parent scope (same parent cannot have duplicate names)

## Testing

```bash
# Run all tests
yarn test

# Run specific test suites
yarn test:contract    # API contract tests
yarn test:integration # Integration tests
yarn test:unit        # Unit tests

# Run with coverage
yarn test:coverage

# Performance testing
yarn test:performance
```

## Development Scripts

```bash
yarn dev              # Start development server with auto-reload
yarn start            # Start production server
yarn test             # Run test suite
yarn lint             # Run ESLint
yarn format           # Format code with Prettier
yarn db:migrate       # Run database migrations
yarn db:seed          # Seed sample data
yarn db:migrate:undo  # Undo last migration
yarn db:seed:undo     # Undo all seeds
```

## Architecture

### Service Layer

- **CategoryService**: Core CRUD operations and business logic
- **HierarchyService**: Tree traversal and validation
- **ValidationService**: Business rule enforcement
- **SlugService**: URL-friendly identifier generation

### Middleware

- **Authentication**: JWT token verification via auth service
- **Authorization**: Admin role verification
- **Validation**: Request data validation with express-validator
- **Error Handling**: Centralized error processing and formatting
- **Logging**: Structured JSON logging with correlation IDs
- **Rate Limiting**: Token bucket algorithm for API protection

### External Integrations

- **Auth Service** (Port 8001): JWT token verification for admin operations
- **Product Catalog** (Port 8004): Product-category associations
- **API Gateway** (Port 8000): Request routing and load balancing

## Error Handling

The service returns structured error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid category name",
    "details": {
      "field": "name",
      "reason": "Name must be between 1 and 100 characters"
    }
  },
  "timestamp": "2025-09-29T10:00:00Z",
  "request_id": "req_12345"
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Category not found
- `CIRCULAR_HIERARCHY`: Circular reference detected
- `MAX_DEPTH_EXCEEDED`: Hierarchy depth limit reached
- `HAS_CHILDREN`: Cannot delete category with active children
- `INVALID_TOKEN`: Authentication token invalid
- `ADMIN_REQUIRED`: Admin privileges required
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Performance

- **Response Time**: <200ms p95 for category queries
- **Throughput**: 1000+ requests/second for read operations
- **Hierarchy Depth**: Optimized for up to 5 levels
- **Database**: Indexed for common query patterns
- **Caching**: In-memory caching for frequently accessed categories

## Security

- **Authentication**: JWT tokens verified via auth service
- **Authorization**: Role-based access control for admin operations
- **Input Validation**: Comprehensive validation and sanitization
- **Rate Limiting**: Protection against abuse and DoS attacks
- **CORS**: Configurable cross-origin request handling
- **Error Disclosure**: Secure error messages without information leakage

## Monitoring

### Health Endpoints

- `GET /health`: Basic liveness check
- `GET /health/ready`: Readiness check with dependency validation

### Logging

Structured JSON logs include:
- Request/response details
- Error information with stack traces
- Performance metrics
- Dependency health status

### Metrics

Key metrics to monitor:
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Database connection health
- Auth service connectivity
- Category hierarchy depth distribution

## Contributing

1. Follow the existing code style (ESLint + Prettier)
2. Write tests for new features
3. Update documentation for API changes
4. Ensure Docker builds successfully
5. Test integration with auth and product services

## License

MIT - See project root for license details.