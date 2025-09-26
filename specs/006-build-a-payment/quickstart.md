# Quickstart: Payment Processing Service

**Feature**: Payment Processing Service  
**Date**: 2025-09-27  
**Phase**: 1 - Design & Contracts

## Overview

This quickstart guide provides step-by-step instructions to set up, run, and test the Payment Processing Service for the Project Zero App e-commerce platform.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Auth Service running on port 8001
- Order Service running on port 8008
- Valid JWT token from Auth Service

## Quick Setup

### 1. Clone and Navigate

```bash
cd /path/to/project-zero-app
git checkout 006-build-a-payment
cd services/payment-service
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `.env` file:

```env
# Service Configuration
PORT=8009
HOST=0.0.0.0
DEBUG=true

# Database Configuration
DATABASE_URL=sqlite:///./payment_service.db

# External Services
AUTH_SERVICE_URL=http://localhost:8001
ORDER_SERVICE_URL=http://localhost:8008

# Payment Configuration
PAYMENT_SUCCESS_RATE=0.95
PAYMENT_PROCESSING_DELAY_MIN=1000
PAYMENT_PROCESSING_DELAY_MAX=3000
PAYMENT_FAILURE_SCENARIOS=true
WEBHOOK_SIMULATION_ENABLED=true
WEBHOOK_DELAY_MIN=500
WEBHOOK_DELAY_MAX=2000

# Security
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 4. Database Setup

```bash
# Initialize database
python -m src.models.database init

# Run migrations (if any)
python -m src.models.database migrate

# Seed test data
python -m src.models.database seed
```

### 5. Start the Service

```bash
# Development mode
uvicorn src.main:app --host 0.0.0.0 --port 8009 --reload

# Or using Docker
docker-compose up --build
```

## Service Verification

### 1. Health Check

```bash
# Check service health
curl http://localhost:8009/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-09-27T00:00:00Z",
  "version": "1.0.0",
  "uptime": 123.45
}
```

### 2. Readiness Check

```bash
# Check service readiness
curl http://localhost:8009/health/ready

# Expected response:
{
  "ready": true,
  "checks": {
    "database": "ready",
    "auth_service": "ready",
    "order_service": "ready"
  }
}
```

## API Testing

### 1. Get JWT Token

First, obtain a JWT token from the Auth Service:

```bash
# Login to get JWT token
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'

# Save the token from response
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 2. Add Payment Method

```bash
# Add a credit card payment method
curl -X POST http://localhost:8009/api/v1/payment-methods \
  -H "Authorization: Bearer $JWT_TOKEN" \
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

# Save the payment_method_id from response
export PAYMENT_METHOD_ID="uuid-from-response"
```

### 3. Create Test Order

Create an order using the Order Service:

```bash
# Create test order
curl -X POST http://localhost:8008/api/v1/orders \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "product_id": "test-product-1",
        "quantity": 2,
        "price": 2999
      }
    ],
    "total_amount": 5998
  }'

# Save the order_id from response
export ORDER_ID="uuid-from-response"
```

### 4. Process Payment

```bash
# Process payment for the order
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$ORDER_ID'",
    "payment_method_id": "'$PAYMENT_METHOD_ID'",
    "amount": 5998,
    "currency": "USD",
    "description": "Payment for order '$ORDER_ID'"
  }'

# Save the payment_id from response
export PAYMENT_ID="uuid-from-response"
```

### 5. Check Payment Status

```bash
# Get payment status
curl -X GET http://localhost:8009/api/v1/payments/$PAYMENT_ID/status \
  -H "Authorization: Bearer $JWT_TOKEN"

# Expected response:
{
  "payment_id": "uuid",
  "status": "COMPLETED",
  "updated_at": "2025-09-27T00:00:00Z"
}
```

### 6. Get Payment History

```bash
# Get user's payment history
curl -X GET http://localhost:8009/api/v1/payments?limit=10 \
  -H "Authorization: Bearer $JWT_TOKEN"

# Get specific payment details
curl -X GET http://localhost:8009/api/v1/payments/$PAYMENT_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

## Testing Scenarios

