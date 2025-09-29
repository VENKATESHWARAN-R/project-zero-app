# Project Zero App 🛍️

> A comprehensive e-commerce microservices application built for demonstrating AI-powered DevOps and security tooling

## Overview

**Project Zero App** is a fully-functional e-commerce platform built using modern microservices architecture. This application serves as a realistic demonstration environment for **Project Zero** - an AI-powered DevOps and security analysis platform that includes automated vulnerability scanning, code analysis, and infrastructure monitoring.

### Why This Project Exists

This application was specifically designed to:

- **Demonstrate Real-World IT Landscapes**: Provide a realistic microservices environment with multiple technologies, databases, and deployment patterns
- **Security Analysis Showcase**: Generate authentic vulnerabilities, dependencies, and security findings for AI-powered scanning tools
- **DevOps Tooling Demo**: Create a comprehensive CI/CD pipeline, infrastructure-as-code, and monitoring setup for demonstration purposes
- **Multi-Technology Coverage**: Include diverse programming languages, frameworks, and infrastructure components to showcase broad analysis capabilities
- **Documentation Excellence**: Serve as an example of specification-driven development with comprehensive documentation for AI agents to analyze

## Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Redis        │    │   PostgreSQL    │
│   (Next.js)     │    │   (Sessions)     │    │   (Production)  │
│   Port 3000     │    │   Port 6379      │    │   Port 5432     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌─────────────────────────────┼─────────────────────────────┐
    │           ┌─────────────────┼─────────────────┐           │
    │           │   API Gateway   │                 │           │
    │           │    (Go/Gin)     │                 │           │
    │           │   Port 8000     │                 │           │
    │           └─────────────────┼─────────────────┘           │
    │                            │                             │
    ┌────────────────────────────┼────────────────────────────┐
    │                           │                            │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │ Product Service │    │  Cart Service   │
│ FastAPI+SQLite  │    │ FastAPI+SQLite  │    │ Node.js+SQLite  │
│   Port 8001     │    │   Port 8004     │    │   Port 8007     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                           │                            │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Order Service  │    │ Payment Service │    │User Profile Svc │
│ FastAPI+SQLite  │    │ FastAPI+SQLite  │    │ FastAPI+SQLite  │
│   Port 8008     │    │   Port 8009     │    │   Port 8002     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Current Status**: ✅ **8 Backend Services + API Gateway + Frontend Implemented & Running**

### Service Breakdown

## Phase 1 - MVP Services (Core Functionality) ✅ **IMPLEMENTED**

### 🔐 001-auth-service ✅
- **Technology**: Python 3.13+ / FastAPI + SQLite
- **Purpose**: User authentication, JWT token management
- **Endpoints**: `/auth/login`, `/auth/logout`, `/auth/refresh`, `/auth/verify`, `/auth/register`
- **Database**: User credentials, sessions (SQLite)
- **Port**: 8001
- **Status**: **Fully implemented with comprehensive testing**

### 📦 004-product-catalog-service ✅
- **Technology**: Python 3.13+ / FastAPI + SQLite
- **Purpose**: Product information management with search & filtering
- **Endpoints**: `/api/v1/products`, `/api/v1/products/{id}`, `/api/v1/categories`, `/api/v1/products/search`
- **Database**: Product details, categories, pricing (SQLite)
- **Port**: 8004
- **Status**: **Fully implemented with advanced search capabilities**

### 🛒 007-cart-service ✅
- **Technology**: Node.js / Express + SQLite
- **Purpose**: Shopping cart operations with persistence
- **Endpoints**: `/api/v1/cart`, `/api/v1/cart/items`, `/api/v1/cart/summary`
- **Database**: Cart items, user sessions (SQLite)
- **Port**: 8007
- **Status**: **Fully implemented with session management**

### 📋 008-order-service ✅
- **Technology**: Python 3.13+ / FastAPI + SQLite
- **Purpose**: Order processing and lifecycle management
- **Endpoints**: `/orders/`, `/orders/{id}`, `/orders/{id}/status`, `/shipping/calculate`
- **Database**: Orders, status history, shipping (SQLite)
- **Port**: 8008
- **Status**: **Fully implemented with status tracking**

