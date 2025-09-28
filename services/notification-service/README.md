# Notification Service

**Version**: 1.0.0
**Port**: 8011
**Technology**: Node.js + Express + Sequelize + SQLite

## Overview

The Notification Service is a core component of the Project Zero App e-commerce platform, responsible for handling all user communications including email notifications, SMS notifications, and in-app notifications. The service provides a comprehensive API for sending immediate and scheduled notifications, managing notification templates, and handling user notification preferences.

## Features

### Core Functionality
- **Multi-channel Notifications**: Support for email, SMS, and in-app notifications
- **Template System**: Reusable notification templates with variable substitution
- **Scheduled Notifications**: Schedule notifications for future delivery with retry logic
- **User Preferences**: Granular user control over notification types and channels
- **Notification History**: Complete audit trail and history of all notifications
- **Mock Providers**: Simulated email and SMS delivery for development and testing

### Integration
- **JWT Authentication**: Integrated with Project Zero App auth service
- **Service Communication**: RESTful API integration with other microservices
- **Health Monitoring**: Comprehensive health and readiness checks
- **Swagger Documentation**: Complete API documentation at `/docs`

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Generate API documentation
node src/swagger/index.js

# Visit service
open http://localhost:8011/health
open http://localhost:8011/docs
```

### Docker Deployment

```bash
# Build image
docker build -t notification-service:latest .

# Run container
docker run -p 8011:8011 \
  -e AUTH_SERVICE_URL="http://host.docker.internal:8001" \
  notification-service:latest

# Health check
curl http://localhost:8011/health
```

## API Endpoints

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check with dependencies

### Notification Endpoints
- `POST /notifications` - Send immediate notification
- `GET /notifications` - Get user notification history (paginated)
- `GET /notifications/{id}` - Get specific notification details
- `POST /notifications/schedule` - Schedule notification for future delivery
- `POST /notifications/template` - Send notification using template

### Template Endpoints
- `GET /templates` - List available templates (with filters)
- `POST /templates` - Create new template (admin only)
- `GET /templates/{id}` - Get template details
- `PUT /templates/{id}` - Update template (admin only)

### Preference Endpoints
- `GET /preferences` - Get user notification preferences
- `PUT /preferences` - Update user notification preferences

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | `8011` | No |
| `HOST` | Bind host | `0.0.0.0` | No |
| `NODE_ENV` | Environment | `development` | No |
| `DATABASE_URL` | SQLite database URL | `sqlite:///notification_service.db` | No |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | Yes |
| `USER_PROFILE_SERVICE_URL` | User profile service URL | `http://localhost:8002` | No |
| `JWT_SECRET_KEY` | JWT signing secret | Auto-generated | Recommended |
| `LOG_LEVEL` | Logging level | `info` | No |

### Example Configuration

```bash
# Development
export AUTH_SERVICE_URL=http://localhost:8001
export USER_PROFILE_SERVICE_URL=http://localhost:8002
export LOG_LEVEL=debug

# Production
export NODE_ENV=production
export DATABASE_URL=postgresql://user:pass@db:5432/notifications
export AUTH_SERVICE_URL=https://auth.projectzero.com
export JWT_SECRET_KEY=your-strong-secret-key
```

## Notification Templates

### Default Templates

The service includes several default templates:

#### Welcome Email (`welcome_email_registration`)
```json
{
  "subject": "Welcome to Project Zero App, {{userName}}!",
  "variables": {
    "userName": { "type": "string", "required": true },
    "activationLink": { "type": "string", "required": true }
  }
}
```

#### Order Confirmation (`order_email_confirmation`)
```json
{
  "subject": "Order Confirmation - {{orderNumber}}",
  "variables": {
    "customerName": { "type": "string", "required": true },
    "orderNumber": { "type": "string", "required": true },
    "orderTotal": { "type": "string", "required": true },
    "orderItems": { "type": "array", "required": true }
  }
}
```

