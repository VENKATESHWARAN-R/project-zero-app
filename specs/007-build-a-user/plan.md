
# Implementation Plan: User Profile Management Service

**Branch**: `007-build-a-user` | **Date**: 2025-09-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-build-a-user/spec.md`

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
Implement a comprehensive user profile management service for the Project Zero App e-commerce platform using Python with FastAPI framework. The service manages user profiles, shipping/billing addresses, preferences, and activity tracking. It integrates with the auth service for user verification and provides address data to the order service during checkout. Key features include profile CRUD operations, multi-address management with defaults, notification preferences, and comprehensive activity logging with admin support capabilities.

## Technical Context
**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, uvicorn, pytest
**Storage**: SQLite (local development), PostgreSQL (production)
**Testing**: pytest with TestClient for FastAPI, coverage testing
**Target Platform**: Linux server (containerized)
**Project Type**: single microservice - determines source structure
**Performance Goals**: <200ms response time, 1000 req/s for profile operations
**Constraints**: <200ms p95 latency, stateless service design, JWT auth integration
**Scale/Scope**: Support 10k+ users, comprehensive profile data, multi-address management

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**✅ Article I: Core Philosophy**
- ✅ Simplicity First: Using proven FastAPI + SQLAlchemy stack, following existing service patterns
- ✅ Functionality Over Architecture: Implementing MVP profile service with essential features first
- ✅ Progressive Enhancement: Starting with basic CRUD, can extend with complex features later
- ✅ Demo-Focused Development: Prioritizing demonstrable profile management over production optimizations

**✅ Article II: Project Organization**
- ✅ Service Structure: Following `services/user-profile-service/` pattern consistent with existing services
- ✅ Specification-Driven Structure: Using proper `.specify/` directory structure with specs
- ✅ Infrastructure Organization: Will include docker-compose integration

**✅ Article III: Docker Requirements**
- ✅ Containerization Mandate: Will include Dockerfile, docker-compose.yml, .dockerignore, health endpoints
- ✅ Container Standards: Using official Python base image, non-root user, explicit port exposure

**✅ Article V: Technology Standards**
- ✅ Backend Technologies: Using FastAPI + SQLAlchemy + Pydantic + PyJWT (constitutional compliance)
- ✅ Database: SQLite (dev) + PostgreSQL (prod) as specified in constitution

**✅ Article VI: Security Standards**
- ✅ Authentication Requirements: JWT integration with auth service, input validation, proper error handling
- ✅ Security Practices: Environment variables for secrets, no sensitive data logging

**✅ Article VII: Observability Requirements**
- ✅ Logging Standards: Structured JSON logging, proper log levels, no sensitive data
- ✅ Health Monitoring: `/health` and `/health/ready` endpoints, basic metrics

**✅ Article VIII: Testing Standards**
- ✅ Test Coverage Requirements: Unit tests, integration tests, API contract tests
- ✅ Testing Tools: pytest with TestClient for FastAPI (constitutional compliance)

**Initial Gate Status: PASS** - No constitutional violations detected

**Post-Design Constitutional Review:**
- ✅ **Simplicity**: Data model follows established SQLAlchemy patterns without over-engineering
- ✅ **Service Structure**: Maintains consistency with existing microservice organization
- ✅ **Technology Compliance**: Uses constitutional backend stack (FastAPI + SQLAlchemy + Pydantic)
- ✅ **Security Standards**: JWT integration, input validation, audit logging implemented
- ✅ **Testing Standards**: Contract, integration, and unit tests planned
- ✅ **Docker Standards**: Multi-stage build, health checks, non-root user planned
- ✅ **Observability**: Structured logging, health endpoints, metrics readiness

**Post-Design Gate Status: PASS** - Design maintains constitutional compliance

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

**Structure Decision**: Option 1 (Single project) - Microservice architecture with dedicated service directory under `services/user-profile-service/`

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
- Each SQLAlchemy model → model creation task [P]
- Each user story from spec → integration test task
- Service layer tasks for business logic implementation
- FastAPI router implementation tasks
- Docker containerization and integration tasks

**Ordering Strategy**:
- TDD order: Contract tests → Models → Services → API routes → Integration tests
- Dependency order: Database models → Business services → API layer → Docker integration
- Mark [P] for parallel execution (independent files and services)

**Key Task Categories**:
1. **Database Layer**: SQLAlchemy models (UserProfile, Address, UserPreferences, ActivityLog)
2. **API Contracts**: OpenAPI validation tests for all endpoints
3. **Business Logic**: Profile service, address service, preference service
4. **API Layer**: FastAPI routers for profiles, addresses, preferences, admin
5. **Authentication**: JWT integration and user verification
6. **Testing**: Unit tests, integration tests, contract tests
7. **Docker**: Containerization, health checks, docker-compose integration
8. **Documentation**: Service README, API documentation updates

**Estimated Output**: 30-35 numbered, dependency-ordered tasks in tasks.md

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

**Artifacts Generated**:
- [x] research.md - Technical research and patterns analysis
- [x] data-model.md - Database schema and entity relationships
- [x] contracts/openapi.yaml - Complete API specification
- [x] quickstart.md - Service validation and testing guide
- [x] CLAUDE.md - Updated agent context

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