### 💳 009-payment-service ✅
- **Technology**: Python 3.13+ / FastAPI + SQLite
- **Purpose**: Mock payment processing with realistic simulation
- **Endpoints**: `/api/v1/payments`, `/api/v1/payment-methods`, `/api/v1/webhooks`
- **Database**: Payments, methods, history (SQLite)
- **Port**: 8009
- **Status**: **Fully implemented with 95% success rate simulation**

### 🌐 016-frontend-web-app ✅
- **Technology**: Next.js 15 / TypeScript / Tailwind CSS 4
- **Purpose**: Customer-facing web application
- **Location**: `frontend/` (separate from backend services)
- **Features**: Product browsing, cart management, user authentication, responsive design
- **Port**: 3000
- **Status**: **Fully implemented with modern React patterns**

## Phase 2 - Core E-commerce (Extended Functionality)

### 👤 002-user-profile-service ✅
- **Technology**: Python 3.13+ / FastAPI + SQLite
- **Purpose**: User profile, address, and preferences management
- **Endpoints**: `/profiles`, `/addresses`, `/preferences`, `/activity`, `/admin`
- **Database**: User profiles, addresses, preferences, activity logs (SQLite)
- **Port**: 8002
- **Status**: **Fully implemented with comprehensive profile management**

### 🌉 015-api-gateway ✅
- **Technology**: Go/Gin with Viper configuration
- **Purpose**: Request routing, rate limiting, circuit breaking, authentication proxy
- **Endpoints**: `/health`, `/health/ready`, `/gateway/services`, `/gateway/routes`, `/gateway/metrics`, `/api/*`
- **Features**: Service discovery, health monitoring, CORS support, structured logging
- **Port**: 8000
- **Status**: **Fully implemented with service registry and middleware**

## Phase 3 - Enhanced Features

### 📂 005-category-service ✅
- **Technology**: Node.js/Express + Sequelize + SQLite
- **Purpose**: Hierarchical product categorization and organization with admin management
- **Endpoints**: `/categories`, `/categories/{id}`, `/categories/{id}/hierarchy`, `/categories/{id}/products`, `/categories/search`
- **Database**: Hierarchical categories with parent-child relationships (SQLite)
- **Port**: 8005
- **Status**: **Fully implemented with 5-level hierarchy, circular prevention, and admin authentication**

### 📧 011-notification-service ✅
- **Technology**: Node.js/Express + SQLite
- **Purpose**: Multi-channel notifications (email, SMS, in-app) with template management
- **Endpoints**: `/notifications`, `/notifications/schedule`, `/notifications/template`, `/templates`, `/preferences`
- **Database**: Notifications, templates, user preferences (SQLite)
- **Port**: 8011
- **Status**: **Fully implemented with template system and user preferences**

### 📊 006-inventory-service
- **Technology**: Python/FastAPI
- **Purpose**: Stock management and tracking
- **Port**: 8006

### ⭐ 013-review-service
- **Technology**: Node.js/Express
- **Purpose**: Product reviews and ratings
- **Port**: 8013

## Phase 4 - Full Platform

### 🔍 012-search-service
- **Technology**: Node.js/Express
- **Purpose**: Advanced product search
- **Port**: 8012

### 🚚 010-shipping-service
- **Technology**: Go
- **Purpose**: Shipping calculations and tracking
- **Port**: 8010

### ⚙️ 014-admin-service
- **Technology**: Python/FastAPI
- **Purpose**: Administrative dashboard
- **Port**: 8014

### 🎯 003-user-preferences-service
- **Technology**: Python/FastAPI
- **Purpose**: User personalization settings
- **Port**: 8003

## Technology Stack

### Backend Technologies
- **Python**: FastAPI, SQLAlchemy, Pydantic, bcrypt, PyJWT
- **Node.js**: Express.js, Sequelize, bcrypt, jsonwebtoken
- **Go**: Gin framework, GORM, JWT-Go

### Frontend Technologies
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context/zustand
- **HTTP Client**: Axios/fetch

### Databases & Storage
- **Development Database**: SQLite (per service) - Currently implemented
- **Production Database**: PostgreSQL 15+ (configured, ready for deployment)
- **Cache**: Redis 7+ (available via Docker Compose)
- **Session Storage**: Redis
- **File Storage**: Local filesystem (demo) / S3-compatible

