# Quickstart Guide: Order Processing Service

**Purpose**: End-to-end validation of order processing functionality for Project Zero App
**Audience**: Developers, QA testers, demonstration purposes
**Prerequisites**: Auth service, Cart service, and Product catalog service running

## Service Overview

The Order Processing Service manages the complete e-commerce order lifecycle from cart checkout to delivery, including:

- Order creation from cart contents
- Order status management and tracking
- Customer order history
- Admin order management
- Shipping cost calculations
- Tax calculations

**Port**: 8008
**Base URL**: http://localhost:8008

## Complete E-commerce Flow

The Order Processing Service completes the core e-commerce flow, enabling users to actually buy things! Here's the complete user journey:

### End-to-End User Journey
1. **Browse Products** → Product Catalog Service (port 8004)
2. **Add to Cart** → Cart Service (port 8007)
3. **Login/Register** → Auth Service (port 8001)
4. **Complete Purchase** → **Order Service (port 8008)** ✨
5. **View Order History** → Order Service
6. **Track Order Status** → Order Service

### Order Creation Flow
When a user clicks "Checkout" on their cart page:

1. **Frontend** calls `POST /orders` with shipping address
2. **Order Service** retrieves cart contents from Cart Service (port 8007)
3. **Order Service** validates products with Product Catalog Service (port 8004)
4. **Order Service** calculates totals (subtotal + 8.5% tax + shipping)
5. **Order Service** creates order record with PENDING status
6. **Order Service** clears user's cart via Cart Service
7. **Order Service** returns order confirmation to frontend

### Service Integration Points
- **Auth Service (8001)**: User verification & admin role checks
- **Cart Service (8007)**: Retrieve cart contents & clear after order creation
- **Product Catalog (8004)**: Validate products & get current pricing details

### Why Order Service is Strategic
After implementing the Order Service, Project Zero App will have:
- ✅ **Complete E-commerce Flow** - Users can browse → cart → purchase
- ✅ **End-to-End Testing** - Full customer journey validation
- ✅ **Rich Business Logic** - Order management, status workflows, integrations
- ✅ **Foundation for Extensions** - Payment service, shipping service, notifications
- ✅ **Real-world Complexity** - Multi-service coordination, state management

## Quick Setup

### 1. Start Required Services

Based on the service README files, here are the correct startup commands:

```bash
# Start auth service (Python, port 8001)
cd services/auth-service
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload &

# Start product catalog service (Python, port 8004)
cd services/product-catalog-service
uv sync
uv run uvicorn src.main:app --reload --port 8004 &

# Start cart service (Node.js, port 8007)
cd services/cart-service
yarn install
yarn dev &

# Start order service (Python, port 8008) - TO BE IMPLEMENTED
cd services/order-service
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```

### 2. Verify Service Health

```bash
curl http://localhost:8001/health  # Auth service
curl http://localhost:8004/health  # Product catalog
curl http://localhost:8007/health  # Cart service
curl http://localhost:8008/health  # Order service
```

### 3. View API Documentation

Open the following in your browser:
- Auth Service: http://localhost:8001/docs
- Product Catalog: http://localhost:8004/docs
- Cart Service: No Swagger (Express.js), see README
- Order Service: http://localhost:8008/docs

## User Journey Tests

### Scenario 1: Customer Order Creation

**Story**: A customer converts their cart into an order and tracks it through delivery.

#### Step 1: User Authentication
```bash
# Login to get JWT token
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# Register if user doesn't exist
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# Save the access_token from response
TOKEN="your_jwt_token_here"
```

#### Step 2: Add Items to Cart
```bash
# Cart service uses different endpoint structure - see its README
# Add product to cart (product IDs from catalog service)
curl -X POST http://localhost:8007/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 2,
    "quantity": 2
  }'

# Add another product
curl -X POST http://localhost:8007/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 3,
    "quantity": 1
  }'

# Verify cart contents
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8007/cart
```

#### Step 3: Calculate Shipping Cost
```bash
curl -X POST http://localhost:8008/shipping/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"weight": 0.5, "quantity": 2},
      {"weight": 1.2, "quantity": 1}
    ],
    "address": {
      "recipient_name": "John Doe",
      "address_line_1": "123 Main Street",
      "city": "San Francisco",
      "state_province": "CA",
      "postal_code": "94105",
      "country": "US"
    }
  }'

# Expected: Shipping cost based on weight tiers
```

#### Step 4: Create Order from Cart
```bash
curl -X POST http://localhost:8008/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "recipient_name": "John Doe",
      "address_line_1": "123 Main Street",
      "address_line_2": "Apt 4B",
      "city": "San Francisco",
      "state_province": "CA",
      "postal_code": "94105",
      "country": "US",
      "phone": "+1-555-123-4567"
    },
    "notes": "Please leave at front door"
  }'

# Expected: Order created with PENDING status, cart cleared
# Save order_id from response
ORDER_ID="returned_order_id"
```

#### Step 5: View Order Details
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8008/orders/$ORDER_ID

# Expected: Complete order details with items and shipping address
```

#### Step 6: View Order History
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8008/orders

# Expected: List of user's orders with pagination
```

### Scenario 2: Admin Order Management

**Story**: An admin user manages orders and updates fulfillment status.

#### Step 1: Admin Authentication
```bash
# Login as admin user (user needs admin role in auth service)
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

ADMIN_TOKEN="admin_jwt_token_here"
```

