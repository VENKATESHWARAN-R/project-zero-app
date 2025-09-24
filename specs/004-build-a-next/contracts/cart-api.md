# Cart API Contract

**Base URL**: `http://localhost:8007`
**Service**: Cart Service
**Version**: v1
**Authentication**: Required (JWT Bearer token)

## Endpoints

### GET /cart
Retrieve current user's cart with all items.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": "cart-uuid-123",
  "user_id": "user-uuid-123",
  "items": [
    {
      "id": "cart-item-uuid-1",
      "product_id": "product-uuid-123",
      "quantity": 2,
      "added_at": "2025-09-24T10:00:00Z",
      "product": {
        "id": "product-uuid-123",
        "name": "Gaming Laptop Pro",
        "price": 149999,
        "currency": "USD",
        "image_url": "https://example.com/images/laptop-pro.jpg",
        "in_stock": true,
        "stock_quantity": 15
      }
    }
  ],
  "total_amount": 299998,
  "item_count": 2,
  "currency": "USD",
  "created_at": "2025-09-24T09:30:00Z",
  "updated_at": "2025-09-24T10:00:00Z"
}
```

**Response (200 OK - Empty Cart)**:
```json
{
  "id": "cart-uuid-123",
  "user_id": "user-uuid-123",
  "items": [],
  "total_amount": 0,
  "item_count": 0,
  "currency": "USD",
  "created_at": "2025-09-24T09:30:00Z",
  "updated_at": "2025-09-24T09:30:00Z"
}
```

### POST /cart/items
Add a product to the cart or update quantity if already exists.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Request**:
```json
{
  "product_id": "product-uuid-123",
  "quantity": 1
}
```

**Response (201 Created)**:
```json
{
  "id": "cart-item-uuid-1",
  "product_id": "product-uuid-123",
  "quantity": 1,
  "added_at": "2025-09-24T10:00:00Z",
  "product": {
    "id": "product-uuid-123",
    "name": "Gaming Laptop Pro",
    "price": 149999,
    "currency": "USD",
    "image_url": "https://example.com/images/laptop-pro.jpg",
    "in_stock": true,
    "stock_quantity": 15
  },
  "cart_summary": {
    "total_amount": 149999,
    "item_count": 1
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid quantity or product not available
- `404 Not Found`: Product not found
- `409 Conflict`: Insufficient stock

### PUT /cart/items/{id}
Update quantity of specific cart item.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Cart item UUID

**Request**:
```json
{
  "quantity": 3
}
```

**Response (200 OK)**:
```json
{
  "id": "cart-item-uuid-1",
  "product_id": "product-uuid-123",
  "quantity": 3,
  "added_at": "2025-09-24T10:00:00Z",
  "product": {
    "id": "product-uuid-123",
    "name": "Gaming Laptop Pro",
    "price": 149999,
    "currency": "USD",
    "image_url": "https://example.com/images/laptop-pro.jpg",
    "in_stock": true,
    "stock_quantity": 15
  },
  "cart_summary": {
    "total_amount": 449997,
    "item_count": 3
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid quantity
- `404 Not Found`: Cart item not found
- `409 Conflict`: Insufficient stock

### DELETE /cart/items/{id}
Remove specific item from cart.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Cart item UUID

**Response (200 OK)**:
```json
{
  "message": "Item removed from cart",
  "removed_item_id": "cart-item-uuid-1",
  "cart_summary": {
    "total_amount": 0,
    "item_count": 0
  }
}
```

**Error Responses**:
- `404 Not Found`: Cart item not found

### DELETE /cart
Clear all items from cart.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "message": "Cart cleared successfully",
  "cart_summary": {
    "total_amount": 0,
    "item_count": 0
  }
}
```

### GET /cart/summary
Get cart summary without full item details (for header display).

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "item_count": 3,
  "total_amount": 449997,
  "currency": "USD",
  "updated_at": "2025-09-24T10:00:00Z"
}
```

### POST /cart/validate
Validate cart items against current product availability and pricing.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "valid": true,
  "items": [
    {
      "cart_item_id": "cart-item-uuid-1",
      "product_id": "product-uuid-123",
      "status": "valid",
      "requested_quantity": 2,
      "available_quantity": 15,
      "current_price": 149999,
      "price_changed": false
    }
  ],
  "total_amount": 299998,
  "issues": []
}
```

**Response (200 OK - With Issues)**:
```json
{
  "valid": false,
  "items": [
    {
      "cart_item_id": "cart-item-uuid-1",
      "product_id": "product-uuid-123",
      "status": "insufficient_stock",
      "requested_quantity": 20,
      "available_quantity": 15,
      "current_price": 149999,
      "price_changed": false
    }
  ],
  "total_amount": 2249985,
  "issues": [
    {
      "type": "insufficient_stock",
      "cart_item_id": "cart-item-uuid-1",
      "message": "Only 15 items available, requested 20"
    }
  ]
}
```

## Bulk Operations

### POST /cart/items/bulk
Add multiple products to cart in single request.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Request**:
```json
{
  "items": [
    {
      "product_id": "product-uuid-123",
      "quantity": 2
    },
    {
      "product_id": "product-uuid-456",
      "quantity": 1
    }
  ]
}
```

**Response (200 OK)**:
```json
{
  "added_items": [
    {
      "id": "cart-item-uuid-1",
      "product_id": "product-uuid-123",
      "quantity": 2,
      "status": "added"
    }
  ],
  "failed_items": [
    {
      "product_id": "product-uuid-456",
      "error": "Product not found"
    }
  ],
  "cart_summary": {
    "total_amount": 299998,
    "item_count": 2
  }
}
```

## Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "additional context"
  }
}
```

## Business Rules
1. Cart items automatically removed when product becomes unavailable
2. Quantities adjusted automatically if stock becomes insufficient
3. Prices updated in real-time during validation
4. Cart expires after 30 days of inactivity
5. Maximum 50 unique items per cart
6. Maximum quantity of 10 per item

## Performance Considerations
- Cart data cached for 5 minutes
- Product availability checked in real-time for critical operations
- Bulk operations processed asynchronously for large quantities
- Cart summary optimized for frequent header display updates