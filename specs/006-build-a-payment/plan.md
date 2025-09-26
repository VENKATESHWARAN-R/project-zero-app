
# Implementation Plan: Payment Processing Service

**Branch**: `006-build-a-payment` | **Date**: 2025-09-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-build-a-payment/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a mock payment processing service for the Project Zero App e-commerce platform using Python FastAPI framework. The service will handle payment processing for orders with multiple payment methods (credit card, debit card, PayPal simulation), maintain transaction history, and integrate with existing order and auth services. Implementation focuses on realistic simulation without actual financial transactions for demonstration purposes.

## Technical Context
**Language/Version**: Python 3.13+ with FastAPI framework (matching existing services)  
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, bcrypt, PyJWT, httpx, python-jose, passlib, alembic, email-validator  
**Storage**: SQLite for local development, PostgreSQL for production with SQLAlchemy ORM  
**Testing**: pytest with TestClient for FastAPI, contract testing for API endpoints  
**Target Platform**: Linux server, containerized with Docker, running on port 8009
**Project Type**: single service - microservice architecture following existing pattern  
**Performance Goals**: Handle 100+ concurrent payment requests, <500ms response time for payment processing  
**Constraints**: Mock implementation only, no real financial transactions, must integrate with order service (port 8008) and auth service (port 8001)  
**Scale/Scope**: Support demo-level traffic, comprehensive logging, configurable success/failure rates for testing

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I: Core Philosophy**
- ✅ Simplicity First: Using FastAPI (simple, well-documented framework) with SQLite (simple database)
- ✅ Functionality Over Architecture: Mock implementation focuses on working features over complex payment architecture
- ✅ Progressive Enhancement: Starting with basic payment processing, can add complexity later
- ✅ Demo-Focused Development: Explicitly designed for demonstration purposes with mock transactions

**Article II: Project Organization**
- ✅ Service Structure: Following `services/payment-service/` pattern consistent with existing services
- ✅ Infrastructure Organization: Will include Docker configuration and health checks
- ✅ Specification-Driven Structure: Following the spec → plan → tasks → implementation flow

**Article V: Technology Standards**
- ✅ Backend Technologies: Using FastAPI + SQLAlchemy + Pydantic + bcrypt + PyJWT as specified
- ✅ Database: SQLite for local development as per constitution

**Article VI: Security Standards**
- ✅ Authentication Requirements: JWT-based auth integration with auth service
- ✅ Security Practices: Secure handling of payment data (even in mock implementation)

**Article VII: Observability Requirements**
- ✅ Logging Standards: Structured JSON logging with correlation IDs
- ✅ Health Monitoring: `/health` and `/health/ready` endpoints required

**Article VIII: Testing Standards**
- ✅ Test Coverage Requirements: Unit tests, integration tests, API contract tests planned
- ✅ Testing Tools: pytest with TestClient for FastAPI as specified

**RESULT**: ✅ PASS - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
services/payment-service/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── payment.py       # Payment transaction model
│   │   ├── payment_method.py # Payment method model
│   │   └── database.py      # Database configuration
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── payments.py      # Payment processing endpoints
│   │   ├── payment_methods.py # Payment method management
│   │   └── health.py        # Health check endpoints
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── payment_processor.py # Mock payment processing
│   │   ├── payment_validator.py # Payment validation
│   │   └── webhook_simulator.py # Webhook simulation
│   ├── integrations/        # External service integrations
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Auth service client
│   │   └── order_service.py # Order service client
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── logging.py       # Structured logging
│       └── security.py     # Security utilities
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── contract/            # API contract tests
├── migrations/              # Database migrations (if needed)
├── scripts/                 # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

**Structure Decision**: Single microservice following existing Python service pattern in `services/` directory

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Database and model setup tasks from data-model.md
- API endpoint implementation tasks from payment-api.yaml contract
- Service integration tasks for auth and order services
- Mock payment processing logic implementation
- Webhook simulation implementation
- Testing tasks for all components

**Specific Task Categories**:

1. **Infrastructure Setup** [P]:
   - Project structure creation
   - Docker configuration
   - Environment setup
   - Database initialization

2. **Data Layer** [P]:
   - SQLAlchemy models for Payment, PaymentMethod, PaymentStatusHistory, WebhookEvent
   - Database configuration and connection management
   - Migration scripts setup

3. **API Layer**:
   - FastAPI application setup
   - Health check endpoints (/health, /health/ready)
   - Payment processing endpoints
   - Payment method management endpoints
   - Webhook endpoints
   - JWT authentication middleware

4. **Business Logic**:
   - Realistic mock payment processor with 1-3 second delays
   - 95% configurable success rate with specific failure scenarios
   - Payment validation service with comprehensive checks
   - Webhook simulator with async delivery and retry logic
   - Integration clients for auth and order services
   - Transaction ID generation with realistic gateway prefixes
   - Different processing logic for credit cards, debit cards, and PayPal

5. **Testing** [P]:
   - Unit tests for models and services
   - Integration tests for API endpoints
   - Contract tests validating OpenAPI specification
   - End-to-end payment flow tests

6. **Documentation**:
   - README.md with setup instructions
   - API documentation generation
   - Docker deployment guide

**Ordering Strategy**:
- TDD order: Contract tests → Models → Services → API endpoints → Integration tests
- Dependency order: Database → Models → Services → API → Integration → Documentation
- Mark [P] for parallel execution where tasks are independent
- Critical path: Models → Payment processor → API endpoints → Integration

**Estimated Output**: 28-32 numbered, ordered tasks in tasks.md

**Task Dependencies**:
- Database models must be completed before services
- Auth integration required before payment processing
- Payment processing logic required before webhook simulation
- All core functionality required before comprehensive testing

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
