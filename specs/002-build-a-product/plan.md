
# Implementation Plan: Product Catalog Service

**Branch**: `002-build-a-product` | **Date**: 2025-09-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-build-a-product/spec.md`

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
Product catalog service for Project Zero App e-commerce platform. Provides REST API endpoints for browsing, searching, and filtering products with admin management capabilities. Built using Python FastAPI with SQLAlchemy ORM, SQLite database, and integration with auth service for admin operations.

## Technical Context
**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, uvicorn
**Storage**: SQLite (development), PostgreSQL (production)
**Testing**: pytest with TestClient for FastAPI
**Target Platform**: Linux server (containerized)
**Project Type**: single - microservice following auth-service pattern
**Performance Goals**: Standard web API performance (<200ms p95)
**Constraints**: Stateless service, minimal dependencies, demo-focused
**Scale/Scope**: 20+ sample products, 4+ categories, CRUD operations
**Port**: 8004
**Auth Integration**: http://localhost:8001 for admin verification
**Features**: REST API, OpenAPI docs, CORS support, health checks, database seeding

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Simplicity First ✅
- Using established FastAPI pattern from auth-service (proven simple approach)
- SQLite for development (simple, no external dependencies)
- Minimal dependencies: FastAPI, SQLAlchemy, Pydantic, uvicorn
- Single responsibility: Product catalog management only

### Service Organization ✅
- Following services/{service-name}-service/ pattern
- Self-contained service with own dependencies
- Clear responsibility boundary (product catalog only)

### Technology Standards ✅
- Python + FastAPI + SQLAlchemy + Pydantic (matches constitution backend standards)
- JWT integration with existing auth service
- SQLite (dev) → PostgreSQL (prod) migration path

### Documentation Requirements ✅
- README.md will include: API docs, env vars, local setup, Docker instructions, testing
- Health check endpoints: /health and /health/ready
- OpenAPI documentation via FastAPI

### Security Standards ✅
- Auth integration for admin endpoints via existing auth service
- Input validation via Pydantic models
- No sensitive data exposure in logs

### Testing Standards ✅
- pytest with TestClient for FastAPI
- Contract tests for API endpoints
- Integration tests for database operations

**RESULT: PASS** - No constitutional violations detected

### Post-Design Re-evaluation ✅
After completing Phase 1 design (contracts, data model, quickstart):
- **API Design**: RESTful endpoints following OpenAPI 3.0 specification
- **Data Model**: Simple, normalized design with strategic indexing
- **Authentication**: Proper integration with auth service for admin operations
- **Documentation**: Comprehensive quickstart guide and API contracts
- **Testing Strategy**: Multi-tier approach (unit, integration, contract)
- **Simplicity**: Single-table design appropriate for demo scope
- **Consistency**: Matches auth-service patterns and structure

**FINAL RESULT: PASS** - Design maintains constitutional compliance

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

**Structure Decision**: Option 1 (Single project) - microservice following established auth-service pattern in services/ directory

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
- Based on OpenAPI contract → 6 endpoint contract test tasks [P]
- Based on Product entity → model creation task [P]
- Based on sample data requirement → database seeding task [P]
- Based on user stories → 6 integration test scenarios
- Implementation tasks following TDD to make tests pass
- Docker and deployment tasks matching constitutional requirements

**Specific Task Categories**:
1. **Setup Tasks**: Project structure, dependencies, configuration
2. **Model Tasks**: SQLAlchemy Product model, database migrations
3. **Contract Test Tasks**: One per endpoint (GET /products, POST /products, etc.)
4. **Service Layer Tasks**: Business logic, validation, database operations
5. **API Layer Tasks**: FastAPI routes, middleware, error handling
6. **Integration Tasks**: Auth service integration, health checks
7. **Data Tasks**: Sample data seeding, database initialization
8. **Documentation Tasks**: README, Docker files, environment setup

**Ordering Strategy**:
- TDD order: Contract tests → Models → Services → API routes
- Dependency order: Database models → Business logic → API endpoints
- Parallel opportunities: Contract tests [P], Documentation [P]
- Auth integration after basic CRUD operations are working

**Service Structure** (following auth-service pattern):
```
services/product-catalog-service/
├── src/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic models
│   ├── services/        # Business logic
│   ├── api/            # FastAPI routes
│   ├── database/       # DB connection, seeding
│   └── utils/          # Helpers, auth integration
├── tests/
│   ├── contract/       # API contract tests
│   ├── integration/    # End-to-end scenarios
│   └── unit/          # Model and service tests
├── main.py            # FastAPI application
├── requirements.txt   # Dependencies
├── Dockerfile        # Container definition
├── docker-compose.yml # Local development
└── README.md         # Service documentation
```

**Estimated Output**: 28-32 numbered, ordered tasks in tasks.md

**Key Implementation Dependencies**:
- Auth service running on port 8001 for integration testing
- SQLAlchemy models must be created before API routes
- Contract tests must be written before implementations
- Sample data seeding after model creation

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
- [x] Phase 0: Research complete (/plan command) ✅ research.md created
- [x] Phase 1: Design complete (/plan command) ✅ data-model.md, contracts/, quickstart.md created
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅ Strategy defined
- [ ] Phase 3: Tasks generated (/tasks command) - Ready for /tasks
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅ No violations found
- [x] Post-Design Constitution Check: PASS ✅ Design maintains compliance
- [x] All NEEDS CLARIFICATION resolved ✅ No ambiguities in Technical Context
- [x] Complexity deviations documented ✅ No deviations required

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
