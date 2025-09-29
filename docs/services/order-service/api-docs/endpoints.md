# Order Service API Documentation

**Service**: Order Service  
**Base URL**: `http://localhost:8008` (Development)  
**API Gateway Path**: `/api/orders/*`  
**Version**: 1.0.0  
**Last Updated**: 2025-09-29

## Overview

The Order Service provides comprehensive order lifecycle management for the Project Zero App e-commerce platform. It handles order creation from cart checkout, tax and shipping calculations, status tracking, and integrates with authentication, cart, and product catalog services.

## Authentication

All endpoints require JWT authentication except health checks. Include the access token in the Authorization header.

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Base URLs

| Environment | Base URL | Notes |
|-------------|----------|-------|
| Development | `http://localhost:8008` | Local development |
| Production | `https://api.projectzero.com/orders` | Production environment |
| API Gateway | `/api/orders/*` | Proxied through gateway |

## Order Management Endpoints

### POST /orders

Create a new order from the user's cart.

**Request Body:**
```json
{
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  },
  "billing_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "order_12345",
  "user_id": "user123",
  "status": "PENDING",
  "items": [
    {
      "product_id": 1,
      "name": "Laptop",
      "quantity": 1,
      "price": 999.99,
      "weight": 5.0
    }
  ],
  "subtotal": 999.99,
  "tax": 84.99,
  "shipping_cost": 9.99,
  "total": 1094.97,
  "shipping_address": {...},
  "billing_address": {...},
  "created_at": "2025-09-29T10:00:00Z"
}
```

---

### GET /orders

Get user's order history with optional filtering.

**Query Parameters:**
- `status`: Filter by order status
- `limit`: Number of orders to return (default: 20)
- `offset`: Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": "order_12345",
      "status": "SHIPPED",
      "total": 1094.97,
      "created_at": "2025-09-29T10:00:00Z",
      "updated_at": "2025-09-29T14:00:00Z"
    }
  ],
  "total_count": 1,
  "limit": 20,
  "offset": 0
}
```

---

### GET /orders/{id}

Get detailed information for a specific order.

**Response (200 OK):**
```json
{
  "id": "order_12345",
  "user_id": "user123",
  "status": "SHIPPED",
  "items": [...],
  "subtotal": 999.99,
  "tax": 84.99,
  "shipping_cost": 9.99,
  "total": 1094.97,
  "shipping_address": {...},
  "billing_address": {...},
  "tracking_number": "1Z999AA1234567890",
  "created_at": "2025-09-29T10:00:00Z",
  "updated_at": "2025-09-29T14:00:00Z"
}
```

---

### PATCH /orders/{id}

Modify an existing order (limited by status).

**Request Body:**
```json
{
  "shipping_address": {
    "address_line_1": "456 New St",
    "city": "Newtown"
  }
}
```

**Response (200 OK):**
```json
{
  "id": "order_12345",
  "status": "PENDING",
  "updated_at": "2025-09-29T10:30:00Z",
  "message": "Order updated successfully"
}
```

---

### POST /orders/{id}/cancel

Cancel an order.

**Response (200 OK):**
```json
{
  "id": "order_12345",
  "status": "CANCELLED",
  "cancelled_at": "2025-09-29T10:30:00Z",
  "message": "Order cancelled successfully"
}
```

## Order Status Management

### PUT /orders/{id}/status

Update order status (admin only).

**Request Body:**
```json
{
  "status": "PROCESSING",
  "notes": "Order being prepared for shipment"
}
```

**Response (200 OK):**
```json
{
  "id": "order_12345",
  "status": "PROCESSING",
  "status_updated_at": "2025-09-29T11:00:00Z",
  "notes": "Order being prepared for shipment"
}
```

---

### GET /orders/{id}/status-history

Get complete status history for an order.

**Response (200 OK):**
```json
{
  "order_id": "order_12345",
  "status_history": [
    {
      "status": "PENDING",
      "timestamp": "2025-09-29T10:00:00Z",
      "notes": "Order created"
    },
    {
      "status": "CONFIRMED",
      "timestamp": "2025-09-29T10:15:00Z",
      "notes": "Payment confirmed"
    },
    {
      "status": "PROCESSING",
      "timestamp": "2025-09-29T11:00:00Z",
      "notes": "Order being prepared for shipment"
    }
  ]
}
```

## Administrative Endpoints

### GET /admin/orders

Get all orders across users (admin only).

**Query Parameters:**
- `status`: Filter by status
- `user_id`: Filter by user
- `limit`: Number of orders (default: 50)
- `offset`: Pagination offset

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": "order_12345",
      "user_id": "user123",
      "status": "SHIPPED",
      "total": 1094.97,
      "created_at": "2025-09-29T10:00:00Z"
    }
  ],
  "total_count": 150,
  "limit": 50,
  "offset": 0
}
```

