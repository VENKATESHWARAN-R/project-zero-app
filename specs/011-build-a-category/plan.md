
# Implementation Plan: Category Management Service

**Branch**: `011-build-a-category` | **Date**: 2025-09-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-build-a-category/spec.md`

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
Category management service for Product Zero App e-commerce platform providing hierarchical product categorization with parent-child relationships, category metadata management, admin authentication, and seamless integration with existing product catalog and auth services.

## Technical Context
**Language/Version**: Node.js 18+ with Express framework
**Primary Dependencies**: Express.js, Sequelize ORM, express-validator, winston, cors, bcrypt, jsonwebtoken, swagger-jsdoc, swagger-ui-express
**Storage**: SQLite (development), PostgreSQL (production)
**Testing**: Jest with supertest for integration testing
**Target Platform**: Docker containers on Linux servers, port 8005
**Project Type**: Microservice - single backend service
**Performance Goals**: Handle category hierarchies up to 5 levels deep, support 1000+ req/s for category reads
**Constraints**: <200ms p95 response time for category queries, prevent circular hierarchies, maintain referential integrity
**Scale/Scope**: Support 10k+ categories, unlimited products per category, admin-only category management

**Implementation Details**: Implement this category service using Node.js with Express framework and yarn package manager for dependency management, following our established patterns for simplicity and integration. Use SQLite database for local development with Sequelize ORM to maintain consistency with our other Node.js services. The service should run on port 8005 and expose REST API endpoints with comprehensive Swagger/OpenAPI documentation automatically generated and saved as swagger.json in the service folder. Include Sequelize models for categories with self-referencing relationships for hierarchical structure, category metadata, and category-product associations. The service should integrate with product catalog service (port 8004) for product-category relationships and auth service (port 8001) for admin verification. Include proper request validation using express-validator, comprehensive error handling, structured logging with winston, health check endpoints, and CORS support for frontend integration. Implement category hierarchy management with depth limits to prevent infinite nesting, category image/icon support via URLs, and category-based product filtering enhancements. Ensure the service is containerized with Docker and integrates seamlessly with the existing docker-compose.yml file. Use yarn for all package management operations and follow Node.js best practices for project structure. After implementation, verify Docker container builds successfully, test integration with product catalog and auth services via docker-compose, confirm Swagger documentation is generated and accessible at /docs endpoint with swagger.json saved in service folder, and update the project root README.md with detailed service information including category hierarchy patterns, API endpoints, and integration details.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I: Core Philosophy**
- ✅ Simplicity First: Using proven Express.js + Sequelize stack, minimal complexity
- ✅ Functionality Over Architecture: Implementing MVP category management, no over-engineering
- ✅ Progressive Enhancement: Starting with basic hierarchy, can add advanced features later
- ✅ Demo-Focused Development: Showcasing microservice patterns and AI integration

**Article II: Project Organization**
- ✅ Service Structure: Following `services/category-service/` pattern
- ✅ Infrastructure Organization: Will integrate with existing docker-compose setup
- ✅ Specification-Driven: Following .specify/ structure with plan.md, spec.md

**Article III: Docker Requirements**
- ✅ Containerization Mandate: Will include Dockerfile, docker-compose.yml, .dockerignore
- ✅ Container Standards: Using official Node.js base image, non-root user, explicit ports

**Article IV: Documentation Standards**
- ✅ Service Documentation: Will include comprehensive README.md with API docs
- ✅ Service Integration: Will document dependencies on auth and product services
- ✅ GCP Deployment: Will include deployment instructions

**Article V: Technology Standards**
- ✅ Backend Technologies: Using Node.js + Express.js + Sequelize (constitutionally approved)
- ✅ Database: SQLite (dev) → PostgreSQL (prod) as specified
- ✅ Infrastructure: Docker + Docker Compose for local development

**Article VI: Security Standards**
- ✅ Authentication: JWT integration with auth service for admin operations
- ✅ Security Practices: Input validation, secure error handling, no secrets in code

**Article VII: Observability Requirements**
- ✅ Logging Standards: Winston structured JSON logging with correlation IDs
- ✅ Health Monitoring: /health and /health/ready endpoints

**Article VIII: Testing Standards**
- ✅ Test Coverage: Jest + supertest, contract tests, integration tests
- ✅ Testing Tools: Jest (constitutionally approved for Node.js)

**RESULT: PASS** - No constitutional violations detected. Approach aligns with simplicity-first principles and established technology standards.

## Project Structure

### Documentation (this feature)
```
specs/011-build-a-category/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Microservice structure (following existing pattern)
services/category-service/
├── src/
│   ├── models/          # Sequelize models (Category, CategoryProduct)
│   ├── routes/          # Express route handlers
│   ├── middleware/      # Auth, validation, error handling
│   ├── services/        # Business logic services
│   ├── config/          # Database, app configuration
│   └── utils/           # Helper functions, logging
├── tests/
│   ├── contract/        # API contract tests
│   ├── integration/     # Service integration tests
│   └── unit/            # Unit tests
├── package.json         # yarn dependencies
├── Dockerfile           # Container image
├── README.md            # Service documentation
├── swagger.json         # Generated API documentation
└── .dockerignore        # Docker ignore file
```

**Structure Decision**: Microservice pattern (Option 1 adapted for service architecture) - single backend service following established `services/` directory pattern.

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
- Each API endpoint → contract test task [P]
- Category entity → Sequelize model creation task [P]
- Each functional requirement → integration test task
- Implementation tasks to make tests pass
- Docker containerization and deployment tasks
- Documentation and integration tasks

**Specific Task Categories**:
1. **Setup & Configuration** (5-7 tasks):
   - Project initialization with yarn
   - Sequelize setup and configuration
   - Environment variable configuration
   - Logging setup with Winston
   - Error handling middleware

2. **Database & Models** (4-6 tasks):
   - Database migration for categories table
   - Sequelize Category model with associations
   - Model validation and business rules
   - Database seeding for testing

3. **API Contract Tests** (8-10 tasks):
   - Health endpoints contract tests [P]
   - Category CRUD endpoints contract tests [P]
   - Category hierarchy endpoints contract tests [P]
   - Product integration endpoints contract tests [P]
   - Authentication middleware tests [P]

4. **Service Implementation** (8-12 tasks):
   - Category service business logic
   - Hierarchy validation service
   - Auth integration middleware
   - Product catalog integration service
   - Express route handlers
   - Input validation with express-validator

5. **Documentation & Integration** (4-6 tasks):
   - Swagger/OpenAPI documentation generation
   - Docker containerization
   - Docker Compose integration
   - Service README documentation

**Ordering Strategy**:
- TDD order: Contract tests before implementation
- Dependency order: Models → Services → Routes → Integration
- Mark [P] for parallel execution (independent files)
- Database tasks before service implementation
- Documentation tasks at the end

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**Key Dependencies**:
- Auth service integration tests depend on auth service contract
- Product integration tests depend on product catalog service
- Docker tasks depend on all implementation completion
- Documentation tasks depend on API implementation

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
- [x] plan.md - Implementation plan with technical context and approach
- [x] research.md - Technical decisions and integration patterns resolved
- [x] data-model.md - Category entity model and database schema design
- [x] contracts/api-specification.yaml - Complete OpenAPI specification
- [x] quickstart.md - Step-by-step validation guide for all functional requirements
- [x] CLAUDE.md - Updated agent context with category service details
- [ ] tasks.md - Detailed implementation tasks (pending /tasks command)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
