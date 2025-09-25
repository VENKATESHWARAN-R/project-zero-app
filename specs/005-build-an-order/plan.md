
# Implementation Plan: Order Processing Service

**Branch**: `005-build-an-order` | **Date**: 2025-09-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-build-an-order/spec.md`

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
Implement an order processing service for the Project Zero App e-commerce platform that manages the complete order lifecycle from cart checkout to order completion. The service will handle checkout conversion, order status management, customer order history, and admin order management using FastAPI, SQLAlchemy, and SQLite with integration to cart, auth, and product catalog services. Implementation details: Implement this order service using Python with FastAPI framework to maintain consistency with our auth and product catalog services. Use SQLite database for local development with SQLAlchemy ORM. The service should run on port 8008 and expose REST API endpoints. Include SQLAlchemy models for orders, order items, and order status history. Add Pydantic models for request/response validation. The service should integrate with cart service (port 8007) to retrieve and clear cart after order creation, auth service (port 8001) for user verification, and product catalog service (port 8004) for product details and inventory validation. Include order status management, basic tax and shipping calculations, comprehensive logging, health check endpoint, and admin endpoints for order management. Follow the same project structure as our other Python services with minimal dependencies.

## Technical Context
**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, uvicorn, httpx
**Storage**: SQLite (development), PostgreSQL (production)
**Testing**: pytest with TestClient for FastAPI
**Target Platform**: Linux server (containerized)
**Project Type**: single - microservice (follows services/{service-name}-service/ pattern)
**Performance Goals**: Handle standard e-commerce order volumes with <500ms response times
**Constraints**: Minimal dependencies, consistent with existing auth/catalog services
**Scale/Scope**: Demonstration platform supporting basic e-commerce order lifecycle
**Port Assignment**: 8008 (order service)
**Service Integrations**:
- Cart Service (port 8007) - retrieve and clear cart contents
- Auth Service (port 8001) - user verification and token validation
- Product Catalog Service (port 8004) - product details and inventory updates

[NEEDS CLARIFICATION: Tax calculation method not specified - fixed rate, location-based, or external tax service?]
[NEEDS CLARIFICATION: Shipping cost calculation not defined - flat rate, weight-based, location-based, or carrier integration?]
[NEEDS CLARIFICATION: Payment processing integration scope - does this service handle payment or just order tracking?]
[NEEDS CLARIFICATION: Admin user authorization levels not specified - single admin role or multiple permission levels?]
[NEEDS CLARIFICATION: Order modification policy not defined - can orders be modified after creation, or only status updates?]

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I: Core Philosophy**
✅ **Simplicity First**: Using FastAPI with minimal dependencies, SQLAlchemy for straightforward ORM, SQLite for development simplicity
✅ **Functionality Over Architecture**: Implementing basic order management without over-engineering patterns
✅ **Progressive Enhancement**: Starting with core order lifecycle, can add advanced features later
✅ **Demo-Focused Development**: Focused on demonstrating order processing capabilities, not production e-commerce scale

**Article II: Project Organization**
✅ **Service Structure**: Following `services/order-service/` pattern consistent with auth-service
✅ **Infrastructure Organization**: Docker containerization will align with existing patterns
✅ **Specification-Driven Structure**: Following `.specify/` directory requirements with spec.md and plan.md

**Article III: Docker Requirements**
✅ **Containerization Mandate**: Will include Dockerfile, docker-compose.yml, .dockerignore, health checks
✅ **Container Standards**: Using official Python base image, non-root user, explicit port exposure

**Article V: Technology Standards**
✅ **Backend Technologies**: FastAPI + SQLAlchemy + Pydantic aligned with specified Python stack

**Article VI: Security Standards**
✅ **Authentication Requirements**: JWT validation integration with auth service
✅ **Security Practices**: Environment variables for secrets, input validation via Pydantic

**Article VII: Observability Requirements**
✅ **Logging Standards**: Structured logging with correlation IDs
✅ **Health Monitoring**: `/health` and `/health/ready` endpoints required

**Article VIII: Testing Standards**
✅ **Test Coverage Requirements**: pytest with unit, integration, and API contract tests
✅ **Testing Tools**: pytest with TestClient for FastAPI as specified

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
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project) - This is a standalone microservice following the services/{service-name}-service/ pattern established by the existing auth-service

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
- Each OpenAPI endpoint → contract test task [P]
- Each data entity (Order, OrderItem, ShippingAddress, OrderModification) → model creation task [P]
- Each user story from spec → integration test task
- Service integration tasks for auth, cart, product catalog services
- Implementation tasks to make tests pass (TDD approach)

**Specific Task Categories**:
1. **Database Setup**: SQLAlchemy models, database initialization, migrations
2. **API Contracts**: FastAPI route handlers, Pydantic schemas, OpenAPI validation
3. **Business Logic**: Order creation workflow, status transitions, modification rules
4. **Service Integration**: HTTP clients for auth, cart, product services
5. **Calculations**: Tax calculation (8.5% fixed rate), shipping cost (weight-based tiers)
6. **Testing**: Contract tests, integration tests, service mocking
7. **Containerization**: Dockerfile, docker-compose, health checks

**Ordering Strategy**:
- TDD order: Contract tests → Models → Business logic → API endpoints
- Dependency order: Database models → Services → API handlers → Integration
- Mark [P] for parallel execution (independent files/components)
- Service integrations after core functionality

**Key Dependencies to Handle**:
- Auth service integration for JWT validation and admin roles
- Cart service integration for cart retrieval and clearing
- Product catalog service for product details and inventory
- Database schema creation and seeding

**API Endpoints Coverage** (15 endpoints total):
- `POST /orders` - Create order from cart ✅
- `GET /orders` - Get user order history ✅
- `GET /orders/{order_id}` - Get specific order details ✅
- `PATCH /orders/{order_id}` - Modify order ✅
- `POST /orders/{order_id}/cancel` - Cancel order ✅
- `PUT /orders/{order_id}/status` - Update order status ✅
- `GET /orders/{order_id}/status-history` - Get order status history ✅
- `GET /admin/orders` - Get all orders (admin only) ✅
- `PUT /admin/orders/{order_id}/status` - Admin status update ✅
- `POST /shipping/calculate` - Calculate shipping cost ✅
- `GET /shipping/rates` - Get available shipping rates ✅
- `GET /health` - Health check ✅
- `GET /health/ready` - Readiness check ✅

**Estimated Output**: 30-34 numbered, ordered tasks in tasks.md covering:
- 4 model creation tasks (Order, OrderItem, ShippingAddress, OrderModification)
- 10 API endpoint implementation tasks (15 endpoints grouped logically)
- 6 service integration tasks (auth, cart, product catalog)
- 8 testing tasks (contract, integration, unit)
- 4 infrastructure/deployment tasks (Docker, health checks)

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
