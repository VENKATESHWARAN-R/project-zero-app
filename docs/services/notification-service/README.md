# Notification Service Documentation

**Service Type**: Backend Notification Management Service  
**Technology**: Node.js (Express)  
**Port**: 8011  
**Repository Path**: `services/notification-service/`

## Overview

The Notification Service provides comprehensive communication capabilities for the Project Zero App ecosystem. It handles multi-channel notifications (email, SMS, in-app), template management, user preferences, and scheduled delivery with full integration across all platform services.

## Purpose and Responsibilities

### Core Functions

- **Multi-Channel Delivery**: Email, SMS, and in-app notification support
- **Template Management**: Dynamic template system with variable substitution
- **Notification Scheduling**: Immediate and scheduled notification delivery
- **User Preferences**: Granular user notification preference management
- **Delivery Tracking**: Comprehensive notification history and audit trails

### In-Scope Features

- Multi-channel notification delivery with mock providers
- Template-based notification system with variable substitution
- Immediate and scheduled notification delivery with retry logic
- User notification preference management with granular controls
- Notification history and audit trail for all communications
- JWT authentication integration with auth service
- RESTful API for notification triggering from other services
- Health monitoring and readiness checks with dependency validation

### Out-of-Scope (Future Considerations)

- Real email/SMS provider integration (Sendgrid, Twilio)
- Advanced notification batching and bulk operations
- Real-time push notifications and WebSocket integration
- Notification analytics and delivery tracking
- A/B testing for notification content
- Rich media notifications (images, attachments)

## Architecture Overview

```text
┌─── Express Application ───┐
│  ├── /notifications routes│
│  ├── Template engine      │
│  ├── JWT authentication   │
│  └── Health monitoring    │
├─── Business Logic ────────┤
│  ├── Notification mgmt    │
│  ├── Template processing  │
│  ├── Delivery scheduling  │
│  └── Preference handling  │
├─── Data Access Layer ─────┤
│  ├── SQLite database      │
│  ├── Notification models  │
│  ├── Template storage     │
│  └── Delivery tracking    │
├─── External Integration ──┤
│  ├── Auth service         │
│  ├── User profile service │
│  ├── Mock email provider  │
│  └── Mock SMS provider    │
└─── Infrastructure ────────┘
   ├── SQLite/PostgreSQL
   ├── Template engine
   └── Scheduling system
```

## API Endpoints

### Notification Management

- `POST /notifications` - Send immediate notification to user
- `GET /notifications` - Get user notification history (paginated, filtered)
- `GET /notifications/{id}` - Get specific notification details
- `POST /notifications/schedule` - Schedule notification for future delivery

### Template Management

- `POST /notifications/template` - Send notification using predefined template
- `GET /templates` - List available notification templates (filtered)
- `POST /templates` - Create new notification template (admin only)
- `GET /templates/{id}` - Get template details and variables
- `PUT /templates/{id}` - Update existing template (admin only)

### User Preferences

- `GET /preferences` - Get user notification preferences
- `PUT /preferences` - Update user notification preferences

### Health and Monitoring

- `GET /health` - Basic service health check
- `GET /health/ready` - Readiness check with auth service connectivity

## Technology Stack

### Core Technologies

- **Node.js**: JavaScript runtime with async/await support
- **Express.js**: Web framework with comprehensive middleware
- **SQLite**: Embedded database for development and testing
- **Handlebars**: Template engine for dynamic content generation

### Service Integration

- **axios**: HTTP client for service communication
- **jsonwebtoken**: JWT token verification and validation
- **Auth Service**: User authentication via token verification
- **User Profile Service**: User contact information (optional graceful degradation)

### Development Tools

