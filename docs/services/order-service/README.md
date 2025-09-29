# Order Service Documentation

**Service Type**: Backend Order Management Service  
**Technology**: FastAPI (Python 3.13+)  
**Port**: 8008  
**Repository Path**: `services/order-service/`

## Overview

The Order Service manages the complete order lifecycle for the Project Zero App e-commerce platform, from cart checkout to order fulfillment. It provides comprehensive order management capabilities including tax and shipping calculations, status tracking, and integration with authentication, cart, and product catalog services.

## Purpose and Responsibilities

### Core Functions

- **Order Creation**: Convert shopping carts into orders with comprehensive validation
- **Tax and Shipping**: Calculate taxes and shipping costs based on order details
- **Status Management**: Track orders through complete lifecycle with audit trails
- **Admin Interface**: Administrative tools for order management across all users
- **Service Integration**: Coordinate with auth, cart, and product catalog services

### In-Scope Features

- Order creation from cart with complete validation and calculation
- Tax calculation using configurable rates (8.5% default)
- Weight-based shipping cost calculation with multiple tiers
- Complete order CRUD operations with status-based workflows
- Order status tracking with full lifecycle management
- Admin interface for cross-user order management
- Comprehensive audit trails for all order modifications
- Health and readiness monitoring with dependency checks

### Out-of-Scope (Future Considerations)

- Payment processing integration
- Real-time order notifications
- Advanced shipping provider integrations
- Order fulfillment automation
- Inventory reservation and management

## Architecture Overview

```text
┌─── FastAPI Application ───┐
│  ├── /orders/* endpoints  │
│  ├── JWT authentication   │
│  ├── Admin middleware     │
│  └── Health monitoring    │
├─── Business Logic ────────┤
│  ├── Order management     │
│  ├── Tax calculation      │
│  ├── Shipping logic       │
│  └── Status workflows     │
├─── Data Access Layer ─────┤
│  ├── SQLAlchemy ORM       │
│  ├── Order models         │
│  ├── Status tracking      │
│  └── Audit logging        │
├─── External Integration ──┤
│  ├── Auth service         │
│  ├── Cart service         │
│  ├── Product catalog      │
│  └── Future payment API   │
└─── Infrastructure ────────┘
   ├── PostgreSQL/SQLite
   ├── HTTP clients
   └── Configuration mgmt
```

## API Endpoints

### Order Management

- `POST /orders` - Create order from cart with validation
- `GET /orders` - Get user order history with filtering
- `GET /orders/{id}` - Get detailed order information
- `PATCH /orders/{id}` - Modify order (status-dependent)
- `POST /orders/{id}/cancel` - Cancel order with validation

### Order Status Management

- `PUT /orders/{id}/status` - Update order status (admin only)
- `GET /orders/{id}/status-history` - Get complete status audit trail

### Administrative Endpoints

- `GET /admin/orders` - Get all orders across users (admin only)
- `PUT /admin/orders/{id}/status` - Admin-level status updates

### Shipping and Pricing

- `POST /shipping/calculate` - Calculate shipping costs for order
- `GET /shipping/rates` - Get available shipping rate tiers

### Health and Monitoring

- `GET /health` - Basic service health check
- `GET /health/ready` - Comprehensive readiness with dependencies

## Technology Stack

### Core Technologies

- **FastAPI**: High-performance web framework with OpenAPI documentation
- **Python 3.13+**: Latest Python with enhanced performance and typing
- **SQLAlchemy**: Object-relational mapping with declarative models
- **Pydantic**: Data validation and serialization with type safety

### Service Integration

- **httpx**: Async HTTP client for service communication
- **python-jose**: JWT token verification for authentication
- **Auth Service**: Token verification via `GET /auth/verify`
- **Cart Service**: Cart retrieval and clearing operations
- **Product Service**: Product validation and details

### Database and Storage

