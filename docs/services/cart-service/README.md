# Cart Service Documentation

**Service Type**: Backend Cart Management Service  
**Technology**: Node.js (Express)  
**Port**: 8007  
**Repository Path**: `services/cart-service/`

## Overview

The Cart Service manages shopping cart functionality for the Project Zero App e-commerce platform. Built with Node.js and Express, it provides session-based cart management, product validation, and seamless integration with authentication and product catalog services.

## Purpose and Responsibilities

### Core Functions

- **Cart Management**: Create, update, and manage user shopping carts
- **Session Handling**: Persistent cart storage with session management
- **Product Integration**: Validate products and maintain cart consistency
- **Authentication**: JWT-based user authentication and cart isolation
- **Performance**: Efficient cart operations with caching strategies

### In-Scope Features

- User-specific cart creation and management
- Add, update, and remove cart items with validation
- Product availability and pricing validation
- Cart persistence across user sessions
- JWT authentication integration with auth service
- Health monitoring and dependency validation
- RESTful API with comprehensive error handling

### Out-of-Scope (Future Considerations)

- Guest cart functionality (non-authenticated users)
- Cart sharing and collaboration features
- Advanced pricing rules and discounts
- Cart abandonment tracking and recovery
- Real-time cart synchronization across devices

## Architecture Overview

```text
┌─── Express Application ───┐
│  ├── /cart/* routes       │
│  ├── JWT middleware       │
│  ├── Validation layer     │
│  └── Health endpoints     │
├─── Business Logic ────────┤
│  ├── Cart operations      │
│  ├── Item management      │
│  ├── Product validation   │
│  └── Session handling     │
├─── Data Access Layer ─────┤
│  ├── SQLite database      │
│  ├── Cart models          │
│  ├── Item relationships   │
│  └── Database migrations  │
├─── External Integration ──┤
│  ├── Auth service         │
│  ├── Product catalog      │
│  └── Session management   │
└─── Infrastructure ────────┘
   ├── SQLite/Redis
   ├── HTTP clients
   └── Error handling
```

## API Endpoints

### Cart Management

- `GET /carts/{user_id}` - Get user's cart with all items
- `POST /carts/{user_id}/items` - Add item to cart with validation
- `PUT /carts/{user_id}/items/{item_id}` - Update item quantity
- `DELETE /carts/{user_id}/items/{item_id}` - Remove item from cart
- `DELETE /carts/{user_id}` - Clear entire cart

### Cart Information

- `GET /carts/{user_id}/summary` - Get cart summary with totals
- `GET /carts/{user_id}/count` - Get total item count in cart

### Health and Monitoring

- `GET /health` - Basic service health check
- `GET /health/ready` - Readiness check with dependencies

## Technology Stack

### Core Technologies

- **Node.js**: JavaScript runtime with async/await support
- **Express.js**: Web framework with middleware support
- **SQLite**: Embedded database for development and testing
- **Knex.js**: SQL query builder with migration support

### Service Integration

- **axios**: HTTP client for service communication
- **jsonwebtoken**: JWT token verification
- **Auth Service**: User authentication via token verification
- **Product Service**: Product validation and details

### Development Tools

- **Jest**: Testing framework with comprehensive coverage
- **ESLint**: Code linting with Airbnb style guide
- **Prettier**: Code formatting and style consistency
- **nodemon**: Development server with auto-reload

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required | Notes |
|----------|---------|---------|----------|-------|
| `DATABASE_URL` | SQLite database path | `sqlite:cart.db` | No | Use Redis for production |
| `AUTH_SERVICE_URL` | Auth service endpoint | `http://localhost:8001` | Yes | JWT verification |
| `PRODUCT_SERVICE_URL` | Product catalog URL | `http://localhost:8004` | Yes | Product validation |
| `JWT_SECRET` | JWT verification key | Auto-generated | Recommended | Must match auth service |
| `PORT` | Service port | `8007` | No | Service mesh port |
| `NODE_ENV` | Environment mode | `development` | No | Controls features |
| `LOG_LEVEL` | Logging verbosity | `info` | No | debug, info, warn, error |

## Cart Data Model

### Cart Schema

```json
{
  "user_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "items": [
    {
      "id": "integer",
      "product_id": "integer",
      "quantity": "integer",
      "price": "decimal",
      "added_at": "datetime"
    }
  ],
  "totals": {
    "subtotal": "decimal",
    "tax": "decimal",
    "total": "decimal",
    "item_count": "integer"
  }
}
```

