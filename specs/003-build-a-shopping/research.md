# Research: Shopping Cart Service

**Date**: 2025-09-23
**Feature**: Shopping Cart Service
**Status**: Phase 0 Complete

## Research Tasks Completed

### 1. Node.js Express Best Practices for Microservices

**Decision**: Express.js with middleware-based architecture
**Rationale**:
- Lightweight and fast for microservices
- Extensive middleware ecosystem (cors, validation, logging)
- Simple to understand and maintain
- Good integration with Sequelize ORM

**Alternatives considered**:
- Fastify: Higher performance but smaller ecosystem
- Koa.js: Modern async/await but less middleware availability
- NestJS: More complex, violates simplicity principle

### 2. Sequelize ORM Configuration for Cart Data

**Decision**: Sequelize with SQLite for development, PostgreSQL for production
**Rationale**:
- Mature ORM with good TypeScript support
- Built-in migrations and model definitions
- Supports both SQLite and PostgreSQL
- Consistent with constitution database standards

**Alternatives considered**:
- Prisma: Modern but adds complexity for simple use case
- TypeORM: Good but heavier than needed
- Raw SQL: Too low-level for demo purposes

### 3. Service Integration Patterns

**Decision**: HTTP REST calls with axios and circuit breaker pattern
**Rationale**:
- Simple HTTP integration following REST principles
- Axios provides good error handling and timeouts
- Circuit breaker prevents cascade failures
- Aligns with existing service architecture

**Alternatives considered**:
- gRPC: More complex setup, not used by existing services
- Message queues: Adds infrastructure complexity
- GraphQL federation: Over-engineered for cart operations

### 4. Authentication Middleware Design

**Decision**: JWT verification middleware calling auth service
**Rationale**:
- Stateless authentication matching existing auth service
- Middleware pattern for reusable auth checks
- Direct service-to-service calls for token validation
- Consistent with project security standards

**Alternatives considered**:
- Local JWT verification: Requires shared secrets management
- Session-based auth: Stateful, doesn't match existing pattern
- OAuth: Over-complex for internal service communication

### 5. Cart Data Model Design

**Decision**: Cart and CartItem entities with user association
**Rationale**:
- Normalized data model prevents duplication
- User-cart relationship enables multi-session support
- Product ID reference allows external product data
- Quantity and timestamps for business logic

**Key entities identified**:
- Cart: user_id, created_at, updated_at
- CartItem: cart_id, product_id, quantity, created_at

### 6. Error Handling and Validation Strategy

**Decision**: express-validator for input validation, structured error responses
**Rationale**:
- Declarative validation rules
- Consistent error format across endpoints
- Integration with Express middleware chain
- JSON error responses for API consumers

**Error response format**:
```json
{
  "error": "Validation failed",
  "details": [
    {"field": "quantity", "message": "Must be positive integer"}
  ]
}
```

### 7. Logging and Monitoring Approach

**Decision**: Winston for structured logging, custom middleware for request tracking
**Rationale**:
- JSON structured logs for parsing
- Request correlation IDs for tracing
- Multiple log levels and transports
- Health check endpoints for monitoring

**Log format**:
```json
{
  "timestamp": "2025-09-23T10:00:00Z",
  "level": "info",
  "message": "Cart item added",
  "correlationId": "req-123",
  "userId": "user-456",
  "productId": "prod-789"
}
```

### 8. Package Management and Dependencies

**Decision**: Yarn for package management with lockfile
**Rationale**:
- Consistent dependency resolution
- Workspace support for future monorepo
- Faster installs than npm
- User requirement specification

**Core dependencies**:
- express: Web framework
- sequelize: ORM
- sqlite3: Development database
- express-validator: Input validation
- axios: HTTP client
- winston: Logging
- cors: Cross-origin support
- jsonwebtoken: JWT handling

## Configuration Decisions

### Port and Service Discovery
- **Port**: 8007 (as specified)
- **Health endpoints**: /health and /health/ready
- **API prefix**: /cart for all cart operations

### Environment Variables
- `DATABASE_URL`: Database connection string
- `PORT`: Service port (default 8007)
- `AUTH_SERVICE_URL`: Auth service URL (default http://localhost:8001)
- `PRODUCT_SERVICE_URL`: Product service URL (default http://localhost:8002)
- `LOG_LEVEL`: Logging level (default info)
- `CART_TTL_HOURS`: Cart expiration time (default 24)

### API Endpoint Design
- POST /cart/add - Add item to cart
- GET /cart - Get cart contents with product details
- PUT /cart/items/:productId - Update item quantity
- DELETE /cart/items/:productId - Remove item
- DELETE /cart - Clear entire cart
- GET /health - Health check
- GET /health/ready - Readiness check

## Resolved Clarifications

1. **Quantity limits per item**: Default max 10 per item (configurable)
2. **Cart persistence duration**: 24 hours of inactivity (configurable)
3. **Cross-session cart**: Single cart per user, persists across sessions

## Next Phase Prerequisites

All research complete. Ready for Phase 1 design with:
- Technology stack finalized
- Integration patterns defined
- Data model approach confirmed
- Configuration strategy established