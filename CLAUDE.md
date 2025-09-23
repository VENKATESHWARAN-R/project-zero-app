# Project Zero App Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-23

## Project Overview

**Project Zero App** is a comprehensive e-commerce microservices application designed to demonstrate AI-powered DevOps and security tooling. This serves as a realistic demonstration environment for **Project Zero** - an AI-powered DevOps and security analysis platform.

### Core Purpose
- **Demonstrate Real-World IT Landscapes**: Realistic microservices with multiple technologies
- **Security Analysis Showcase**: Generate authentic vulnerabilities for AI-powered scanning tools
- **DevOps Tooling Demo**: Comprehensive CI/CD, infrastructure-as-code, and monitoring
- **Multi-Technology Coverage**: Diverse programming languages and frameworks
- **Specification-Driven Development**: Example of comprehensive documentation for AI analysis

## Architecture Overview

### Microservices Structure
```
Frontend (Next.js) ↔ API Gateway (Go) ↔ Microservices
                                      ├── Auth Service (Python/FastAPI) ✅
                                      ├── Product Catalog (Python/FastAPI) 📋
                                      ├── Cart Service (Node.js/Express) 📋
                                      ├── Order Service (Python/FastAPI) 📋
                                      ├── Payment Service (Python/FastAPI) 📋
                                      ├── User Profile (Python/FastAPI) 📋
                                      └── Notification (Node.js/Express) 📋
```

### Current Implementation Status
- ✅ **Auth Service**: JWT authentication, bcrypt, rate limiting (Production Ready)
- 🏗️ **Infrastructure**: Docker, monitoring, GCP deployment setup
- 📋 **Planned**: Product catalog, cart, order management, payment processing

## Active Technologies

### Backend Services
- **Python 3.11+ Services**: FastAPI, SQLAlchemy, bcrypt, PyJWT, python-multipart, uvicorn, Pydantic
- **Node.js Services**: Express.js, Sequelize, bcrypt, jsonwebtoken (planned)
- **Go Services**: Gin framework, GORM, JWT-Go (planned for API gateway)

### Frontend & Infrastructure
- **Frontend**: Next.js 14+ with TypeScript, Tailwind CSS, Shadcn UI
- **Databases**: PostgreSQL (primary), Redis (caching/sessions)
- **Infrastructure**: Docker, Kubernetes, Terraform (GCP), Prometheus + Grafana
- **Development**: Specification-driven development with GitHub Spec Kit

## Project Structure

```
project-zero-app/
├── .specify/                    # Spec Kit configuration
│   ├── memory/
│   │   └── constitution.md      # Development governance (v1.0.0)
│   └── templates/               # Feature templates
├── specs/                       # Feature specifications
│   └── 001-build-a-user/       # Auth service specification
│       ├── spec.md              # Requirements & user stories
│       ├── plan.md              # Technical implementation plan
│       ├── tasks.md             # Task breakdown
│       ├── contracts/           # API specifications
│       └── data-model.md        # Database schemas
├── services/                    # Microservice implementations
│   ├── auth-service/            # ✅ ACTIVE: JWT authentication service
│   │   ├── src/                 # FastAPI application code
│   │   │   ├── api/             # API endpoints
│   │   │   ├── models/          # SQLAlchemy models
│   │   │   ├── services/        # Business logic
│   │   │   ├── schemas/         # Pydantic schemas
│   │   │   └── utils/           # Utilities & helpers
│   │   ├── tests/               # Comprehensive test suite
│   │   │   ├── contract/        # API contract tests
│   │   │   ├── integration/     # Integration tests
│   │   │   └── unit/            # Unit tests
│   │   ├── Dockerfile           # Multi-stage Docker build
│   │   ├── docker-compose.yml   # Local development
│   │   ├── requirements.txt     # Python dependencies
│   │   └── README.md            # Service documentation
│   ├── product-catalog-service/ # 📋 PLANNED
│   ├── cart-service/           # 📋 PLANNED
│   └── frontend-app/           # 📋 PLANNED
├── infrastructure/              # Infrastructure as code
│   ├── docker-compose/         # Local development orchestration
│   ├── kubernetes/             # K8s manifests
│   ├── terraform/              # GCP infrastructure
│   └── monitoring/             # Observability stack
└── docs/                       # Project documentation
```

## Commands

### Development Commands
```bash
# Auth Service (Current Active Service)
cd services/auth-service
uv sync                         # Install dependencies
uvicorn main:app --reload --port 8001  # Run development server
pytest                         # Run tests
ruff check .                    # Lint code
ruff format .                   # Format code

# Docker Operations
docker-compose up -d           # Start services
docker-compose down            # Stop services
docker build -t auth-service . # Build image

# Testing
pytest tests/                  # All tests
pytest tests/contract/         # Contract tests only
pytest tests/integration/     # Integration tests only
pytest --cov=src              # Coverage report
```

### Project Commands
```bash
# Specification-driven development
uvx --from git+https://github.com/github/spec-kit.git specify  # Spec Kit CLI
specify init --here --ai claude  # Initialize for Claude

# Infrastructure
terraform -chdir=infrastructure/terraform plan   # Plan infrastructure
kubectl apply -f infrastructure/kubernetes/      # Deploy to K8s
```

## Code Style & Standards

### Python 3.11+ (Active)
- **Framework**: FastAPI with async/await patterns
- **ORM**: SQLAlchemy 2.0 with declarative models
- **Validation**: Pydantic v2 models for request/response
- **Testing**: pytest with async support, minimum 80% coverage
- **Linting**: ruff for linting and formatting
- **Security**: bcrypt for passwords, PyJWT for tokens
- **Structure**: Layered architecture (API → Services → Models)

