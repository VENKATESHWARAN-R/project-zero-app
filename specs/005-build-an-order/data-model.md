# Data Model: Order Processing Service

**Phase**: 1 - Design & Contracts
**Date**: 2025-09-25
**Status**: Complete

## Overview

This document defines the data entities, relationships, and validation rules for the Order Processing Service based on functional requirements and research findings.

## Core Entities

### 1. Order

**Purpose**: Represents a customer's purchase commitment with complete lifecycle tracking

**Attributes**:
- `id`: Primary key (auto-generated UUID or integer)
- `user_id`: Foreign key to user (from auth service)
- `order_number`: Unique human-readable identifier (e.g., ORD-2025-001234)
- `status`: Order lifecycle status (enum)
- `subtotal`: Sum of all order item totals (decimal, 2 precision)
- `tax_rate`: Applied tax rate at order creation (decimal, 4 precision)
- `tax_amount`: Calculated tax amount (decimal, 2 precision)
- `shipping_cost`: Calculated shipping cost (decimal, 2 precision)
- `total`: Final order total (subtotal + tax + shipping, decimal, 2 precision)
- `currency`: Currency code (default: USD)
- `created_at`: Order creation timestamp
- `updated_at`: Last modification timestamp
- `modification_count`: Number of modifications made (integer, default 0)

**Status Enum Values**:
- `PENDING`: Initial status, payment not processed
- `CONFIRMED`: Payment successful, order confirmed
- `PROCESSING`: Order being prepared for shipment
- `SHIPPED`: Order dispatched to customer
- `DELIVERED`: Order received by customer
- `CANCELLED`: Order cancelled

**Validation Rules**:
- Order number must be unique across system
- Subtotal must be positive
- Tax rate must be between 0 and 1
- Total must equal subtotal + tax_amount + shipping_cost
- Status transitions must follow defined workflow
- User_id must reference valid authenticated user

**Relationships**:
- One-to-many with OrderItem
- One-to-one with ShippingAddress
- One-to-many with OrderModification (audit trail)

### 2. OrderItem

**Purpose**: Individual product entries within an order with pricing snapshots

**Attributes**:
- `id`: Primary key
- `order_id`: Foreign key to Order
- `product_id`: Product identifier (from catalog service)
- `product_name`: Product name snapshot at order time
- `product_sku`: Product SKU snapshot
- `quantity`: Number of units ordered (integer, positive)
- `unit_price`: Price per unit at order time (decimal, 2 precision)
- `total_price`: Quantity * unit_price (decimal, 2 precision)
- `weight`: Item weight for shipping calculation (decimal, 2 precision)
- `created_at`: Item addition timestamp

**Validation Rules**:
- Quantity must be positive integer
- Unit price must be positive
- Total price must equal quantity * unit_price
- Product_id must reference valid product in catalog service
- Weight must be positive for shipping calculations

**Relationships**:
- Many-to-one with Order
- References Product in catalog service (external)

### 3. ShippingAddress

**Purpose**: Customer delivery location with complete contact information

**Attributes**:
- `id`: Primary key
- `order_id`: Foreign key to Order (one-to-one)
- `recipient_name`: Full name of recipient
- `company`: Company name (optional)
- `address_line_1`: Primary address line
- `address_line_2`: Secondary address line (optional)
- `city`: City name
- `state_province`: State or province
- `postal_code`: ZIP or postal code
- `country`: Country code (ISO 3166-1 alpha-2)
- `phone`: Contact phone number (optional)
- `delivery_instructions`: Special delivery notes (optional)
- `created_at`: Address creation timestamp

**Validation Rules**:
- Recipient name is required and non-empty
- Address line 1 is required
- City, state/province, postal code are required
- Country must be valid ISO code
- Phone format validation if provided
- Address validation for deliverability (basic format check)

**Relationships**:
- One-to-one with Order

### 4. OrderModification

**Purpose**: Audit trail for all order changes and status transitions

**Attributes**:
- `id`: Primary key
- `order_id`: Foreign key to Order
- `user_id`: User who made the modification
- `modification_type`: Type of change (enum)
- `old_value`: Previous value (JSON)
- `new_value`: New value (JSON)
- `reason`: Reason for modification (optional)
- `created_at`: Modification timestamp

**Modification Type Enum**:
- `STATUS_CHANGE`: Order status updated
- `ITEM_ADDED`: New item added to order
- `ITEM_REMOVED`: Item removed from order
- `QUANTITY_CHANGED`: Item quantity modified
- `ADDRESS_UPDATED`: Shipping address changed
- `CANCELLATION`: Order cancelled

**Validation Rules**:
- Modification type must be valid enum value
- Old and new values must be valid JSON
- User_id must reference valid user
- Timestamp must be automatically set

**Relationships**:
- Many-to-one with Order
- References User in auth service (external)

## Entity Relationships Diagram

```
Order (1) ←→ (1) ShippingAddress
  ↓
  (1:n)
  ↓
OrderItem

Order (1) ←→ (n) OrderModification

External References:
- Order.user_id → Auth Service User
- OrderItem.product_id → Catalog Service Product
- OrderModification.user_id → Auth Service User
```

## Data Integrity Constraints

### Business Rules
1. **Order Total Consistency**: Order total must always equal sum of item totals + tax + shipping
2. **Status Transition Validity**: Status changes must follow defined workflow
3. **Modification Limits**: Orders can only be modified according to status-based rules
4. **Inventory Consistency**: Order items must reference valid, available products
5. **User Authorization**: Only authenticated users can create/modify their orders
6. **Admin Authorization**: Only admin users can update order status

### Database Constraints
- Foreign key constraints for referential integrity
- Check constraints for positive amounts and quantities
- Unique constraints for order numbers
- Index on user_id for efficient order history queries
- Index on status for admin order filtering
- Index on created_at for chronological sorting

## State Transitions

### Valid Status Transitions
```
PENDING → CONFIRMED (payment successful)
PENDING → CANCELLED (customer/system cancellation)

CONFIRMED → PROCESSING (fulfillment started)
CONFIRMED → CANCELLED (inventory/business issues)

PROCESSING → SHIPPED (order dispatched)
PROCESSING → CANCELLED (fulfillment issues)

SHIPPED → DELIVERED (delivery confirmed)

DELIVERED → [final state]
CANCELLED → [final state]
```

### Transition Rules
- Each transition must be logged in OrderModification
- Invalid transitions must be rejected with appropriate error
- Status changes require appropriate user permissions
- Automatic transitions (e.g., delivery confirmation) must be auditable

## Validation Summary

All entities include comprehensive validation to ensure:
- Data type correctness and format validation
- Business rule compliance
- Referential integrity with external services
- Audit trail completeness
- Security and authorization requirements

This data model supports all functional requirements while maintaining simplicity appropriate for the demonstration platform scope.