- **Jest**: Comprehensive testing framework with coverage reporting
- **ESLint**: Code linting with consistent style enforcement
- **Prettier**: Code formatting and style consistency
- **nodemon**: Development server with automatic reload

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required | Notes |
|----------|---------|---------|----------|-------|
| `DATABASE_URL` | SQLite database URL | `sqlite:///notification_service.db` | No | PostgreSQL for production |
| `AUTH_SERVICE_URL` | Auth service endpoint | `http://localhost:8001` | Yes | JWT token verification |
| `USER_PROFILE_SERVICE_URL` | User profile URL | `http://localhost:8002` | No | User contact information |
| `JWT_SECRET_KEY` | JWT verification key | Auto-generated | Recommended | Must match auth service |
| `NODE_ENV` | Environment mode | `development` | No | Controls features and logging |
| `LOG_LEVEL` | Logging verbosity | `info` | No | debug, info, warn, error |
| `HOST` | Service bind address | `0.0.0.0` | No | Container-friendly |
| `PORT` | Service port | `8011` | No | Service mesh configuration |

## Notification Data Model

### Notification Schema

```json
{
  "id": "integer",
  "user_id": "string",
  "type": "string",
  "channel": "string",
  "title": "string",
  "content": "string",
  "template_id": "integer",
  "template_variables": "object",
  "status": "string",
  "scheduled_at": "datetime",
  "sent_at": "datetime",
  "delivered_at": "datetime",
  "error_message": "string",
  "retry_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Template Schema

```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "type": "string",
  "channel": "string",
  "subject_template": "string",
  "content_template": "string",
  "variables": "array",
  "is_active": "boolean",
  "created_by": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Notification Types and Channels

### Notification Types

- **ORDER_CONFIRMATION**: Order creation and confirmation
- **ORDER_UPDATE**: Order status changes and updates
- **PAYMENT_CONFIRMATION**: Payment processing confirmations
- **SHIPPING_NOTIFICATION**: Shipping and delivery updates
- **WELCOME**: New user welcome messages
- **PROMOTIONAL**: Marketing and promotional content
- **SYSTEM_ALERT**: System maintenance and alerts

### Delivery Channels

- **EMAIL**: Email notifications with HTML templates
- **SMS**: Text message notifications with character limits
- **IN_APP**: In-application notifications and alerts
- **PUSH**: Push notifications (future implementation)

### Channel Priority

1. **IN_APP**: Immediate delivery for real-time alerts
2. **EMAIL**: Primary channel for detailed communications
3. **SMS**: Critical alerts and time-sensitive notifications
4. **PUSH**: Secondary channel for engagement (planned)

## Template System

### Template Variables

Templates support dynamic variable substitution using Handlebars syntax:

```handlebars
Hello {{user.firstName}},

Your order {{order.id}} has been {{order.status}}.

Order Total: {{order.total}}
Estimated Delivery: {{order.estimatedDelivery}}

Thank you for shopping with us!
```

### Common Variables

- **user**: User profile information (firstName, lastName, email)
- **order**: Order details (id, status, total, items)
- **payment**: Payment information (amount, method, status)
- **system**: System information (companyName, supportEmail)

### Template Types

- **TRANSACTIONAL**: Order confirmations, payment receipts
- **PROMOTIONAL**: Marketing campaigns and offers
- **SYSTEM**: System alerts and maintenance notifications
- **INFORMATIONAL**: Account updates and general information

## User Preference Management

### Preference Categories

```json
{
  "email": {
    "order_updates": true,
    "promotional": false,
    "system_alerts": true
  },
  "sms": {
    "order_updates": true,
    "promotional": false,
    "system_alerts": true
  },
  "in_app": {
    "order_updates": true,
    "promotional": true,
    "system_alerts": true
  }
}
```

### Preference Enforcement

- **Opt-out Respect**: Honor user unsubscribe preferences
- **Channel Selection**: Deliver via preferred channels only
- **Frequency Limits**: Respect frequency preferences (planned)
- **Critical Override**: System-critical notifications bypass preferences

## Delivery and Retry Logic

### Delivery States

- **PENDING**: Notification queued for delivery
- **SENT**: Notification dispatched to provider
- **DELIVERED**: Confirmation received from provider
- **FAILED**: Delivery failed with error details
- **CANCELLED**: Notification cancelled before delivery