### Infrastructure & DevOps
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (local: minikube/kind)
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: Terraform (GCP)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Load Balancing**: Nginx
- **Service Mesh**: Istio (advanced scenarios)

### Development Tools
- **Specification-Driven Development**: GitHub Spec Kit
- **API Documentation**: OpenAPI 3.0/Swagger
- **Code Quality**: SonarQube, ESLint, Black
- **Security Scanning**: Trivy, Snyk, OWASP Dependency Check
- **Version Control**: Git with conventional commits

## Development Methodology

This project follows **Specification-Driven Development (SDD)** using GitHub's Spec Kit:

### SDD Workflow
1. **`/specify`** - Define WHAT to build (user stories, requirements)
2. **`/plan`** - Define HOW to build (tech stack, architecture)
3. **`/tasks`** - Break into actionable implementation tasks
4. **Implement** - Build according to specifications
5. **Validate** - Test against acceptance criteria

### Project Structure
```
project-zero-app/
├── .specify/                 # Spec Kit configuration
├── memory/
│   ├── constitution.md       # Development principles
│   └── constitution_update_checklist.md
├── specs/                    # Feature specifications
│   ├── 001-auth-service/
│   │   ├── spec.md          # Requirements & user stories
│   │   ├── plan.md          # Technical implementation plan
│   │   ├── tasks.md         # Actionable task breakdown
│   │   ├── contracts/       # API specifications
│   │   ├── data-model.md    # Database schemas
│   │   └── research.md      # Technology research
│   └── [other services...]
├── services/                 # Backend microservices
│   ├── auth-service/         # ✅ JWT authentication (Python/FastAPI)
│   ├── product-catalog-service/ # ✅ Product management (Python/FastAPI)
│   ├── category-service/     # ✅ Category management (Node.js/Express)
│   ├── cart-service/         # ✅ Shopping cart (Node.js/Express)
│   ├── order-service/        # ✅ Order processing (Python/FastAPI)
│   ├── payment-service/      # ✅ Payment processing (Python/FastAPI)
│   └── notification-service/ # ✅ Notifications (Node.js/Express)
├── frontend/                 # ✅ Next.js web application - Fully implemented
├── infrastructure/
│   ├── docker-compose/      # Local development
│   ├── kubernetes/          # K8s manifests
│   ├── terraform/           # GCP infrastructure
│   └── monitoring/          # Observability stack
├── docs/
│   ├── architecture/        # System design documents
│   ├── api-specs/          # API documentation
│   ├── deployment/         # Setup guides
│   └── security/           # Security documentation
├── scripts/                 # Automation scripts
└── .github/workflows/       # CI/CD pipelines
```

## Development Principles (Constitution)

### Core Philosophy
- **Simplicity First**: Choose the simplest solution that works
- **Functionality Over Complexity**: Working features beat elaborate architectures
- **Progressive Enhancement**: Start minimal, add complexity only when needed
- **Demo-Focused**: Prioritize demonstrable features over production-scale optimizations

### Security Standards
- Implement proper authentication/authorization patterns
- Follow secure coding practices
- Regular dependency scanning and updates
- Secrets management best practices
- Input validation and sanitization

