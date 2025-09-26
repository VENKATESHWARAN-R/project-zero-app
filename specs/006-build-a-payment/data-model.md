# Data Model: Payment Processing Service

**Feature**: Payment Processing Service  
**Date**: 2025-09-27  
**Phase**: 1 - Design & Contracts

## Entity Definitions

### Payment Transaction

**Purpose**: Represents a single payment attempt with complete transaction lifecycle tracking

**Attributes**:
- `id` (UUID, Primary Key): Unique transaction identifier
- `order_id` (UUID, Foreign Key): Reference to order being paid for
- `user_id` (UUID, Foreign Key): Reference to user making payment
- `payment_method_id` (UUID, Foreign Key): Reference to payment method used
- `amount` (Decimal): Payment amount in cents to avoid floating point issues
- `currency` (String): Currency code (default: USD)
- `status` (Enum): Current payment status
- `gateway_transaction_id` (String): Mock gateway transaction reference
- `failure_reason` (String, Optional): Reason for payment failure
- `created_at` (DateTime): Transaction creation timestamp
- `updated_at` (DateTime): Last status update timestamp
- `processed_at` (DateTime, Optional): Payment processing completion timestamp

**Status Values**:
- `PENDING`: Payment initiated but not yet processed
- `PROCESSING`: Payment being processed by gateway
- `COMPLETED`: Payment successfully completed
- `FAILED`: Payment failed during processing
- `CANCELLED`: Payment cancelled by user or system
- `REFUNDED`: Payment refunded (future enhancement)

**Relationships**:
- Belongs to one Order (via order_id)
- Belongs to one User (via user_id)
- Uses one Payment Method (via payment_method_id)
- Has many Payment Status History entries

**Validation Rules**:
- Amount must be positive and greater than 0
- Currency must be valid ISO 4217 code
- Status transitions must follow valid state machine
- Order ID must exist in order service
- User ID must exist in auth service

### Payment Method

**Purpose**: Stores user payment method information (securely masked for demo)

**Attributes**:
- `id` (UUID, Primary Key): Unique payment method identifier
- `user_id` (UUID, Foreign Key): Reference to method owner
- `type` (Enum): Payment method type
- `display_name` (String): User-friendly name for method
- `masked_details` (JSON): Masked payment details for display
- `is_default` (Boolean): Whether this is user's default method
- `is_active` (Boolean): Whether method is available for use
- `expires_at` (DateTime, Optional): Expiration date for cards
- `created_at` (DateTime): Method creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Payment Method Types**:
- `CREDIT_CARD`: Credit card payment
- `DEBIT_CARD`: Debit card payment
- `PAYPAL`: PayPal account payment

**Masked Details Structure**:
```json
{
  "credit_card": {
    "last_four": "1234",
    "brand": "visa",
    "exp_month": 12,
    "exp_year": 2025
  },
  "paypal": {
    "email": "user@example.com"
  }
}
```

**Relationships**:
- Belongs to one User (via user_id)
- Has many Payment Transactions

**Validation Rules**:
- User can have multiple payment methods
- Only one default method per user per type
- Masked details must match payment method type
- Expired methods cannot be used for new payments

### Payment Status History

**Purpose**: Audit trail of all payment status changes for compliance and debugging

**Attributes**:
- `id` (UUID, Primary Key): Unique history entry identifier
- `payment_id` (UUID, Foreign Key): Reference to payment transaction
- `previous_status` (Enum): Status before change
- `new_status` (Enum): Status after change
- `reason` (String, Optional): Reason for status change
- `metadata` (JSON, Optional): Additional context data
- `created_at` (DateTime): Status change timestamp
- `created_by` (String): System or user that triggered change

**Relationships**:
- Belongs to one Payment Transaction (via payment_id)

**Validation Rules**:
- Status changes must be valid transitions
- Cannot delete history entries (append-only)
- Metadata must be valid JSON

### Webhook Event

**Purpose**: Tracks simulated webhook notifications for payment status updates

**Attributes**:
- `id` (UUID, Primary Key): Unique webhook event identifier
- `payment_id` (UUID, Foreign Key): Reference to related payment
- `event_type` (Enum): Type of webhook event
- `payload` (JSON): Webhook payload data
- `endpoint_url` (String): Target webhook URL
- `status` (Enum): Delivery status
- `attempts` (Integer): Number of delivery attempts
- `last_attempt_at` (DateTime, Optional): Last delivery attempt timestamp
- `next_retry_at` (DateTime, Optional): Next retry attempt timestamp
- `created_at` (DateTime): Event creation timestamp

