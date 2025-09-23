# Data Model: Shopping Cart Service

**Date**: 2025-09-23
**Feature**: Shopping Cart Service
**Status**: Phase 1 Design

## Entity Definitions

### Cart Entity
**Purpose**: Represents a user's shopping session

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Auto-generated | Unique cart identifier |
| user_id | String | Required, Index | User ID from auth service |
| created_at | DateTime | Auto-generated | Cart creation timestamp |
| updated_at | DateTime | Auto-updated | Last modification timestamp |

**Sequelize Model Definition**:
```javascript
Cart = {
  id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
  user_id: { type: DataTypes.STRING, allowNull: false, index: true },
  created_at: { type: DataTypes.DATE, defaultValue: DataTypes.NOW },
  updated_at: { type: DataTypes.DATE, defaultValue: DataTypes.NOW }
}
```

**Business Rules**:
- One active cart per user
- Cart expires after 24 hours of inactivity (configurable)
- Soft delete for audit purposes

### CartItem Entity
**Purpose**: Individual product entries within a cart

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Auto-generated | Unique item identifier |
| cart_id | UUID | Foreign Key, Required | Reference to Cart.id |
| product_id | String | Required, Index | Product ID from catalog service |
| quantity | Integer | Required, Min: 1, Max: 10 | Item quantity |
| created_at | DateTime | Auto-generated | Item addition timestamp |
| updated_at | DateTime | Auto-updated | Last modification timestamp |

**Sequelize Model Definition**:
```javascript
CartItem = {
  id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
  cart_id: { type: DataTypes.UUID, allowNull: false, references: { model: 'Cart', key: 'id' } },
  product_id: { type: DataTypes.STRING, allowNull: false, index: true },
  quantity: { type: DataTypes.INTEGER, allowNull: false, validate: { min: 1, max: 10 } },
  created_at: { type: DataTypes.DATE, defaultValue: DataTypes.NOW },
  updated_at: { type: DataTypes.DATE, defaultValue: DataTypes.NOW }
}
```

**Business Rules**:
- Unique constraint on (cart_id, product_id) - no duplicates
- Quantity must be positive integer
- Maximum quantity per item: 10 (configurable)
- Cascade delete when cart is deleted

## Relationships

### Cart ↔ CartItem
- **Type**: One-to-Many
- **Relationship**: Cart.hasMany(CartItem), CartItem.belongsTo(Cart)
- **Foreign Key**: CartItem.cart_id → Cart.id
- **Cascade**: DELETE CASCADE

### External Entity References

### User (Auth Service)
- **Reference**: Cart.user_id → Auth Service User.id
- **Validation**: Verify user exists via auth service
- **Constraints**: Required for all cart operations

### Product (Catalog Service)
- **Reference**: CartItem.product_id → Product Service Product.id
- **Validation**: Verify product exists and is available
- **Constraints**: Required before adding to cart

## Validation Rules

### Cart Validation
- `user_id`: Required, must be valid user from auth service
- `created_at`/`updated_at`: Auto-managed by Sequelize

### CartItem Validation
- `cart_id`: Required, must reference existing cart
- `product_id`: Required, must exist in product catalog
- `quantity`: Required, integer between 1 and 10
- Unique combination of (cart_id, product_id)

### Business Logic Validation
- Cart cannot exceed 50 total items across all products
- Product must be available (not discontinued)
- User must be authenticated for all operations

## State Transitions

### Cart Lifecycle
```
Created → Active → [Expired/Cleared] → Archived
```

**States**:
- **Created**: New cart with no items
- **Active**: Cart with one or more items
- **Expired**: Cart inactive for 24+ hours
- **Archived**: Soft-deleted cart (for audit)

### CartItem Lifecycle
```
Added → Updated → Removed
```

**Operations**:
- **Added**: New item added to cart
- **Updated**: Quantity modified
- **Removed**: Item deleted from cart

## Database Indexes

### Performance Indexes
- `Cart.user_id` - Fast cart lookup by user
- `CartItem.cart_id` - Fast item retrieval for cart
- `CartItem.product_id` - Product-based queries
- `Cart.updated_at` - Expiration cleanup queries

### Unique Constraints
- `CartItem(cart_id, product_id)` - Prevent duplicate items

## Migration Strategy

### Initial Schema
```sql
-- Cart table
CREATE TABLE Cart (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cart_user_id ON Cart(user_id);
CREATE INDEX idx_cart_updated_at ON Cart(updated_at);

-- CartItem table
CREATE TABLE CartItem (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_id UUID NOT NULL REFERENCES Cart(id) ON DELETE CASCADE,
  product_id VARCHAR(255) NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity >= 1 AND quantity <= 10),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cartitem_cart_id ON CartItem(cart_id);
CREATE INDEX idx_cartitem_product_id ON CartItem(product_id);
CREATE UNIQUE INDEX idx_cartitem_unique ON CartItem(cart_id, product_id);
```

## Data Flow Patterns

### Add Item Flow
1. Validate user authentication
2. Validate product exists in catalog
3. Find or create user's cart
4. Check if item already exists
5. If exists: update quantity (within limits)
6. If new: create cart item
7. Update cart timestamp

### Get Cart Flow
1. Validate user authentication
2. Find user's active cart
3. Retrieve all cart items
4. Enrich with product details from catalog
5. Calculate totals and return

### Remove Item Flow
1. Validate user authentication
2. Find cart item by cart_id and product_id
3. Delete cart item
4. Update cart timestamp
5. If cart empty, mark as expired

This data model supports all functional requirements while maintaining referential integrity and performance through proper indexing.