### Observability Requirements
- Structured logging (JSON format) for all services
- Health check endpoints (`/health`) for all services
- Basic metrics collection (request count, response time)
- Distributed tracing for request flows
- Error tracking and alerting

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.13+
- Node.js 18+
- Go 1.21+ (for gateway and shipping service)
- Git
- GitHub Spec Kit CLI

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/project-zero-app.git
   cd project-zero-app
   ```

2. **Install Spec Kit**
   ```bash
   uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai claude
   ```

3. **Start all services with Docker Compose** (Recommended)
   ```bash
   # Start all implemented services
   docker-compose up -d
   
   # Or start specific services
   docker-compose up -d auth-service product-catalog-service cart-service order-service payment-service
   
   # Check service status
   docker ps
   ```

4. **Verify services are running**
   ```bash
   # Health checks for all services
   curl http://localhost:8000/health  # API Gateway
   curl http://localhost:8001/health  # Auth Service
   curl http://localhost:8004/health  # Product Service
   curl http://localhost:8005/health  # Category Service
   curl http://localhost:8007/health  # Cart Service
   curl http://localhost:8008/health  # Order Service
   curl http://localhost:8009/health  # Payment Service
   curl http://localhost:8011/health  # Notification Service
   curl http://localhost:8002/health  # User Profile Service
   ```

5. **Access the application**
   - **Frontend Application**: http://localhost:3000 ✅
   - **API Gateway**: http://localhost:8000 (Entry point for all API requests)
   - **API Documentation**:
     - API Gateway: http://localhost:8000/gateway/services (Service registry)
     - Auth Service: http://localhost:8001/docs
     - Product Service: http://localhost:8004/docs
     - Category Service: http://localhost:8005/docs
     - Cart Service: http://localhost:8007/docs (if available)
     - Order Service: http://localhost:8008/docs
     - Payment Service: http://localhost:8009/docs
     - Notification Service: http://localhost:8011/docs
     - User Profile Service: http://localhost:8002/docs
   - **Individual services**: http://localhost:800X

### Environment Configuration

Create `.env` files for each service with appropriate configuration:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/project_zero
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services (Mock for demo)
EMAIL_SERVICE_URL=http://localhost:8011
PAYMENT_SERVICE_URL=http://localhost:8009
```

## API Documentation

### Interactive Documentation (Swagger UI)
Each service exposes comprehensive OpenAPI documentation:
- **Auth Service**: http://localhost:8001/docs
- **Product Catalog**: http://localhost:8004/docs
- **Category Service**: http://localhost:8005/docs
- **Cart Service**: http://localhost:8007/docs (if available)
- **Order Service**: http://localhost:8008/docs
- **Payment Service**: http://localhost:8009/docs
- **Notification Service**: http://localhost:8011/docs

### API Specifications
Complete OpenAPI specifications are available in each service directory:
- `services/auth-service/swagger.json`
- `services/product-catalog-service/swagger.json`
- `services/category-service/swagger.json`
- `services/cart-service/swagger.json`
- `services/order-service/swagger.json`
- `services/payment-service/swagger.json`
- `services/notification-service/swagger.json`

### Comprehensive Documentation
- **Complete API Guide**: [docs/api-documentation.md](docs/api-documentation.md)
- **Services Overview**: [docs/services-overview.md](docs/services-overview.md)

## Testing Strategy

### Unit Tests
- FastAPI: pytest with TestClient
- Node.js: Jest with supertest
- Go: built-in testing package

### Integration Tests
- Service-to-service communication
- Database integration
- API contract testing

### E2E Tests
- Frontend user flows
- Complete purchase journey
- Cross-service workflows

## Deployment

### Local Development
```bash
docker-compose up -d
```

### Kubernetes (Local)
```bash
kubectl apply -f infrastructure/kubernetes/
```

### GCP Production
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

## Monitoring & Observability

### Health Checks
All services expose `/health` endpoints for monitoring.

### Logs
Structured JSON logs are centralized using the ELK stack.

### Metrics
Prometheus collects metrics from all services, visualized in Grafana.

### Alerts
Basic alerting for service downtime and error rates.

## Contributing

This project uses Specification-Driven Development:

1. **Create a specification** using `/specify` command
2. **Plan the implementation** using `/plan` command  
3. **Break down tasks** using `/tasks` command
4. **Implement** according to the specification
5. **Test** against acceptance criteria
6. **Document** API changes and architectural decisions

## Security Considerations

This application includes both secure implementations and intentional vulnerabilities for security scanning demonstrations:

- **Secure Patterns**: Proper authentication, input validation, secure dependencies
- **Demo Vulnerabilities**: Intentional security gaps for scanning tool demonstration
- **Dependency Management**: Mix of current and outdated packages for scanning

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Project Zero Integration

This application serves as the foundation for demonstrating:

- **XRay-Bot**: Automated vulnerability scanning and analysis
- **DOT-Bot**: DevOps tooling and infrastructure analysis  
- **Project Zero Platform**: Comprehensive AI-powered development assistance

For more information about the Project Zero ecosystem, see the main project documentation.

---

**Built with ❤️ using Specification-Driven Development and GitHub Spec Kit**