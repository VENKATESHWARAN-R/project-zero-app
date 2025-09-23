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
│   Frontend      │    │   API Gateway    │    │   Load Balancer │
│   (Next.js)     │◄───┤   (Go/Gin)       │◄───┤   (Nginx)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼─────┐ ┌───────▼─────┐ ┌───────▼─────┐
        │Auth Service │ │Product Cat. │ │Cart Service │
        │(Python)     │ │(Python)     │ │(Node.js)    │
        └─────────────┘ └─────────────┘ └─────────────┘
                │               │               │
        ┌───────▼─────┐ ┌───────▼─────┐ ┌───────▼─────┐
        │Order Service│ │Payment Svc  │ │Notification │
        │(Python)     │ │(Python)     │ │(Node.js)    │
        └─────────────┘ └─────────────┘ └─────────────┘
                │               │               │
        ┌───────▼─────┐ ┌───────▼─────┐ ┌───────▼─────┐
        │ PostgreSQL  │ │   Redis     │ │   Logs &    │
        │ Database    │ │   Cache     │ │ Monitoring  │
        └─────────────┘ └─────────────┘ └─────────────┘
```

### Service Breakdown

## Phase 1 - MVP Services (Core Functionality)

### 🔐 001-auth-service
- **Technology**: Python/FastAPI
- **Purpose**: User authentication, JWT token management
- **Endpoints**: `/auth/login`, `/auth/logout`, `/auth/refresh`, `/auth/verify`
- **Database**: User credentials, sessions
- **Port**: 8001

### 📦 004-product-catalog-service
- **Technology**: Python/FastAPI
- **Purpose**: Product information management
- **Endpoints**: `/products`, `/products/{id}`, `/categories`
- **Database**: Product details, categories, pricing
- **Port**: 8004

### 🛒 007-cart-service
- **Technology**: Node.js/Express
- **Purpose**: Shopping cart operations
- **Endpoints**: `/cart`, `/cart/add`, `/cart/remove`, `/cart/update`
- **Database**: Cart items, user sessions
- **Port**: 8007

### 🌐 016-frontend-app
- **Technology**: Next.js/TypeScript/Tailwind CSS
- **Purpose**: Customer-facing web application
- **Features**: Product browsing, cart management, user authentication
- **Port**: 3000

## Phase 2 - Core E-commerce (Extended Functionality)

### 👤 002-user-profile-service
- **Technology**: Python/FastAPI
- **Purpose**: User profile and account management
- **Port**: 8002

### 📋 008-order-service
- **Technology**: Python/FastAPI
- **Purpose**: Order processing and management
- **Port**: 8008

### 💳 009-payment-service
- **Technology**: Python/FastAPI
- **Purpose**: Mock payment processing
- **Port**: 8009

### 🌉 015-api-gateway
- **Technology**: Go/Gin
- **Purpose**: Request routing, rate limiting, authentication
- **Port**: 8000

## Phase 3 - Enhanced Features

### 📂 005-category-service
- **Technology**: Node.js/Express
- **Purpose**: Product categorization and organization
- **Port**: 8005

### 📧 011-notification-service
- **Technology**: Node.js/Express
- **Purpose**: Email/SMS notifications
- **Port**: 8011

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
- **Primary Database**: PostgreSQL 15+
- **Cache**: Redis 7+
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
├── services/                 # Microservice implementations
│   ├── auth-service/
│   ├── product-catalog-service/
│   ├── cart-service/
│   └── frontend-app/
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
- Python 3.11+
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

3. **Start local development environment**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run services individually** (Phase 1)
   ```bash
   # Auth Service
   cd services/auth-service
   pip install -r requirements.txt
   uvicorn main:app --port 8001 --reload

   # Product Catalog Service
   cd services/product-catalog-service
   pip install -r requirements.txt
   uvicorn main:app --port 8004 --reload

   # Cart Service
   cd services/cart-service
   npm install
   npm run dev

   # Frontend App
   cd services/frontend-app
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Individual services: http://localhost:800X

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

Each service exposes OpenAPI documentation:
- Auth Service: http://localhost:8001/docs
- Product Catalog: http://localhost:8004/docs
- Cart Service: http://localhost:8007/docs

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