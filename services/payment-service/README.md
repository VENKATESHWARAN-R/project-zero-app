# Payment Processing Service

A comprehensive mock payment processing service for the Project Zero App e-commerce platform. This service provides realistic payment simulation with multiple payment methods, comprehensive failure scenarios, and webhook delivery simulation.

## 🚀 Features

### Core Payment Processing
- **Multiple Payment Methods**: Credit cards, debit cards, and PayPal simulation
- **Realistic Processing**: Configurable delays (1-3 seconds) and success rates (95% default)
- **Comprehensive Failure Scenarios**: Insufficient funds, card declined, network errors, invalid methods
- **Transaction Management**: Complete audit trail with status tracking and history

### Advanced Simulation
- **Gateway Integration**: Mock Stripe, PayPal, and Square gateway responses
- **Realistic Transaction IDs**: Gateway-specific prefixes and formats
- **Configurable Behavior**: Environment-based configuration for testing scenarios
- **Webhook Simulation**: Async delivery with retry logic and exponential backoff

### Security & Integration
- **JWT Authentication**: Secure API endpoints with user validation
- **Service Integration**: Auth service (port 8001) and Order service (port 8008)
- **Input Validation**: Comprehensive payment and method validation
- **Structured Logging**: JSON logging with correlation IDs and observability

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🏃 Quick Start

### Prerequisites

- Python 3.13 or higher (recommended)
- Docker and Docker Compose (recommended for full integration)
- Auth Service running on port 8001
- Order Service running on port 8008
- Redis (for session management) - automatically started with docker-compose

### Installation

1. **Clone and navigate to the service:**
   ```bash
   cd services/payment-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python -m src.models.database init
   ```

6. **Start the service:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8009 --reload
   ```

### Docker Setup (Recommended)

#### Full Stack with All Services
```bash
# From project root - starts all services including payment service
cd ../../
docker-compose up -d auth-service order-service payment-service

# Check all services are running
docker ps

# View payment service logs
docker-compose logs payment-service
```

#### Single Service Development
```bash
# Build and start payment service only
docker-compose up --build payment-service

# Or use the main project's Docker setup
cd ../../
make up SERVICE=payment-service
```

### Health Check & Verification

```bash
# Basic health check
curl http://localhost:8009/health

# Detailed readiness check (includes dependencies)
curl http://localhost:8009/health/ready

# View API documentation
open http://localhost:8009/docs
```

### 🧪 Quick Integration Test

```bash
# 1. Register a test user with auth service
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@payment.com",
    "password": "TestPass123!",
    "full_name": "Payment Test User"
  }'

# 2. Login to get JWT token
JWT_TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@payment.com",
    "password": "TestPass123!"
  }' | jq -r '.access_token')

# 3. Test webhook endpoint (no auth required)
curl -X POST http://localhost:8009/api/v1/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## 📚 API Documentation

### Authentication

All API endpoints (except health checks and webhooks) require JWT authentication:

```bash
Authorization: Bearer <jwt_token>
```

### Core Endpoints

#### Payment Processing