- **SQLite**: Development and testing environment
- **PostgreSQL**: Production database (configured via DATABASE_URL)
- **Alembic**: Database migration management (planned)

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required | Notes |
|----------|---------|---------|----------|-------|
| `DATABASE_URL` | SQLAlchemy connection | `sqlite:///./order_service.db` | No | PostgreSQL for production |
| `JWT_SECRET_KEY` | JWT verification key | Auto-generated | Recommended | Must match auth service |
| `AUTH_SERVICE_URL` | Auth service endpoint | `http://localhost:8001` | Yes | Token verification |
| `CART_SERVICE_URL` | Cart service endpoint | `http://localhost:8007` | Yes | Cart operations |
| `PRODUCT_SERVICE_URL` | Product catalog URL | `http://localhost:8004` | Yes | Product validation |
| `TAX_RATE` | Tax calculation rate | `0.085` (8.5%) | No | Applied to subtotal |
| `HOST` | Service bind address | `0.0.0.0` | No | Container deployment |
| `PORT` | Service port | `8008` | No | Consistent service mesh |

## Order Lifecycle and Status Management

### Order Status Workflow

```text
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
   ↓          ↓           ↓           ↓         ↓
CANCELLED  CANCELLED  CANCELLED  RETURNED  RETURNED
```

### Status Descriptions

- **PENDING**: Order created, awaiting confirmation
- **CONFIRMED**: Order validated and accepted
- **PROCESSING**: Order being prepared for shipment
- **SHIPPED**: Order dispatched to customer
- **DELIVERED**: Order received by customer
- **CANCELLED**: Order cancelled before shipment
- **RETURNED**: Order returned after delivery

## Shipping Calculation

### Weight-Based Tiers

- **Standard** (0-5 lbs): $5.99
- **Heavy** (5-20 lbs): $9.99
- **Oversized** (20+ lbs): $19.99

### Tax Calculation

- Fixed rate of 8.5% applied to order subtotal
- Configurable via `TAX_RATE` environment variable
- Applied before shipping cost calculation

## Integration Patterns

### Service Dependencies

```text
Order Service ──► Auth Service (/auth/verify)
      │
      ├──────────► Cart Service (/carts/{user_id})
      │
      └──────────► Product Service (/products/{id})
```

### Error Handling

- **503 Service Unavailable**: When dependent services are unreachable
- **401 Unauthorized**: Invalid or expired authentication tokens
- **404 Not Found**: Order or referenced resources not found
- **422 Unprocessable Entity**: Validation errors in order data
- **409 Conflict**: Order state conflicts (e.g., modifying cancelled order)

## Deployment and Operations

### Local Development

```bash
cd services/order-service
uv sync
uv run uvicorn main:app --reload --port 8008
```

### Docker Deployment

```bash
docker build -t order-service:latest services/order-service
docker run -p 8008:8008 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/orderdb" \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  -e CART_SERVICE_URL="http://cart-service:8007" \
  -e PRODUCT_SERVICE_URL="http://product-service:8004" \
  order-service:latest
```

### Health Monitoring

- **Liveness**: Basic service and database connectivity
- **Readiness**: Validates all external service dependencies
- **Dependencies**: Auth, Cart, and Product service availability

## Security Considerations

### Authentication and Authorization

- JWT token validation for all order operations
- Admin-only endpoints for cross-user order management
- User isolation ensuring users can only access their orders

### Data Protection

- Order data encryption at rest (database level)
- Secure handling of customer information
- Audit trails for all order modifications

## Monitoring and Observability

### Logging

- Structured JSON logging for production environments
- Order lifecycle event tracking
- Service integration call logging
- Error and exception tracking with context

### Metrics (Planned)

- Order creation and completion rates
- Order value and volume analytics
- Service dependency health and response times
- Error rates by endpoint and operation type

## Related Documentation

### Service Documentation

- [API Documentation](./api-docs/endpoints.md) - Complete endpoint specifications
- [Status Tracking](./api-docs/status-tracking.md) - Order lifecycle management
- [Architecture Overview](./architecture/overview.md) - Technical architecture
- [Order Lifecycle](./architecture/order-lifecycle.md) - State machine design

### Operational Documentation

- [Order Management SOPs](./operations/order-management.md) - Administrative procedures
- [Integration Guide](./integration/multi-service-integration.md) - Service integration
- [Disaster Recovery](./disaster-recovery/order-data-protection.md) - Data protection
- [Monitoring Setup](./monitoring/order-metrics.md) - Observability configuration

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Service Version**: 1.0.0  
**Documentation Version**: 1.0.0