#### Payment SMS (`payment_sms_confirmation`)
```json
{
  "content": "Payment confirmed! Amount: {{amount}} for order {{orderNumber}}. Card ending in {{last4}}.",
  "variables": {
    "amount": { "type": "string", "required": true },
    "orderNumber": { "type": "string", "required": true },
    "last4": { "type": "string", "required": true }
  }
}
```

### Template Variable Substitution

Templates support `{{variableName}}` syntax:

```javascript
// Template content
"Hello {{userName}}, your order {{orderNumber}} totaling {{orderTotal}} has been confirmed."

// Variables
{
  "userName": "John Doe",
  "orderNumber": "ORD-2025-001",
  "orderTotal": "$149.99"
}

// Result
"Hello John Doe, your order ORD-2025-001 totaling $149.99 has been confirmed."
```

## Usage Examples

### Send Immediate Notification

```bash
curl -X POST http://localhost:8011/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "channel": "email",
    "recipient": "user@example.com",
    "subject": "Test Notification",
    "content": "This is a test notification.",
    "metadata": {"source": "api_test"}
  }'
```

### Send Template Notification

```bash
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

### Schedule Notification

```bash
curl -X POST http://localhost:8011/notifications/schedule \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "channel": "email",
    "recipient": "user@example.com",
    "subject": "Scheduled Reminder",
    "content": "This is your scheduled reminder.",
    "scheduledAt": "2025-09-29T10:00:00Z",
    "maxAttempts": 3,
    "retryInterval": 300
  }'
```

### Update User Preferences

```bash
curl -X PUT http://localhost:8011/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": [
      {
        "type": "order",
        "channel": "email",
        "enabled": true,
        "frequency": "immediate"
      },
      {
        "type": "promotional",
        "channel": "email",
        "enabled": false,
        "frequency": "disabled"
      }
    ]
  }'
```

## Database Schema

### Core Tables

#### `notifications`
- `id` (UUID) - Primary key
- `userId` (VARCHAR) - Target user identifier
- `templateId` (UUID) - Template reference (optional)
- `channel` (ENUM) - 'email', 'sms', 'in_app'
- `recipient` (VARCHAR) - Email address or phone number
- `subject` (VARCHAR) - Email subject or SMS preview
- `content` (TEXT) - Notification body
- `metadata` (JSON) - Additional context data
- `status` (ENUM) - 'pending', 'sent', 'delivered', 'failed'
- `scheduledAt`, `sentAt`, `deliveredAt` (TIMESTAMP)
- `failureReason` (TEXT)
- `createdAt`, `updatedAt` (TIMESTAMP)

#### `notification_templates`
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Unique template identifier
- `type` (ENUM) - 'welcome', 'order', 'payment', 'system', 'promotional'
- `channel` (ENUM) - 'email', 'sms', 'in_app'
- `subject` (VARCHAR) - Template subject
- `content` (TEXT) - Template body with variables
- `variables` (JSON) - Variable schema
- `isActive` (BOOLEAN) - Template availability
- `createdAt`, `updatedAt` (TIMESTAMP)

#### `user_notification_preferences`
- `id` (UUID) - Primary key
- `userId` (VARCHAR) - User identifier
- `type` (ENUM) - Notification type
- `channel` (ENUM) - Delivery channel
- `enabled` (BOOLEAN) - Preference enabled
- `frequency` (ENUM) - 'immediate', 'daily', 'weekly', 'disabled'
- `metadata` (JSON) - Additional settings
- `createdAt`, `updatedAt` (TIMESTAMP)

## Testing

### Unit Tests
```bash
npm test
```

### Contract Tests
```bash
npm run test:contract
```

### Integration Tests
```bash
npm run test:integration
```

### Test Coverage
```bash
npm run test:coverage
```

## Development

### Project Structure
```
src/
├── controllers/        # Request handlers
├── middleware/         # Express middleware
├── models/            # Sequelize database models
├── providers/         # Notification delivery providers
├── routes/            # API route definitions
├── services/          # Business logic
├── utils/             # Utility functions
├── integrations/      # External service clients
├── swagger/           # API documentation
├── config/            # Configuration management
├── migrations/        # Database migrations
├── app.js            # Express application setup
└── server.js         # Application entry point