### Node.js (Planned)
- **Framework**: Express.js with TypeScript
- **ORM**: Sequelize with PostgreSQL
- **Testing**: Jest with supertest
- **Authentication**: jsonwebtoken

### Frontend (Planned)
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript with strict typing
- **Styling**: Tailwind CSS + Shadcn UI
- **State**: React Context or Zustand

## Constitutional Governance

The project follows a comprehensive constitution (v1.0.0) defining:

### Core Principles
1. **Simplicity First**: Choose simplest solutions that work
2. **Functionality Over Architecture**: Working features beat elaborate patterns
3. **Progressive Enhancement**: Start minimal, add complexity incrementally
4. **Demo-Focused**: Prioritize demonstrable features over production optimization

### Organization Standards
- **Service Structure**: All services under `services/{service-name}-service/`
- **Docker Mandate**: Every service MUST include Dockerfile, docker-compose.yml
- **Documentation**: Comprehensive READMEs with GCP deployment info
- **Integration Docs**: Service dependencies and API contracts

### Quality Requirements
- **Testing**: 80% minimum coverage, TDD methodology
- **Security**: JWT auth, bcrypt passwords, input validation
- **Observability**: Structured logging, health endpoints, metrics
- **CI/CD**: Automated testing, security scanning, deployment

## Service Integration Patterns

### Authentication Flow
```
1. User → Frontend → Auth Service (/auth/login)
2. Auth Service → JWT tokens (access + refresh)
3. Frontend → Other Services (with Bearer token)
4. Other Services → Auth Service (/auth/verify) for validation
```

### Current API Endpoints (Auth Service)
- `POST /auth/login` - User authentication
- `POST /auth/logout` - Invalidate tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/verify` - Validate token
- `GET /health` - Health check
- `GET /health/ready` - Readiness check

## Development Workflow

### Specification-Driven Development
1. **`/specify`** - Define WHAT to build (user stories, requirements)
2. **`/plan`** - Define HOW to build (tech stack, architecture)
3. **`/tasks`** - Break into actionable implementation tasks
4. **Implement** - Build according to specifications
5. **Validate** - Test against acceptance criteria

### Git Workflow
- **Branch Naming**: `{###-feature-name}` (e.g., `001-build-a-user`)
- **Commit Messages**: Conventional commits
- **Testing**: All tests must pass before merge
- **Documentation**: Update relevant READMEs and specs

## Recent Changes
- **2025-09-23**: Constitution updated to v1.0.0 (comprehensive governance)
- **001-build-a-user**: Auth service implemented with FastAPI, JWT, bcrypt, rate limiting
- **Infrastructure**: Docker containerization, GCP deployment setup

## Security Considerations

### Implemented (Auth Service)
- JWT token authentication with refresh pattern
- bcrypt password hashing (12 salt rounds)
- Rate limiting on authentication endpoints
- Input validation and sanitization
- Account lockout mechanisms
- Structured logging without sensitive data

### Planned Security Features
- HTTPS enforcement in production
- Secret management with environment variables
- Regular dependency vulnerability scanning
- CORS and security headers
- Distributed rate limiting across services

## Monitoring & Observability

### Current Implementation
- Health check endpoints (`/health`, `/health/ready`)
- Structured JSON logging with correlation IDs
- Request/response logging with performance metrics
- Error tracking and classification

### Planned Infrastructure
- Prometheus metrics collection
- Grafana dashboards
- ELK stack for log aggregation
- Distributed tracing with OpenTelemetry
- Alerting for service downtime and error rates

## Testing Strategy

### Current (Auth Service)
- **Contract Tests**: API endpoint validation (94+ tests)
- **Integration Tests**: Database and service integration
- **Unit Tests**: Business logic validation
- **Coverage**: 80%+ maintained
- **TDD Approach**: Tests written before implementation

### Test Commands
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/contract/     # API contract tests
pytest tests/integration/ # Service integration tests
pytest tests/unit/        # Unit tests

# Coverage reporting
pytest --cov=src --cov-report=html
```

## Deployment

### Local Development
```bash
# Start dependencies
docker-compose up -d postgres redis

# Start auth service
cd services/auth-service
uvicorn main:app --reload --port 8001
```

### GCP Production (Planned)
- **Infrastructure**: Terraform modules for GCP resources
- **Container Registry**: Google Container Registry
- **Orchestration**: Google Kubernetes Engine (GKE)
- **Database**: Cloud SQL (PostgreSQL)
- **Caching**: Memorystore (Redis)
- **Monitoring**: Cloud Monitoring + Grafana

## AI Development Notes

### When Working on This Project
1. **Follow the Constitution**: All changes must comply with constitutional principles
2. **Use Specification-Driven Development**: Create/update specs before implementation
3. **Maintain Service Independence**: Each service should be self-contained
4. **Docker Everything**: Every service needs container support
5. **Document Integration**: Always document how services integrate
6. **Test First**: Write tests before implementation (TDD)
7. **Security First**: Implement security patterns consistently
8. **GCP Focus**: Target Google Cloud Platform for deployment

### Current Priorities
1. **Complete Auth Service**: Address any remaining issues or enhancements
2. **Product Catalog Service**: Next service to implement
3. **Infrastructure Setup**: Complete monitoring and deployment automation
4. **API Gateway**: Implement request routing and cross-cutting concerns
5. **Frontend Application**: React/Next.js e-commerce interface

### Key Files to Reference
- `.specify/memory/constitution.md` - Governance and standards
- `README.md` - Project overview and architecture
- `services/auth-service/README.md` - Example service documentation
- `specs/001-build-a-user/` - Example specification structure

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->