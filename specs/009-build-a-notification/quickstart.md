# Quickstart Guide: Notification Service

**Date**: 2025-09-28
**Feature**: Notification Service
**Estimated Time**: 15-20 minutes

## Overview
This quickstart guide demonstrates the core functionality of the notification service by walking through real user scenarios. After completing this guide, you'll have validated all primary notification workflows.

## Prerequisites
- Docker and Docker Compose installed
- All Project Zero App services running (auth, user profile, order, payment services)
- curl or Postman for API testing
- Valid JWT token from auth service

## Quick Setup

### 1. Start the Notification Service

```bash
# Navigate to notification service directory
cd services/notification-service

# Install dependencies
npm install

# Start the service
npm run dev

# Verify service is running
curl http://localhost:8011/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "notification-service",
  "version": "1.0.0",
  "timestamp": "2025-09-28T10:00:00.000Z"
}
```

### 2. Get Authentication Token

```bash
# Login to get JWT token (replace with actual user credentials)
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

Save the `access_token` from the response for subsequent requests.

## Core Scenarios

### Scenario 1: Welcome Notification (User Registration)

**User Story**: As a new user, I want to receive a welcome notification when I register.

```bash
# Send welcome notification using template
curl -X POST http://localhost:8011/notifications/template \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "templateName": "welcome_email_registration",
    "variables": {
      "userName": "John Doe",
      "activationLink": "https://app.example.com/activate/abc123"
    }
  }'
```

**Expected Result**:
- Status: 201 Created
- Notification sent via email
- Response includes notification ID and delivery status

**Verification Steps**:
1. Check notification was created and sent
2. Verify email content contains user name and activation link
3. Confirm notification appears in user's history

### Scenario 2: Order Confirmation Notification

**User Story**: As a customer, I want to receive an order confirmation when I place an order.

```bash
# Send order confirmation notification
curl -X POST http://localhost:8011/notifications/template \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "templateName": "order_email_confirmation",
    "variables": {
      "orderNumber": "ORD-2025-001",
      "customerName": "John Doe",
      "orderTotal": "$149.99",
      "orderItems": [
        {"name": "Wireless Headphones", "price": "$99.99"},
        {"name": "Phone Case", "price": "$49.99"}
      ],
      "estimatedDelivery": "2025-10-05"
    }
  }'
```

**Expected Result**:
- Order details properly formatted in email
- Total amount and items clearly displayed
- Delivery estimate included

**Verification Steps**:
1. Validate order information in notification content
2. Check that all variables were properly substituted
3. Verify notification status is 'sent' or 'delivered'

### Scenario 3: Payment Confirmation (SMS)

**User Story**: As a customer, I want to receive SMS confirmation when my payment is processed.

```bash
# Send payment confirmation via SMS
curl -X POST http://localhost:8011/notifications/template \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "templateName": "payment_sms_confirmation",
    "variables": {
      "amount": "$149.99",
      "orderNumber": "ORD-2025-001",
      "last4": "4242"
    }
  }'
```

**Expected Result**:
- SMS message sent to user's phone
- Contains payment amount and masked card details
- Concise format suitable for SMS

### Scenario 4: Scheduled Order Update Notification

**User Story**: As a customer, I want to be notified when my order status changes.

```bash
# Schedule order shipped notification for future delivery
curl -X POST http://localhost:8011/notifications/schedule \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "channel": "email",
    "recipient": "user@example.com",
    "subject": "Your Order Has Shipped!",
    "content": "Good news! Your order ORD-2025-001 has shipped and will arrive by Oct 5th. Track: TRK123456",
    "scheduledAt": "2025-09-28T14:00:00Z",
    "metadata": {
      "orderNumber": "ORD-2025-001",
      "trackingNumber": "TRK123456"
    }
  }'
```

**Expected Result**:
- Notification scheduled for future delivery
- Returns schedule ID for tracking
- Status shows as 'scheduled'

### Scenario 5: Retrieve Notification History

**User Story**: As a user, I want to see my notification history.

```bash
# Get user's notification history
curl -X GET "http://localhost:8011/notifications?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Result**:
- List of user's notifications with pagination
- Includes status, timestamps, and content
- Properly filtered to user's notifications only

**Verification Steps**:
1. Verify only authenticated user's notifications are returned
2. Check pagination works correctly
3. Confirm all notification details are present

### Scenario 6: User Notification Preferences

**User Story**: As a user, I want to manage my notification preferences.

```bash
# Get current preferences
curl -X GET http://localhost:8011/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Update preferences to disable promotional emails
curl -X PUT http://localhost:8011/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": [
      {
        "type": "promotional",
        "channel": "email",
        "enabled": false,
        "frequency": "disabled"
      },
      {
        "type": "order",
        "channel": "email",
        "enabled": true,
        "frequency": "immediate"
      }
    ]
  }'
```