tests/
├── contract/          # API contract tests
├── integration/       # Integration tests
└── setup.js          # Test configuration
```

### Code Quality
```bash
# Linting
npm run lint
npm run lint:fix

# Formatting
npm run format
npm run format:check
```

### Mock Providers

The service includes mock implementations for development:

- **MockEmailProvider**: Simulates email delivery with configurable delays
- **MockSMSProvider**: Simulates SMS delivery with realistic response times
- **InAppProvider**: Handles in-app notifications with immediate delivery

## Security

### Authentication
- JWT token validation via auth service
- Bearer token authentication for all protected endpoints
- User-specific data access controls

### Rate Limiting
- 100 requests per 15-minute window per IP
- Configurable rate limits with proper error responses

### Input Validation
- Comprehensive request validation
- SQL injection prevention via Sequelize ORM
- XSS protection through proper content handling

### Security Headers
- Helmet.js for security headers
- CORS configuration for cross-origin requests
- Request size limiting (1MB max)

## Monitoring

### Health Checks
- `/health` - Basic service health
- `/health/ready` - Service readiness including dependencies

### Logging
- Structured JSON logging with Winston
- Request correlation IDs for distributed tracing
- Error logging with stack traces
- No sensitive data in logs

### Metrics
Available at `/health/ready`:
- Database connectivity status
- Auth service connectivity status
- Service uptime and version

## Production Deployment

### Docker Deployment
```dockerfile
# Production-ready multi-stage build
# Non-root user for security
# Health checks included
# Optimized for size and security
```

### Environment Setup
```bash
# Database
export DATABASE_URL=postgresql://user:pass@host:5432/notifications

# Services
export AUTH_SERVICE_URL=https://auth.internal
export USER_PROFILE_SERVICE_URL=https://profile.internal

# Security
export JWT_SECRET_KEY=your-production-secret
export NODE_ENV=production

# Monitoring
export LOG_LEVEL=info
```

### Scaling Considerations
- Stateless design for horizontal scaling
- Database connection pooling
- Rate limiting per instance
- Load balancer health check support

## Integration with Project Zero App

### Service Dependencies
- **Auth Service** (port 8001): JWT token validation
- **User Profile Service** (port 8002): User contact information
- **Order Service** (port 8008): Order event notifications
- **Payment Service** (port 8009): Payment event notifications

### API Gateway Integration
The service is designed to work behind the Project Zero App API Gateway:
- All routes available at `/api/notifications/*`
- Authentication handled by gateway
- Rate limiting coordinated with gateway

## Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check port availability
lsof -i :8011

# Check database connection
node -e "require('./src/models').sequelize.authenticate().then(() => console.log('DB OK'))"

# Check auth service connectivity
curl http://localhost:8001/health
```

**Authentication Failures**
```bash
# Verify auth service is running
curl http://localhost:8001/health

# Test JWT token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/auth/verify
```

**Database Issues**
```bash
# Reset database (development only)
rm notification_service.db

# Check database file permissions
ls -la notification_service.db
```

### Debug Mode
```bash
# Start with debug logging
DEBUG=notification-service:* npm run dev

# Or set log level
LOG_LEVEL=debug npm run dev
```

## Contributing

### Code Standards
- ESLint configuration for code quality
- Prettier for code formatting
- Jest for testing
- Conventional commit messages

### Development Workflow
1. Create feature branch from main
2. Implement changes with tests
3. Run linting and testing
4. Update documentation
5. Submit pull request

## License

ISC License - Project Zero App Team

---

**Documentation Version**: 1.0.0
**Last Updated**: 2025-09-28
**Service Status**: ✅ Production Ready