**Event Types**:
- `PAYMENT_INITIATED`: Payment processing started
- `PAYMENT_COMPLETED`: Payment successfully completed
- `PAYMENT_FAILED`: Payment processing failed
- `PAYMENT_CANCELLED`: Payment was cancelled

**Delivery Status**:
- `PENDING`: Waiting to be delivered
- `DELIVERED`: Successfully delivered
- `FAILED`: Delivery failed after retries
- `CANCELLED`: Delivery cancelled

**Relationships**:
- Belongs to one Payment Transaction (via payment_id)

## State Transitions

### Payment Status State Machine

```
PENDING → PROCESSING → COMPLETED
    ↓         ↓           ↓
CANCELLED ← FAILED ← REFUNDED
```

**Valid Transitions**:
- `PENDING` → `PROCESSING`: Payment processing started
- `PENDING` → `CANCELLED`: Payment cancelled before processing
- `PROCESSING` → `COMPLETED`: Payment successfully processed
- `PROCESSING` → `FAILED`: Payment processing failed
- `COMPLETED` → `REFUNDED`: Payment refunded (future)
- `FAILED` → `PROCESSING`: Retry payment processing

**Invalid Transitions**:
- Cannot go from `COMPLETED` to `PENDING`
- Cannot go from `CANCELLED` to any other status
- Cannot skip `PROCESSING` when going from `PENDING` to `COMPLETED`

## Data Relationships

### Primary Relationships

```
User (Auth Service)
  ↓ 1:N
Payment Method
  ↓ 1:N
Payment Transaction ← N:1 → Order (Order Service)
  ↓ 1:N
Payment Status History

Payment Transaction
  ↓ 1:N
Webhook Event
```

### Cross-Service References

**Auth Service Integration**:
- `user_id` fields reference users in auth service
- JWT tokens provide user context for API calls
- User validation required before payment processing

**Order Service Integration**:
- `order_id` fields reference orders in order service
- Order status updated after payment completion
- Order validation required before payment processing

## Indexing Strategy

### Primary Indexes

- `payment_transactions.id` (Primary Key)
- `payment_methods.id` (Primary Key)
- `payment_status_history.id` (Primary Key)
- `webhook_events.id` (Primary Key)

### Secondary Indexes

- `payment_transactions.order_id` (Foreign Key, frequent lookups)
- `payment_transactions.user_id` (Foreign Key, user payment history)
- `payment_transactions.status` (Status filtering)
- `payment_transactions.created_at` (Time-based queries)
- `payment_methods.user_id` (User's payment methods)
- `payment_methods.is_default` (Default method lookup)
- `payment_status_history.payment_id` (Payment audit trail)
- `webhook_events.payment_id` (Payment webhook tracking)
- `webhook_events.status` (Webhook delivery monitoring)

## Data Validation

### Business Rules

1. **Payment Amount**: Must be positive, non-zero, and within reasonable limits
2. **Currency Support**: Initially USD only, extensible for future currencies
3. **Payment Method Limits**: Users can have up to 5 active payment methods
4. **Transaction Limits**: Daily payment limit per user (configurable)
5. **Duplicate Prevention**: Same order cannot have multiple successful payments

### Data Integrity

1. **Foreign Key Constraints**: All references must be valid
2. **Status Consistency**: Payment status must follow state machine rules
3. **Audit Trail**: All status changes must be recorded in history
4. **Timestamp Consistency**: Updated timestamps must be >= created timestamps

### Security Considerations

1. **Data Masking**: All sensitive payment data must be masked in storage
2. **Audit Logging**: All data access and modifications must be logged
3. **Data Retention**: Payment data retention policy compliance
4. **Access Control**: Role-based access to payment data

## Migration Strategy

### Initial Schema Creation

1. Create base tables with proper constraints
2. Set up indexes for performance
3. Create database triggers for audit trail
4. Seed test data for development

### Future Enhancements

1. **Refund Support**: Add refund-related fields and status
2. **Multi-Currency**: Extend currency support and conversion
3. **Payment Plans**: Support for installment payments
4. **Fraud Detection**: Add fraud scoring and prevention fields

This data model provides a solid foundation for the payment processing service while maintaining flexibility for future enhancements and ensuring data integrity throughout the payment lifecycle.
