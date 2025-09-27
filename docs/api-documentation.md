# Project Zero App - API Documentation

## Overview

Project Zero App is a comprehensive e-commerce platform built with a microservices architecture. This document provides detailed information about all backend services and their APIs.

## Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Redis       │    │   PostgreSQL    │
│   (Next.js)     │    │   (Sessions)    │    │   (Production)  │
│   Port 3000     │    │   Port 6379     │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                           │                            │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │ Product Service │    │  Cart Service   │
│    Port 8001    │    │    Port 8004    │    │   Port 8007     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Order Service  │    │ Payment Service │    │   Future APIs   │
│   Port 8008     │    │   Port 8009     │    │      ...        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Services Overview

| Service | Port | Technology | Purpose | Status |
|---------|------|------------|---------|--------|
| [Auth Service](#auth-service) | 8001 | FastAPI + SQLite | User authentication & JWT management | ✅ Active |
| [Product Service](#product-catalog-service) | 8004 | FastAPI + SQLite | Product catalog & inventory | ✅ Active |
| [Cart Service](#cart-service) | 8007 | Node.js + SQLite | Shopping cart management | ✅ Active |
| [Order Service](#order-service) | 8008 | FastAPI + SQLite | Order processing & management | ✅ Active |
| [Payment Service](#payment-service) | 8009 | FastAPI + SQLite | Payment processing (mock) | ✅ Active |
| Frontend | 3000 | Next.js + TypeScript | Web application UI | ✅ Active |

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.13+ (for local development)

### Start All Services
```bash
# Clone the repository
git clone <repository-url>
cd project-zero-app

# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker ps

# View logs for specific service
docker-compose logs <service-name>
```

### Health Checks
```bash
# Check all services
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8004/health  # Product Service
curl http://localhost:8007/health  # Cart Service
curl http://localhost:8008/health  # Order Service
curl http://localhost:8009/health  # Payment Service
```

---

## Auth Service

**Port**: 8001  
**Technology**: FastAPI + SQLite  
**Purpose**: User authentication, registration, and JWT token management

### API Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login (returns JWT tokens)
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/verify` - Verify JWT token

#### Health & Status
- `GET /health` - Service health check
- `GET /` - Service information

### Example Usage

```bash
# Register a new user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Authentication Flow
1. User registers with email/password
2. User logs in to receive JWT access and refresh tokens
3. Access token used for authenticated requests (15 min expiry)
4. Refresh token used to get new access tokens (7 days expiry)

---

## Product Catalog Service

**Port**: 8004  
**Technology**: FastAPI + SQLite  
**Purpose**: Product catalog, inventory management, and search

### API Endpoints

#### Products
- `GET /api/v1/products` - List products with filtering and pagination
- `GET /api/v1/products/{product_id}` - Get product details
- `POST /api/v1/products` - Create new product (admin)
- `PUT /api/v1/products/{product_id}` - Update product (admin)
- `DELETE /api/v1/products/{product_id}` - Delete product (admin)

#### Categories
- `GET /api/v1/categories` - List product categories
- `GET /api/v1/categories/{category_id}` - Get category details

#### Search & Filtering
- `GET /api/v1/products/search` - Search products by name/description
- `GET /api/v1/products/category/{category_id}` - Products by category

#### Health & Status
- `GET /health` - Service health check

### Example Usage

```bash
# Get all products
curl http://localhost:8004/api/v1/products

# Search products
curl "http://localhost:8004/api/v1/products/search?q=laptop"

# Get product details
curl http://localhost:8004/api/v1/products/{product_id}
```

---

## Cart Service

**Port**: 8007  
**Technology**: Node.js + Express + SQLite  
**Purpose**: Shopping cart management and session handling

### API Endpoints

#### Cart Management
- `GET /api/v1/cart` - Get user's cart
- `POST /api/v1/cart/items` - Add item to cart
- `PUT /api/v1/cart/items/{item_id}` - Update cart item quantity
- `DELETE /api/v1/cart/items/{item_id}` - Remove item from cart
- `DELETE /api/v1/cart` - Clear entire cart

#### Cart Operations
- `POST /api/v1/cart/merge` - Merge guest cart with user cart
- `GET /api/v1/cart/summary` - Get cart summary (total, count, etc.)

#### Health & Status
- `GET /health` - Service health check

### Example Usage

```bash
# Get cart (requires JWT token)
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:8007/api/v1/cart

# Add item to cart
curl -X POST http://localhost:8007/api/v1/cart/items \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "product-uuid",
    "quantity": 2
  }'
```

---

## Order Service

**Port**: 8008  
**Technology**: FastAPI + SQLite  
**Purpose**: Order processing, status management, and order history

### API Endpoints

#### Order Management
- `POST /orders/` - Create new order
- `GET /orders/` - Get user's orders
- `GET /orders/{order_id}` - Get order details
- `PUT /orders/{order_id}/cancel` - Cancel order
- `GET /orders/{order_id}/status` - Get order status
- `GET /orders/{order_id}/status-history` - Get order status history

#### Admin Operations
- `GET /admin/orders` - Get all orders (admin)
- `PUT /admin/orders/{order_id}/status` - Update order status (admin)

#### Shipping
- `POST /shipping/calculate` - Calculate shipping costs
- `GET /shipping/rates` - Get available shipping rates

#### Health & Status
- `GET /health` - Service health check
- `GET /health/ready` - Service readiness check

### Example Usage

```bash
# Create order
curl -X POST http://localhost:8008/orders/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "product_id": "product-uuid",
        "quantity": 2,
        "price": 2999
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "country": "US"
    }
  }'

# Get order status
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:8008/orders/{order_id}/status
```

---

## Payment Service

**Port**: 8009  
**Technology**: FastAPI + SQLite  
**Purpose**: Mock payment processing with realistic simulation

### API Endpoints

#### Payment Processing
- `POST /api/v1/payments` - Process payment
- `GET /api/v1/payments` - Get payment history
- `GET /api/v1/payments/{payment_id}` - Get payment details
- `GET /api/v1/payments/{payment_id}/status` - Get payment status

#### Payment Methods
- `POST /api/v1/payment-methods` - Add payment method
- `GET /api/v1/payment-methods` - Get user's payment methods
- `DELETE /api/v1/payment-methods/{method_id}` - Remove payment method

#### Webhooks
- `POST /api/v1/webhooks/payment` - Payment webhook (no auth)
- `POST /api/v1/webhooks/test` - Test webhook endpoint
- `GET /api/v1/webhooks/events/{payment_id}` - Get webhook events

#### Health & Status
- `GET /health` - Service health check
- `GET /health/ready` - Service readiness check

### Payment Simulation Features

- **Success Rate**: 95% configurable success rate
- **Processing Delays**: 1-3 seconds realistic delays
- **Failure Scenarios**: 
  - Insufficient funds (amount ending in 01)
  - Card declined (amount ending in 02)
  - Network error (amount ending in 03)
  - Invalid method (amount ending in 04)

### Example Usage

```bash
# Add payment method
curl -X POST http://localhost:8009/api/v1/payment-methods \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CREDIT_CARD",
    "display_name": "My Visa Card",
    "payment_details": {
      "card_number": "4111111111111111",
      "exp_month": 12,
      "exp_year": 2025,
      "cvv": "123",
      "cardholder_name": "John Doe"
    },
    "is_default": true
  }'

# Process payment
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order-uuid",
    "payment_method_id": "method-uuid",
    "amount": 5000,
    "currency": "USD"
  }'
```

---

## Authentication & Security

### JWT Token Usage

All services (except health endpoints and webhooks) require JWT authentication:

```bash
# Include in request headers
Authorization: Bearer <jwt_token>
```

### Token Lifecycle
1. **Access Token**: 15 minutes expiry, used for API requests
2. **Refresh Token**: 7 days expiry, used to get new access tokens

### Security Features
- Password validation (uppercase, lowercase, numbers, special chars)
- JWT token validation across all services
- Input sanitization and validation
- Rate limiting (configurable)
- HTTPS enforcement in production

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": {
    "error": "error_type",
    "code": "error_code",
    "message": "Human readable error message",
    "timestamp": "2025-09-27T13:00:00Z"
  }
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `422` - Unprocessable Entity (validation errors)
- `500` - Internal Server Error

---

## Development & Testing

### Local Development Setup

```bash
# Start individual service for development
cd services/<service-name>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port <port>
```

### API Testing

```bash
# Test complete e-commerce flow
# 1. Register user
# 2. Login to get token
# 3. Browse products
# 4. Add to cart
# 5. Create order
# 6. Process payment

# See individual service documentation for detailed examples
```

### Swagger Documentation

Each service provides interactive API documentation:

- Auth Service: http://localhost:8001/docs
- Product Service: http://localhost:8004/docs
- Cart Service: http://localhost:8007/docs (if available)
- Order Service: http://localhost:8008/docs
- Payment Service: http://localhost:8009/docs

---

## Monitoring & Observability

### Health Checks
All services provide health check endpoints for monitoring:

```bash
# Basic health check
curl http://localhost:<port>/health

# Detailed readiness check (where available)
curl http://localhost:<port>/health/ready
```

### Logging
- Structured JSON logging across all services
- Correlation IDs for request tracing
- Configurable log levels (DEBUG, INFO, WARN, ERROR)

### Metrics
- Response time monitoring
- Error rate tracking
- Request volume metrics
- Database connection health

---

## Production Deployment

### Environment Configuration
- Use PostgreSQL for production databases
- Configure proper JWT secrets
- Set up SSL/TLS certificates
- Configure log aggregation
- Set up monitoring and alerting

### Scaling Considerations
- Horizontal scaling with load balancers
- Database connection pooling
- Caching for frequently accessed data
- Async processing for background tasks

---

## Support & Documentation

### Additional Resources
- **Architecture Docs**: `/docs/architecture/`
- **Deployment Guide**: `/docs/deployment/`
- **API Collections**: Postman/Insomnia collections available
- **Troubleshooting**: `/docs/troubleshooting.md`

### Getting Help
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check service-specific READMEs

---

**Last Updated**: 2025-09-27  
**API Version**: 1.0.0  
**Project**: Project Zero App