### Retry Strategy

- **Exponential Backoff**: Increasing delays between retry attempts
- **Maximum Retries**: Configurable retry limit (default: 3)
- **Dead Letter Queue**: Failed notifications after max retries
- **Manual Retry**: Administrative retry for failed notifications

## Integration Patterns

### Service Dependencies

```text
Notification Service ──► Auth Service (/auth/verify)
         │
         └────────────► User Profile Service (/profile) [Optional]
```

### Service Integration

- **Order Service**: Order status and confirmation notifications
- **Payment Service**: Payment confirmation and failure notifications
- **Auth Service**: Welcome messages and account notifications
- **User Profile Service**: Contact information and preferences

### Error Handling

- **401 Unauthorized**: Invalid or expired JWT tokens
- **404 Not Found**: Notification or template not found
- **422 Unprocessable Entity**: Invalid notification data
- **503 Service Unavailable**: External service failures
- **429 Too Many Requests**: Rate limiting enforcement

## Mock Provider Implementation

### Email Provider

- **SMTP Simulation**: Mock SMTP server for development
- **HTML Rendering**: Template rendering with HTML support
- **Bounce Handling**: Simulated bounce and delivery tracking
- **Attachment Support**: File attachment capabilities (planned)

### SMS Provider

- **Message Validation**: Character limit and format validation
- **Delivery Simulation**: Mock delivery confirmation
- **International Support**: Country code and format validation
- **Cost Tracking**: Simulated SMS cost calculations

## Deployment and Operations

### Local Development

```bash
cd services/notification-service
npm install
npm run dev
```

### Docker Deployment

```bash
docker build -t notification-service:latest services/notification-service
docker run -p 8011:8011 \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  -e USER_PROFILE_SERVICE_URL="http://user-profile-service:8002" \
  notification-service:latest
```

### Production Deployment

- **Database**: PostgreSQL with connection pooling
- **Message Queue**: Redis for notification queuing (planned)
- **Email Provider**: Integration with Sendgrid or similar
- **SMS Provider**: Integration with Twilio or similar

## Security Considerations

### Authentication and Authorization

- JWT token validation for all notification operations
- User isolation ensuring notification access control
- Admin-only access for template management
- Secure handling of user contact information

### Data Protection

- **PII Handling**: Secure processing of personally identifiable information
- **Template Security**: Validation of template content and variables
- **Audit Logging**: Comprehensive logging of all notification activities
- **Data Retention**: Configurable retention policies for notification history

## Monitoring and Observability

### Notification Metrics

- **Delivery Rates**: Success and failure rates by channel
- **Response Times**: Notification processing and delivery times
- **Template Usage**: Template utilization and performance analytics
- **User Engagement**: Notification open and click rates (planned)

### System Health

- **Service Dependencies**: Auth and profile service health monitoring
- **Provider Health**: Email and SMS provider connectivity
- **Queue Health**: Notification queue depth and processing times
- **Error Rates**: Failure rates by notification type and channel

### Alerting

- **High Failure Rates**: Delivery failure threshold alerts
- **Service Outages**: Dependency service failure notifications
- **Queue Backlog**: Notification queue overflow alerts
- **Template Errors**: Template rendering failure notifications

## Related Documentation

### Service Documentation

- [API Documentation](./api-docs/endpoints.md) - Complete API reference
- [Template Management](./api-docs/template-management.md) - Template system guide
- [Architecture Overview](./architecture/overview.md) - Technical architecture
- [Delivery Tracking](./architecture/delivery-tracking.md) - Delivery system design

### Operational Documentation

- [Template Management](./operations/template-management.md) - Operational procedures
- [Service Integration](./integration/service-integration.md) - Integration guide
- [Monitoring Setup](./monitoring/notification-monitoring.md) - Observability configuration
- [Troubleshooting](./troubleshooting/common-issues.md) - Issue resolution

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Service Version**: 1.0.0  
**Documentation Version**: 1.0.0