**POST /api/v1/payments**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_method_id": "550e8400-e29b-41d4-a716-446655440001",
  "amount": 5000,
  "currency": "USD",
  "description": "Order payment"
}
```

**GET /api/v1/payments**
- Query parameters: `limit`, `offset`, `status`
- Returns paginated payment history

**GET /api/v1/payments/{payment_id}**
- Returns detailed payment information

**GET /api/v1/payments/{payment_id}/status**
- Returns current payment status

#### Payment Methods

**POST /api/v1/payment-methods**
```json
{
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
}
```

**GET /api/v1/payment-methods**
- Returns user's payment methods

**DELETE /api/v1/payment-methods/{method_id}**
- Removes a payment method

#### Webhooks

**POST /api/v1/webhooks/payment**
- Receives payment gateway webhooks (no auth required)

### Interactive API Documentation

Once the service is running, visit:
- **Swagger UI**: http://localhost:8009/docs
- **ReDoc**: http://localhost:8009/redoc

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8009 | Service port |
| `HOST` | 0.0.0.0 | Service host |
| `DEBUG` | false | Debug mode |
| `DATABASE_URL` | sqlite:///./payment_service.db | Database connection |
| `AUTH_SERVICE_URL` | http://localhost:8001 | Auth service URL |
| `ORDER_SERVICE_URL` | http://localhost:8008 | Order service URL |
| `PAYMENT_SUCCESS_RATE` | 0.95 | Payment success rate (0.0-1.0) |
| `PAYMENT_PROCESSING_DELAY_MIN` | 1000 | Min processing delay (ms) |
| `PAYMENT_PROCESSING_DELAY_MAX` | 3000 | Max processing delay (ms) |
| `PAYMENT_FAILURE_SCENARIOS` | true | Enable failure scenarios |
| `WEBHOOK_SIMULATION_ENABLED` | true | Enable webhook simulation |
| `JWT_SECRET_KEY` | your-secret-key | JWT secret key |
| `LOG_LEVEL` | INFO | Logging level |
| `LOG_FORMAT` | json | Log format (json/console) |

### Payment Configuration

#### Success Rate
Control the percentage of successful payments:
```bash
PAYMENT_SUCCESS_RATE=0.95  # 95% success rate
```

#### Processing Delays
Simulate realistic processing times:
```bash
PAYMENT_PROCESSING_DELAY_MIN=1000  # 1 second minimum
PAYMENT_PROCESSING_DELAY_MAX=3000  # 3 seconds maximum
```

#### Failure Scenarios
Enable/disable specific failure testing:
```bash
PAYMENT_FAILURE_SCENARIOS=true
```

Special amounts for testing failures:
- Amount ending in `01`: Insufficient funds
- Amount ending in `02`: Card declined
- Amount ending in `03`: Network error
- Amount ending in `04`: Invalid payment method

### Database Configuration

#### Development (SQLite)
```bash
DATABASE_URL=sqlite:///./payment_service.db
```

#### Production (PostgreSQL)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/payment_service
```

## 🛠️ Development

### Project Structure

```
services/payment-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── models/              # SQLAlchemy models
│   │   ├── payment.py       # Payment transaction model
│   │   ├── payment_method.py # Payment method model
│   │   └── database.py      # Database configuration
│   ├── api/                 # API endpoints
│   │   ├── payments.py      # Payment processing endpoints
│   │   ├── payment_methods.py # Payment method management
│   │   └── webhooks.py      # Webhook endpoints
│   ├── services/            # Business logic
│   │   ├── payment_processor.py # Mock payment processing
│   │   ├── payment_validator.py # Payment validation
│   │   └── webhook_simulator.py # Webhook simulation
│   ├── integrations/        # External service clients
│   │   ├── auth_service.py  # Auth service client
│   │   └── order_service.py # Order service client
│   └── utils/               # Utilities
│       ├── logging.py       # Structured logging
│       └── security.py     # Security utilities
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── contract/            # API contract tests
│   └── performance/         # Performance tests
├── migrations/              # Database migrations
├── scripts/                 # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

### Code Quality

#### Formatting and Linting
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Database Management

#### Migrations
```bash
# Create migration
python -m src.models.database create-migration "description"

# Apply migrations
python -m src.models.database migrate

# Reset database
python -m src.models.database reset
```

#### Seeding Test Data
```bash
python -m src.models.database seed
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
pytest tests/performance/

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run with verbose output
pytest -v
```

### Test Categories

#### Unit Tests
- **Payment Processor**: Mock processing logic and configuration
- **Payment Validator**: Validation rules and business logic
- **Webhook Simulator**: Delivery simulation and retry logic

#### Integration Tests
- **Payment Flow**: End-to-end payment processing
- **Payment Methods**: Method management workflows
- **Webhook Delivery**: Webhook simulation integration

#### Contract Tests
- **API Endpoints**: OpenAPI specification compliance
- **Request/Response**: Schema validation
- **Error Handling**: Error response formats

#### Performance Tests
- **Concurrent Processing**: Load testing with multiple payments
- **Response Times**: Performance benchmarking
- **Memory Usage**: Resource utilization testing

### Test Configuration

```bash
# Test environment variables
export TEST_DATABASE_URL=sqlite:///./test_payment_service.db
export PAYMENT_SUCCESS_RATE=1.0  # Force success for testing
export PAYMENT_PROCESSING_DELAY_MIN=1
export PAYMENT_PROCESSING_DELAY_MAX=5
```

## 🚢 Deployment

### Docker Deployment

#### Single Service
```bash
# Build image
docker build -t payment-service .