#### Step 2: View All Orders (Admin)
```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8008/admin/orders?limit=10"

# Expected: All orders across all users
```

#### Step 3: Update Order Status
```bash
# Confirm order (payment processed)
curl -X PUT http://localhost:8008/admin/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "CONFIRMED",
    "notes": "Payment processed successfully"
  }'

# Start processing
curl -X PUT http://localhost:8008/admin/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "PROCESSING",
    "notes": "Order picked and being prepared"
  }'

# Mark as shipped
curl -X PUT http://localhost:8008/admin/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "SHIPPED",
    "notes": "Shipped via FedEx, tracking: 1234567890"
  }'
```

#### Step 4: Mark as Delivered
```bash
# Using the main status endpoint (requires admin privileges)
curl -X PUT http://localhost:8008/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DELIVERED",
    "notes": "Delivered to front door as requested"
  }'

# Alternative: Using admin-specific endpoint
curl -X PUT http://localhost:8008/admin/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DELIVERED",
    "notes": "Delivered to front door as requested"
  }'
```

#### Step 5: View Order Status History
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8008/orders/$ORDER_ID/status-history

# Expected: Complete history of status changes with timestamps and notes
# {
#   "order_id": 123,
#   "status_history": [
#     {
#       "status": "PENDING",
#       "timestamp": "2025-09-25T10:00:00Z",
#       "notes": "Order created",
#       "updated_by": "system"
#     },
#     {
#       "status": "CONFIRMED",
#       "timestamp": "2025-09-25T10:05:00Z",
#       "notes": "Payment processed successfully",
#       "updated_by": "admin@example.com"
#     }
#     // ... additional status changes
#   ]
# }
```

### Scenario 3: Order Modifications

**Story**: A customer modifies their order before it's processed.

#### Step 1: Create Order in PENDING Status
```bash
# Follow steps from Scenario 1 to create order
# Order starts in PENDING status
```

#### Step 2: Update Shipping Address (Allowed in PENDING)
```bash
curl -X PATCH http://localhost:8008/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "recipient_name": "John Doe",
      "address_line_1": "456 Oak Avenue",
      "city": "Oakland",
      "state_province": "CA",
      "postal_code": "94601",
      "country": "US",
      "phone": "+1-555-123-4567"
    }
  }'

# Expected: Address updated, modification logged
```

#### Step 3: Try to Modify After Status Change
```bash
# Admin confirms order first
curl -X PUT http://localhost:8008/admin/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "CONFIRMED"}'

# Try to modify items (should fail in CONFIRMED status)
curl -X PATCH http://localhost:8008/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Updated delivery instructions"
  }'

# Expected: Limited modifications allowed for CONFIRMED status
```

#### Step 4: Cancel Order
```bash
curl -X POST http://localhost:8008/orders/$ORDER_ID/cancel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Changed mind, no longer needed"
  }'

# Expected: Order cancelled if status allows
```

## Error Scenarios Testing

### Test Invalid Status Transitions
```bash
# Try to ship a pending order (should fail)
curl -X PUT http://localhost:8008/admin/orders/$ORDER_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "SHIPPED"}'

# Expected: 400 Bad Request - invalid status transition
```

### Test Unauthorized Access
```bash
# Try to access admin endpoint without admin token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8008/admin/orders

# Expected: 403 Forbidden - admin privileges required
```

### Test Order Not Found
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8008/orders/99999

# Expected: 404 Not Found
```

## Expected Results Summary

**Successful Order Flow**:
1. Order created in PENDING status with correct totals
2. Status progresses: PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
3. Order modifications follow status-based rules
4. All changes are audited and logged
5. Customer can view order history
6. Admin can manage all orders

**Validation Points**:
- Tax calculated at 8.5% of subtotal (fixed rate)
- Shipping cost based on weight tiers (configurable flat rate)
- Order total = subtotal + tax + shipping
- Status transitions follow defined workflow
- Authorization enforced for all endpoints
- Cart cleared after order creation (integration with cart service)
- Audit trail maintained for all changes

**Error Handling**:
- Invalid status transitions rejected
- Unauthorized access blocked
- Non-existent orders return 404
- Validation errors return 422
- Service dependencies checked in health endpoints

## Troubleshooting

### Service Won't Start
**Order Service**:
- Check if port 8008 is already in use
- Verify database connection
- Ensure dependencies are installed with `uv sync`

**Cart Service (Node.js)**:
- Check if port 8007 is available
- Run `yarn install` to install dependencies
- Check `AUTH_SERVICE_URL` and `PRODUCT_SERVICE_URL` in environment

**Product Catalog Service**:
- Check if port 8004 is available
- Run `uv sync` to install Python dependencies
- Verify SQLite database permissions

**Auth Service**:
- Check if port 8001 is available
- Run `uv sync` for Python dependencies
- Check JWT secret key configuration

### Orders Not Creating
- Verify auth service is running and JWT is valid
- Check that cart service is accessible and has items
- Confirm product catalog service has products
- Ensure all service URLs are correctly configured

### Status Updates Failing
- Ensure user has admin role in auth service
- Verify status transition is valid according to workflow
- Check order exists and is accessible

### Integration Issues
- Check service-to-service communication
- Verify all services can reach each other
- Check firewall/network configurations
- Validate service URLs in environment variables

This quickstart guide validates all core functionality and demonstrates the complete order lifecycle management capabilities of the service with proper integration to existing Project Zero App services.