**Expected Result**:
- Preferences updated successfully
- Future promotional emails won't be sent
- Order notifications continue as normal

## Integration Testing

### Test Service Communication

**1. Auth Service Integration**
```bash
# Verify token validation works
curl -X GET http://localhost:8011/notifications \
  -H "Authorization: Bearer INVALID_TOKEN"
# Should return 401 Unauthorized
```

**2. User Profile Service Integration**
```bash
# Test user preference lookup
curl -X GET http://localhost:8011/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
# Should return user's current preferences
```

### Test Template System

**1. List Available Templates**
```bash
curl -X GET http://localhost:8011/templates \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**2. Test Template Variable Substitution**
```bash
# Send notification with complex variables
curl -X POST http://localhost:8011/notifications/template \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "templateName": "order_email_confirmation",
    "variables": {
      "orderNumber": "TEST-123",
      "items": [{"name": "Test Item", "price": "$10.00"}]
    }
  }'
```

## Performance Testing

### Load Testing Basic Notification Sending
```bash
# Send multiple notifications to test performance
for i in {1..10}; do
  curl -X POST http://localhost:8011/notifications \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"userId\": \"user123\",
      \"channel\": \"email\",
      \"recipient\": \"test$i@example.com\",
      \"subject\": \"Test Notification $i\",
      \"content\": \"This is test notification number $i\"
    }" &
done
wait
```

## Error Scenarios

### Test Error Handling

**1. Invalid Template**
```bash
curl -X POST http://localhost:8011/notifications/template \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "templateName": "nonexistent_template",
    "variables": {}
  }'
# Should return 404 with clear error message
```

**2. Missing Required Fields**
```bash
curl -X POST http://localhost:8011/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123"
  }'
# Should return 422 with validation errors
```

**3. Future Schedule in Past**
```bash
curl -X POST http://localhost:8011/notifications/schedule \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "channel": "email",
    "recipient": "test@example.com",
    "content": "Test",
    "scheduledAt": "2020-01-01T00:00:00Z"
  }'
# Should return 400 with scheduling error
```

## Success Criteria Validation

After completing this quickstart, verify the following:

### ✅ Functional Requirements Met
- [ ] FR-001: Immediate notifications sent successfully
- [ ] FR-002: Multiple channels (email, SMS, in-app) working
- [ ] FR-003: Scheduled notifications created and queued
- [ ] FR-004: Notification history retrievable
- [ ] FR-005: Templates working with variable substitution
- [ ] FR-006: Auth service integration functional
- [ ] FR-009: User preferences respected
- [ ] FR-016: Mock providers simulating delivery

### ✅ Integration Points Working
- [ ] JWT authentication via auth service
- [ ] User preference lookup
- [ ] Template rendering with variables
- [ ] Error handling with proper status codes

### ✅ Performance Characteristics
- [ ] Response times under 200ms for simple notifications
- [ ] Concurrent notification handling works
- [ ] Database operations complete successfully

### ✅ Error Handling
- [ ] Invalid requests return appropriate error codes
- [ ] Missing authentication handled correctly
- [ ] Template errors provide clear feedback
- [ ] Validation errors include field-specific messages

## Troubleshooting

### Common Issues

**1. Service Won't Start**
- Check port 8011 is not in use: `lsof -i :8011`
- Verify Node.js version: `node --version` (requires Node.js 16+)
- Check SQLite database permissions

**2. Authentication Fails**
- Verify auth service is running on port 8001
- Check JWT token is valid and not expired
- Ensure token is included in Authorization header

**3. Notifications Not Sending**
- Check mock providers are configured correctly
- Verify user preferences allow the notification type
- Check template exists and is active

**4. Database Errors**
- Verify SQLite database file is writable
- Check database migrations have run
- Ensure foreign key constraints are satisfied

### Debug Mode
```bash
# Run service with debug logging
DEBUG=notification-service:* npm run dev
```

### Health Check Endpoints
```bash
# Basic health check
curl http://localhost:8011/health

# Detailed readiness check
curl http://localhost:8011/health/ready
```

## Next Steps

After completing this quickstart:

1. **Explore Advanced Features**:
   - Bulk notification sending
   - Template management APIs
   - Notification analytics

2. **Integration Development**:
   - Connect with order service for automatic notifications
   - Set up payment service webhooks
   - Implement real-time notification UI

3. **Production Preparation**:
   - Configure real email/SMS providers
   - Set up monitoring and alerting
   - Performance optimization and scaling

4. **Documentation**:
   - Review complete API documentation at `/docs`
   - Check integration patterns in service README
   - Study notification best practices

This quickstart validates the core notification service functionality and demonstrates integration with the broader Project Zero App ecosystem.