# Run container
docker run -p 8009:8009 \
  -e DATABASE_URL=postgresql://... \
  -e AUTH_SERVICE_URL=http://auth-service:8001 \
  payment-service
```

#### Docker Compose
```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Production Considerations

#### Environment Setup
- Use PostgreSQL for production database
- Configure proper JWT secrets
- Set up SSL/TLS certificates
- Configure log aggregation

#### Monitoring
- Health check endpoints: `/health` and `/health/ready`
- Structured JSON logging for observability
- Metrics collection for performance monitoring
- Error tracking and alerting

#### Security
- JWT token validation
- Input sanitization and validation
- Rate limiting configuration
- HTTPS enforcement

#### Scaling
- Horizontal scaling with load balancers
- Database connection pooling
- Async processing for webhooks
- Caching for frequently accessed data

## 🏗️ Architecture

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │  Order Service  │    │ Payment Service │
│    (Port 8001)  │    │   (Port 8008)   │    │   (Port 8009)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    Database     │
                    │   (SQLite/PG)   │
                    └─────────────────┘
```

### Payment Processing Flow

```
1. Client Request → JWT Validation → Payment Validation
                                          ↓
2. Order Validation ← Order Service ← Payment Creation
                                          ↓
3. Payment Processing → Mock Gateway → Status Update
                                          ↓
4. Webhook Delivery → External Services ← Result Response
```

### Data Models

#### Payment Transaction
- Unique payment identifier
- Order and user references
- Amount and currency
- Status tracking with history
- Gateway transaction details

#### Payment Method
- User payment methods
- Secure detail masking
- Expiration tracking
- Default method management

#### Webhook Events
- Payment status notifications
- Delivery tracking and retry
- Configurable endpoints
- Failure handling

### Integration Patterns

#### Auth Service Integration
- JWT token validation
- User context extraction
- Permission checking

#### Order Service Integration
- Order validation
- Status updates
- Event notifications

#### Webhook Simulation
- Async delivery
- Retry with exponential backoff
- Delivery status tracking

## 🤝 Contributing

### Development Workflow

1. **Fork and Clone**
   ```bash
   git clone <your-fork>
   cd project-zero-app/services/payment-service
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Make Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

5. **Run Tests**
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   ```

6. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Link related issues
   - Describe changes and testing
   - Request review

### Code Style Guidelines

- **Python**: Follow PEP 8, use Black formatter
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Documentation**: Use docstrings for all public functions and classes
- **Testing**: Maintain >90% test coverage
- **Logging**: Use structured logging with appropriate levels

### Commit Message Format

```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scope: api, models, services, tests, config
```

Examples:
- `feat(api): add payment status endpoint`
- `fix(validator): handle edge case in card validation`
- `docs(readme): update configuration section`

## 📄 License

This project is part of the Project Zero App and follows the same licensing terms.

## 🆘 Support

### Documentation
- **API Docs**: http://localhost:8009/docs
- **Architecture**: See `/specs/006-build-a-payment/`
- **Quickstart**: See `/specs/006-build-a-payment/quickstart.md`

### Troubleshooting

#### Common Issues

1. **Service Won't Start**
   - Check port availability (8009)
   - Verify database connectivity
   - Check environment variables

2. **Authentication Errors**
   - Verify JWT token validity
   - Check AUTH_SERVICE_URL configuration
   - Ensure JWT_SECRET_KEY matches auth service

3. **Payment Processing Fails**
   - Check order exists in order service
   - Verify payment method validity
   - Review payment amount and currency

4. **Database Errors**
   - Ensure database file permissions
   - Check migration status
   - Verify schema matches models

#### Debug Mode

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
uvicorn src.main:app --reload --log-level debug
```

#### Health Checks

```bash
# Service health
curl http://localhost:8009/health

# Service readiness
curl http://localhost:8009/health/ready
```

### Getting Help

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check `/specs/006-build-a-payment/` for detailed specs

---

**Built with ❤️ for the Project Zero App ecosystem**
