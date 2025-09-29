# Services Documentation Index

**Purpose**: Directory index for all Project Zero App service documentation  
**Last Updated**: 2025-09-29  
**Services Count**: 10 (1 frontend + 9 backend services)  

## Service Overview

Project Zero App consists of 10 services that work together to provide a complete e-commerce platform:

### Frontend Services
- [**Frontend Application**](./frontend/README.md) - Next.js user interface (Port: 3000)

### Backend Services
- [**API Gateway**](./api-gateway/README.md) - Go-based request routing and middleware (Port: 8000)
- [**Authentication Service**](./auth-service/README.md) - FastAPI user authentication & JWT management (Port: 8001)  
- [**Product Catalog Service**](./product-catalog-service/README.md) - FastAPI product management (Port: 8004)
- [**Shopping Cart Service**](./cart-service/README.md) - Node.js cart management (Port: 8007)
- [**Order Processing Service**](./order-service/README.md) - FastAPI order lifecycle management (Port: 8008)
- [**Payment Service**](./payment-service/README.md) - FastAPI payment processing (Port: 8009)
- [**User Profile Service**](./user-profile-service/README.md) - FastAPI user profile management (Port: 8002)
- [**Notification Service**](./notification-service/README.md) - Node.js multi-channel notifications (Port: 8011)

## Documentation Structure

Each service directory contains standardized documentation:

```
{service-name}/
├── README.md                   # Service overview and quick links
├── api-docs/                   # API documentation
├── architecture/              # Architecture documentation  
├── operations/                # Operational procedures
├── incidents/                 # Incident reports and post-mortems
├── disaster-recovery/         # DR plans and procedures
├── integration/               # Service integration guides
├── security/                  # Security documentation
├── monitoring/                # Monitoring and alerting
├── deployment/                # Deployment procedures
└── troubleshooting/           # Troubleshooting guides
```

## Service Dependencies

### Upstream Dependencies (Services that depend on others)
- **API Gateway**: Routes to all backend services
- **Cart Service**: Depends on Auth + Product Catalog services
- **Order Service**: Depends on Auth + Cart + Product + Notification services  
- **Payment Service**: Depends on Auth + Order services
- **User Profile Service**: Depends on Auth service
- **Notification Service**: Depends on Auth + User Profile services
- **Frontend**: Consumes all services via API Gateway

### Standalone Services (No dependencies)
- **Auth Service**: Core authentication provider
- **Product Catalog Service**: Core product data

## Quick Access by Category

### API Documentation
- [Frontend API Integration](./frontend/api-docs/)
- [API Gateway Routes](./api-gateway/api-docs/)
- [Auth API Endpoints](./auth-service/api-docs/)
- [Product API Endpoints](./product-catalog-service/api-docs/)
- [Cart API Endpoints](./cart-service/api-docs/)
- [Order API Endpoints](./order-service/api-docs/)
- [Payment API Endpoints](./payment-service/api-docs/)
- [Profile API Endpoints](./user-profile-service/api-docs/)
- [Notification API Endpoints](./notification-service/api-docs/)

### Architecture Documentation  
- [Frontend Architecture](./frontend/architecture/)
- [API Gateway Architecture](./api-gateway/architecture/)
- [Auth Service Architecture](./auth-service/architecture/)
- [Product Catalog Architecture](./product-catalog-service/architecture/)
- [Cart Service Architecture](./cart-service/architecture/)
- [Order Service Architecture](./order-service/architecture/)
- [Payment Service Architecture](./payment-service/architecture/)
- [Profile Service Architecture](./user-profile-service/architecture/)
- [Notification Architecture](./notification-service/architecture/)

### Operational Procedures
- [Frontend Operations](./frontend/operations/)
- [API Gateway Operations](./api-gateway/operations/)
- [Auth Service Operations](./auth-service/operations/)
- [Product Operations](./product-catalog-service/operations/)
- [Cart Operations](./cart-service/operations/)
- [Order Operations](./order-service/operations/)
- [Payment Operations](./payment-service/operations/)
- [Profile Operations](./user-profile-service/operations/)
- [Notification Operations](./notification-service/operations/)

## Technology Stack Summary

| Service | Primary Language | Framework | Database | Special Features |
|---------|-----------------|-----------|----------|------------------|
| Frontend | TypeScript | Next.js | N/A | Server-side rendering |
| API Gateway | Go | Gorilla Mux | N/A | Rate limiting, circuit breakers |
| Auth Service | Python | FastAPI | SQLite/PostgreSQL | JWT, bcrypt, rate limiting |
| Product Catalog | Python | FastAPI | SQLite/PostgreSQL | Search, categorization |
| Cart Service | JavaScript | Node.js/Express | SQLite | Session-based storage |
| Order Service | Python | FastAPI | SQLite/PostgreSQL | State machine, workflow |
| Payment Service | Python | FastAPI | SQLite/PostgreSQL | PCI DSS compliance |
| User Profile | Python | FastAPI | SQLite/PostgreSQL | GDPR compliance |
| Notification | JavaScript | Node.js/Express | SQLite | Multi-channel delivery |

## Health Check Summary

All services implement standard health check endpoints:
- `GET /health` - Basic liveness check
- `GET /health/ready` - Readiness check with dependency validation

## Emergency Contacts

For service-specific emergencies, see individual service documentation or:
- [On-Call Schedule](../contacts/on-call-schedule.md)
- [Escalation Matrix](../contacts/escalation-matrix.md)
- [Emergency Contacts](../contacts/emergency-contacts.md)

---

**Last Updated**: 2025-09-29  
**Next Review**: 2025-12-29