### Database Tables

- **carts**: User cart metadata and timestamps
- **cart_items**: Individual items with product references
- **Indexes**: Optimized for user_id and product_id lookups

## Cart Operations

### Add Item Workflow

1. **Authentication**: Verify JWT token with auth service
2. **Product Validation**: Validate product exists and is available
3. **Quantity Check**: Ensure positive quantity and stock availability
4. **Duplicate Handling**: Update quantity if item already exists
5. **Database Update**: Save item to cart with current price
6. **Response**: Return updated cart with totals

### Cart Calculations

- **Subtotal**: Sum of (quantity × price) for all items
- **Tax Calculation**: Applied by order service during checkout
- **Item Count**: Total quantity across all items
- **Price Snapshot**: Product prices captured at add time

## Integration Patterns

### Service Dependencies

```text
Cart Service ──► Auth Service (/auth/verify)
     │
     └─────────► Product Service (/products/{id})
```

### Error Handling

- **401 Unauthorized**: Invalid or expired JWT tokens
- **404 Not Found**: Cart or product not found
- **422 Unprocessable Entity**: Invalid cart operation
- **503 Service Unavailable**: External service failures
- **400 Bad Request**: Invalid request parameters

### Authentication Flow

1. Extract JWT token from Authorization header
2. Verify token with auth service `/auth/verify` endpoint
3. Extract user_id from verified token payload
4. Authorize cart operations for authenticated user

## Performance Considerations

### Database Optimization

- Indexes on user_id and product_id for fast lookups
- Connection pooling for concurrent requests
- Efficient query patterns with Knex.js
- Database transaction management for consistency

### Caching Strategy

- In-memory cart caching for frequently accessed carts
- Product information caching to reduce API calls
- Session-based cache invalidation
- Redis integration for production environments

## Session Management

### Cart Persistence

- User carts persist across login sessions
- Items maintain product price snapshots
- Automatic cleanup of abandoned carts (planned)
- Session timeout and renewal handling

### Concurrency Handling

- Optimistic locking for cart updates
- Race condition prevention for item modifications
- Atomic operations for cart state changes

## Deployment and Operations

### Local Development

```bash
cd services/cart-service
npm install
npm run migrate
npm run dev
```

### Docker Deployment

```bash
docker build -t cart-service:latest services/cart-service
docker run -p 8007:8007 \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  -e PRODUCT_SERVICE_URL="http://product-service:8004" \
  cart-service:latest
```

### Database Management

```bash
# Run migrations
npm run migrate

# Rollback migrations
npm run migrate:rollback

# Seed development data
npm run seed
```

## Security Considerations

### Authentication and Authorization

- JWT token validation for all cart operations
- User isolation ensuring cart access control
- Secure handling of user identifiers
- Protection against cart manipulation attacks

### Data Protection

- Input validation and sanitization
- SQL injection prevention via query builder
- Secure storage of cart and item data
- Rate limiting on cart operations (planned)

## Monitoring and Observability

### Logging

- Structured JSON logging for production
- Cart operation audit trails
- Service integration call logging
- Error tracking with detailed context

### Metrics (Planned)

- Cart creation and abandonment rates
- Item addition and removal analytics
- Average cart value and size metrics
- Service dependency health monitoring

## Testing Strategy

### Test Coverage

- **Unit Tests**: Cart operations and business logic
- **Integration Tests**: Database operations and migrations
- **Contract Tests**: External service integration
- **E2E Tests**: Complete cart workflows

### Test Categories

```bash
npm test                    # All tests
npm run test:unit          # Unit tests only
npm run test:integration   # Integration tests
npm run test:contract      # Contract tests
npm run test:coverage      # Coverage report
```

## Related Documentation

### Service Documentation

- [API Documentation](./api-docs/endpoints.md) - Complete API reference
- [Session Management](./api-docs/session-management.md) - Cart persistence
- [Architecture Overview](./architecture/overview.md) - Technical design
- [Redis Integration](./architecture/redis-integration.md) - Caching layer

### Operational Documentation

- [Cache Management](./operations/cache-management.md) - Operational procedures
- [Data Recovery](./disaster-recovery/data-recovery.md) - Backup and recovery
- [Integration Guide](./integration/auth-product-integration.md) - Service integration
- [Troubleshooting](./troubleshooting/common-issues.md) - Issue resolution

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Service Version**: 1.0.0  
**Documentation Version**: 1.0.0