### 1. Successful Payment Flow

```bash
# Test successful payment (90% success rate by default)
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$ORDER_ID'",
    "payment_method_id": "'$PAYMENT_METHOD_ID'",
    "amount": 1999,
    "currency": "USD"
  }'
```

### 2. Realistic Payment Processing Testing

The service simulates realistic payment processing with the following features:

**Processing Delays**: Each payment takes 1-3 seconds to process (configurable)
**Success Rate**: 95% success rate by default (configurable)
**Failure Scenarios**: Different types of failures with realistic error messages

```bash
# Test successful payment (95% chance)
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$ORDER_ID'",
    "payment_method_id": "'$PAYMENT_METHOD_ID'",
    "amount": 2999,
    "currency": "USD"
  }'

# Force specific failure scenarios by using special amounts:
# Amount ending in 01: Insufficient funds
# Amount ending in 02: Card declined  
# Amount ending in 03: Network error
# Amount ending in 04: Invalid payment method

# Test insufficient funds scenario
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$ORDER_ID'",
    "payment_method_id": "'$PAYMENT_METHOD_ID'",
    "amount": 1501,
    "currency": "USD"
  }'

# Test card declined scenario
curl -X POST http://localhost:8009/api/v1/payments \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$ORDER_ID'",
    "payment_method_id": "'$PAYMENT_METHOD_ID'",
    "amount": 1502,
    "currency": "USD"
  }'
```

### 3. PayPal Payment Method

```bash
# Add PayPal payment method
curl -X POST http://localhost:8009/api/v1/payment-methods \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "PAYPAL",
    "display_name": "My PayPal Account",
    "payment_details": {
      "email": "user@example.com"
    }
  }'
```

### 4. Webhook Testing

```bash
# Simulate webhook notification
curl -X POST http://localhost:8009/api/v1/webhooks/payment \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "PAYMENT_COMPLETED",
    "payment_id": "'$PAYMENT_ID'",
    "data": {
      "gateway_transaction_id": "mock_txn_123",
      "amount": 5998,
      "currency": "USD"
    },
    "timestamp": "2025-09-27T00:00:00Z"
  }'
```

## Development Workflow

### 1. Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### 2. Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### 3. Database Management

```bash
# Reset database
python -m src.models.database reset

# Create migration
python -m src.models.database create-migration "add_new_field"

# Apply migrations
python -m src.models.database migrate
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check if ports 8001 and 8008 are accessible
   - Verify database file permissions
   - Check environment variables

2. **Authentication errors**
   - Ensure JWT token is valid and not expired
   - Verify AUTH_SERVICE_URL is correct
   - Check JWT_SECRET_KEY matches auth service

3. **Payment processing fails**
   - Check order exists in order service
   - Verify payment method is valid and active
   - Review payment amount and currency

4. **Database errors**
   - Ensure database file is writable
   - Check if migrations are up to date
   - Verify database schema matches models

### Logs and Debugging

```bash
# View service logs
docker-compose logs payment-service

# Enable debug logging
export LOG_LEVEL=DEBUG

# Check specific log files
tail -f logs/payment-service.log
```

## Integration Testing

### End-to-End Flow

1. User registers/logs in via Auth Service
2. User creates order via Order Service
3. User adds payment method via Payment Service
4. User processes payment via Payment Service
5. Order status updated via Order Service integration
6. Payment confirmation sent via webhook simulation

### Service Dependencies

- **Auth Service**: User authentication and JWT validation
- **Order Service**: Order validation and status updates
- **Database**: Payment data persistence
- **Mock Gateway**: Simulated payment processing

## Production Considerations

### Security

- Use HTTPS in production
- Rotate JWT secrets regularly
- Implement rate limiting
- Monitor for suspicious activity

### Performance

- Configure database connection pooling
- Implement caching for frequent queries
- Monitor response times and error rates
- Set up proper logging and alerting

### Monitoring

- Health check endpoints for load balancers
- Structured logging for observability
- Metrics collection for performance monitoring
- Error tracking and alerting

This quickstart guide provides everything needed to get the Payment Processing Service running and tested in a development environment.
