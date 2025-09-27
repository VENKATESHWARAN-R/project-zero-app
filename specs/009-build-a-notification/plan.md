
# Implementation Plan: Notification Service

**Branch**: `009-build-a-notification` | **Date**: 2025-09-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-build-a-notification/spec.md`

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
Build a notification service for the Project Zero App e-commerce platform that handles all communication with users including email notifications, SMS notifications, and in-app notifications. The service sends notifications for key events like user registration welcome messages, order confirmations, payment confirmations, order status updates, password reset notifications, and promotional communications. The service integrates with existing services (auth, order, payment, user profile) and uses mock email/SMS providers for demonstration purposes. Implementation follows the constitution of simplicity first with stateless, lightweight design.

## Technical Context
**Language/Version**: Node.js with Express framework for technology diversity
**Primary Dependencies**: Express.js, Sequelize ORM, SQLite, Swagger/OpenAPI, bcrypt, jsonwebtoken
**Storage**: SQLite database for local development with Sequelize ORM models
**Testing**: Jest with supertest for Express.js API testing
**Target Platform**: Linux server (port 8011) with Docker containerization
**Project Type**: single - microservice component in larger platform
**Performance Goals**: Mock email/SMS delivery simulation, realistic notification workflows
**Constraints**: Stateless operation, lightweight design, integration with existing services
**Scale/Scope**: Demo-focused with mock providers, comprehensive API documentation, Docker integration

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity First**: ✅ PASS - Using Node.js with Express follows established patterns, SQLite for local development, mock providers instead of complex integrations
**Functionality Over Architecture**: ✅ PASS - Focusing on core notification delivery functionality first, minimal viable service approach
**Progressive Enhancement**: ✅ PASS - Starting with basic notification delivery, templates, and history; can enhance with advanced features later
**Demo-Focused Development**: ✅ PASS - Mock email/SMS providers for demonstration, realistic workflows without production complexity
**Service Structure**: ✅ PASS - Following services/{service-name}-service/ pattern under services/notification-service/
**Docker Requirements**: ✅ PASS - Dockerfile, health checks, non-root user, integration with docker-compose.yml
**Technology Standards**: ✅ PASS - Node.js + Express.js + Sequelize aligns with constitution's Node.js service standards
**Security Standards**: ✅ PASS - JWT authentication integration, input validation, secure patterns
**Testing Standards**: ✅ PASS - Jest + supertest for API testing, contract validation

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

**Structure Decision**: Option 1 (Single project) - This is a microservice component that follows the services/ directory pattern

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
- Generate Sequelize model creation tasks for each entity [P]
- Generate Express.js route implementation tasks from API contracts [P]
- Generate contract test tasks for each endpoint [P]
- Generate service integration tasks for auth, user profile, order, payment services
- Generate mock provider implementation tasks for email/SMS simulation
- Generate Docker containerization and health check tasks
- Generate comprehensive testing tasks from quickstart scenarios

**Ordering Strategy**:
- TDD order: Contract tests → Models → Services → Routes → Integration
- Dependency order: Database setup → Models → Services → API routes → Tests → Docker
- Mark [P] for parallel execution (independent components like models, mock providers)
- Sequential dependencies: Auth integration → Other service integrations → Full system tests

**Specific Task Categories**:
1. **Infrastructure Tasks** (Sequential):
   - Project setup with Node.js/Express structure
   - Database schema creation with Sequelize
   - Environment configuration and Docker setup

2. **Model Tasks** [P] (Parallel):
   - Notification model with validations
   - NotificationTemplate model
   - NotificationHistory model
   - UserNotificationPreference model
   - ScheduledNotification model

3. **Service Integration Tasks** (Sequential):
   - JWT authentication middleware
   - Auth service client integration
   - User profile service integration
   - Mock email provider implementation
   - Mock SMS provider implementation

4. **API Implementation Tasks** [P] (Parallel per route group):
   - Health check endpoints
   - Notification CRUD operations
   - Template management endpoints
   - User preference endpoints
   - Scheduled notification endpoints

5. **Testing Tasks**:
   - Contract tests for all API endpoints
   - Integration tests for service communication
   - End-to-end quickstart scenario validation
   - Performance and error handling tests

6. **Documentation and Deployment**:
   - Swagger/OpenAPI documentation generation
   - Docker container optimization
   - Service README completion
   - Integration with docker-compose.yml

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md

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
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