---

### PUT /admin/orders/{id}/status

Admin-level status updates with enhanced privileges.

**Request Body:**
```json
{
  "status": "DELIVERED",
  "notes": "Package delivered to front door",
  "tracking_number": "1Z999AA1234567890"
}
```

## Shipping and Pricing

### POST /shipping/calculate

Calculate shipping cost for order items.

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 1,
      "weight": 5.0
    }
  ],
  "shipping_address": {
    "country": "US",
    "state": "CA",
    "postal_code": "12345"
  }
}
```

**Response (200 OK):**
```json
{
  "shipping_cost": 9.99,
  "shipping_method": "STANDARD",
  "estimated_delivery": "2025-10-03T00:00:00Z",
  "calculation_details": {
    "base_rate": 5.99,
    "weight_surcharge": 4.00,
    "total_weight": 5.0
  }
}
```

---

### GET /shipping/rates

Get available shipping rates and methods.

**Response (200 OK):**
```json
{
  "rates": [
    {
      "method": "STANDARD",
      "cost": 5.99,
      "weight_limit": 5.0,
      "estimated_days": 5
    },
    {
      "method": "EXPEDITED",
      "cost": 9.99,
      "weight_limit": 20.0,
      "estimated_days": 3
    },
    {
      "method": "OVERNIGHT",
      "cost": 19.99,
      "weight_limit": 20.0,
      "estimated_days": 1
    }
  ]
}
```

## Order Status Workflow

The order follows a defined status workflow:

```text
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
   ↓          ↓           ↓           ↓         ↓
CANCELLED  CANCELLED  CANCELLED  RETURNED  RETURNED
```

### Status Descriptions

- **PENDING**: Order created, awaiting payment confirmation
- **CONFIRMED**: Payment verified, order accepted
- **PROCESSING**: Order being prepared for shipment
- **SHIPPED**: Order dispatched to customer
- **DELIVERED**: Order received by customer
- **CANCELLED**: Order cancelled before shipment
- **RETURNED**: Order returned after delivery

## Tax and Pricing

### Tax Calculation

- Fixed rate of 8.5% applied to order subtotal
- Configurable via service environment variables
- Applied before shipping cost calculation

### Shipping Calculation

Weight-based pricing tiers:
- **0-5 lbs**: $5.99 (Standard)
- **5-20 lbs**: $9.99 (Heavy)
- **20+ lbs**: $19.99 (Oversized)

## Health and Monitoring

### GET /health

Basic service health check.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-29T10:00:00Z",
  "service": "order-service",
  "version": "1.0.0"
}
```

---

### GET /health/ready

Comprehensive readiness check with dependencies.

**Response (200 OK):**
```json
{
  "status": "ready",
  "timestamp": "2025-09-29T10:00:00Z",
  "dependencies": {
    "auth_service": "healthy",
    "cart_service": "healthy",
    "product_service": "healthy",
    "database": "connected"
  }
}
```

## Error Handling

### Common Error Responses

- `400 Bad Request`: Invalid request format or parameters
- `401 Unauthorized`: Invalid or expired JWT token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Order not found
- `409 Conflict`: Order state conflict (e.g., modifying cancelled order)
- `422 Unprocessable Entity`: Validation errors
- `503 Service Unavailable`: External service failure

### Example Error Response

```json
{
  "error": "Order cannot be modified",
  "error_code": "ORDER_STATE_CONFLICT",
  "details": "Order is already shipped and cannot be cancelled",
  "timestamp": "2025-09-29T10:00:00Z"
}
```

## Testing Examples

### cURL Examples

**Create Order:**
```bash
curl -X POST http://localhost:8008/orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "first_name": "John",
      "last_name": "Doe",
      "address_line_1": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "postal_code": "12345",
      "country": "US"
    }
  }'
```

**Get Orders:**
```bash
curl -X GET "http://localhost:8008/orders?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Related Documentation

- [Order Lifecycle](../architecture/order-lifecycle.md) - State machine design
- [Service Integration](../integration/multi-service-integration.md) - Service dependencies
- [Architecture Overview](../architecture/overview.md) - Technical architecture
- [Monitoring Guide](../monitoring/order-metrics.md) - Observability setup

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**API Version**: 1.0.0