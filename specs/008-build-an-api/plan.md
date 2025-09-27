
# Implementation Plan: API Gateway Service

**Branch**: `008-build-an-api` | **Date**: 2025-09-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-build-an-api/spec.md`

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
Implement a high-performance API gateway service using Go with the Gin framework to serve as the single entry point for all client requests to the Project Zero App e-commerce platform. The gateway will handle request routing to backend microservices (auth:8001, profile:8002, products:8004, cart:8007, orders:8008, payments:8009), implement JWT authentication middleware, rate limiting using token bucket algorithm, CORS support, request logging, and circuit breaker patterns for resilience. The service will include service discovery with health checks, graceful shutdown handling, and comprehensive monitoring capabilities.

## Technical Context
**Language/Version**: Go 1.21+
**Primary Dependencies**: Gin framework, net/http reverse proxy, logrus for structured logging, rate limiting libraries
**Storage**: N/A (stateless gateway with in-memory service registry)
**Testing**: Go built-in testing package with testify for assertions
**Target Platform**: Linux server (containerized with Docker)
**Project Type**: single (microservice gateway)
**Performance Goals**: High throughput request routing with minimal latency overhead (<10ms p95 routing latency)
**Constraints**: Stateless design, graceful degradation when services unavailable, configurable via environment variables
**Scale/Scope**: Handle routing for 6 backend services with load balancing capabilities for horizontal scaling

**User-Provided Implementation Details**: Implement this API gateway using Go with the Gin framework for high performance and technology diversity in our microservices stack. Use Go modules for dependency management and structure the project following Go best practices. The service should run on port 8000 and act as the main entry point for all client requests. Include middleware for CORS, authentication, rate limiting (using token bucket algorithm), request logging, and error handling. Implement service discovery by maintaining a service registry with health checks for all downstream services (auth:8001, profile:8002, products:8004, cart:8007, orders:8008, payments:8009). Use Go's net/http reverse proxy for request forwarding and include circuit breaker pattern for resilience. Add structured logging with logrus or similar, configuration management via environment variables, graceful shutdown handling, and comprehensive health check endpoints. Ensure the service is containerized with Docker using multi-stage builds for optimal image size and integrates properly with the existing docker-compose.yml file. After implementation, test Docker container build, verify integration with all backend services via docker-compose, ensure proper request routing and authentication, and update the project root README.md with gateway information, routing patterns, and setup instructions.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I: Core Philosophy**
- ✅ Simplicity First: Go with Gin framework provides simple, straightforward API gateway implementation
- ✅ Functionality Over Architecture: Implementing essential gateway features without over-engineering
- ✅ Progressive Enhancement: Starting with core routing, auth, and rate limiting; extensible design for future needs
- ✅ Demo-Focused Development: Prioritizing demonstrable gateway functionality for Project Zero showcase

**Article II: Project Organization**
- ✅ Service Structure: Will be organized under `services/api-gateway-service/` following established pattern
- ✅ Infrastructure Organization: Docker configuration will integrate with existing `infrastructure/` structure
- ✅ Specification-Driven Structure: Following `.specify/` directory structure with specs, plan, tasks

**Article III: Docker Requirements**
- ✅ Containerization Mandate: Will include Dockerfile with multi-stage build, docker-compose integration
- ✅ Container Standards: Using official Go base image, non-root user, explicit port exposure

**Article IV: Documentation Standards**
- ✅ Service Documentation: Will include comprehensive README.md with API docs, config, setup instructions
- ✅ GCP Deployment Documentation: Will document GCP deployment using existing Terraform patterns
- ✅ Service Integration Documentation: Will document integration with all backend services and routing patterns

**Article V: Technology Standards**
- ✅ Backend Technologies: Using Go with Gin framework as specified in constitution for Go services
- ✅ Infrastructure Technologies: Docker containerization, integration with existing infrastructure

**Article VI: Security Standards**
- ✅ Authentication Requirements: JWT validation middleware, secure token handling
- ✅ Security Practices: Environment variable configuration, proper error handling without data leakage

**Article VII: Observability Requirements**
- ✅ Logging Standards: Structured JSON logging with logrus, request correlation IDs
- ✅ Health Monitoring: `/health` and `/health/ready` endpoints, integration with monitoring infrastructure

**Article VIII: Testing Standards**
- ✅ Test Coverage Requirements: Unit and integration tests using Go testing package with testify
- ✅ Testing Tools: Built-in Go testing package with testify as specified in constitution

**Constitutional Compliance**: PASS - No violations detected. Implementation aligns with all constitutional principles.

**Post-Design Re-evaluation**: PASS - After completing Phase 1 design artifacts:
- ✅ Data model maintains simplicity with clear entity definitions
- ✅ API contracts follow RESTful patterns without over-engineering
- ✅ Quickstart guide demonstrates progressive enhancement approach
- ✅ Technology choices remain consistent with constitutional standards
- ✅ No new complexity introduced that violates constitutional principles

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

**Structure Decision**: [DEFAULT to Option 1 unless Technical Context indicates web/mobile app]

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
- API Gateway specific task breakdown:
  1. Project structure and Go module initialization
  2. Configuration management implementation (Viper + validation)
  3. Core data structures (ServiceConfig, RouteConfig, etc.)
  4. HTTP server setup with Gin framework
  5. Reverse proxy implementation using net/http/httputil
  6. Service discovery and health checking
  7. Rate limiting middleware (token bucket algorithm)
  8. JWT authentication middleware with auth service integration
  9. Circuit breaker implementation using sony/gobreaker
  10. Structured logging with correlation IDs
  11. CORS middleware implementation
  12. Gateway management endpoints (/health, /gateway/services, etc.)
  13. Docker containerization with multi-stage builds
  14. Docker Compose integration
  15. Comprehensive error handling and graceful shutdown

**Ordering Strategy**:
- Foundation first: Project setup, configuration, basic server
- Core functionality: Routing, proxy, service discovery
- Middleware implementation: Auth, rate limiting, logging, CORS
- Resilience patterns: Circuit breakers, error handling
- Observability: Health checks, metrics, logging
- Containerization: Docker build and compose integration
- Testing: Unit tests, integration tests, contract validation
- Documentation: Service README, deployment guides

**Task Dependencies**:
- Configuration system must be implemented before any middleware
- Service discovery required before routing implementation
- Authentication middleware depends on auth service integration
- Circuit breakers require service registry for state management
- Health endpoints need service discovery for dependency checks

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**Testing Strategy**:
- Unit tests for each middleware component
- Integration tests for service routing and health checks
- Contract tests validating API specification compliance
- Load testing for rate limiting and circuit breaker behavior
- Docker integration tests for containerized deployment

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
- [x] research.md - Technology research and decisions
- [x] data-model.md - Core entities and data structures
- [x] contracts/gateway-api.yaml - OpenAPI specification
- [x] quickstart.md - Setup and testing guide
- [x] CLAUDE.md updated - Agent context with new technology stack

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
