# Tasks: API Gateway Service

**Input**: Design documents from `/specs/008-build-an-api/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Go with Gin framework, reverse proxy, middleware architecture
2. Load optional design documents:
   → data-model.md: ServiceConfig, RouteConfig, RateLimitPolicy entities
   → contracts/: gateway-api.yaml → contract test tasks
   → research.md: Technology decisions → setup tasks
3. Generate tasks by category:
   → Setup: Go project init, dependencies, configuration
   → Tests: contract tests, integration tests
   → Core: models, services, middleware
   → Integration: health checks, service registry, circuit breakers
   → Polish: Docker, documentation, comprehensive testing
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- Gateway service structure: `services/api-gateway-service/`
- Source code: `services/api-gateway-service/internal/`
- Tests: `services/api-gateway-service/tests/`
- Configuration: `services/api-gateway-service/config/`

## Phase 3.1: Setup
- [ ] T001 Create Go project structure at `services/api-gateway-service/` with proper module initialization
- [ ] T002 Initialize Go module with dependencies: Gin, Viper, slog, sony/gobreaker, golang.org/x/time/rate
- [ ] T003 [P] Configure Go linting and formatting tools (golangci-lint configuration)
- [ ] T004 [P] Setup Docker multi-stage build configuration in `services/api-gateway-service/Dockerfile`
- [ ] T005 [P] Create base configuration structure in `services/api-gateway-service/config/config.yaml`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T006 [P] Contract test GET /health in `services/api-gateway-service/tests/contract/test_health.go`
- [ ] T007 [P] Contract test GET /health/ready in `services/api-gateway-service/tests/contract/test_readiness.go`
- [ ] T008 [P] Contract test GET /gateway/services in `services/api-gateway-service/tests/contract/test_services.go`
- [ ] T009 [P] Contract test GET /gateway/routes in `services/api-gateway-service/tests/contract/test_routes.go`
- [ ] T010 [P] Contract test GET /gateway/metrics in `services/api-gateway-service/tests/contract/test_metrics.go`
- [ ] T011 [P] Contract test proxy routing to auth service in `services/api-gateway-service/tests/contract/test_auth_proxy.go`
- [ ] T012 [P] Contract test proxy routing to orders service in `services/api-gateway-service/tests/contract/test_orders_proxy.go`
- [ ] T013 [P] Integration test authentication flow through gateway in `services/api-gateway-service/tests/integration/test_auth_flow.go`
- [ ] T014 [P] Integration test rate limiting behavior in `services/api-gateway-service/tests/integration/test_rate_limiting.go`
- [ ] T015 [P] Integration test circuit breaker functionality in `services/api-gateway-service/tests/integration/test_circuit_breaker.go`
- [ ] T016 [P] Integration test service discovery and health checks in `services/api-gateway-service/tests/integration/test_service_discovery.go`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T017 [P] ServiceConfig model in `services/api-gateway-service/internal/models/service.go`
- [ ] T018 [P] RouteConfig model in `services/api-gateway-service/internal/models/route.go`
- [ ] T019 [P] RateLimitPolicy model in `services/api-gateway-service/internal/models/ratelimit.go`
- [ ] T020 [P] CircuitBreakerState model in `services/api-gateway-service/internal/models/circuit.go`
- [ ] T021 [P] RequestLogEntry model in `services/api-gateway-service/internal/models/logging.go`
- [ ] T022 [P] GatewayConfig model in `services/api-gateway-service/internal/models/config.go`
- [ ] T023 Configuration management service using Viper in `services/api-gateway-service/internal/config/manager.go`
- [ ] T024 Service registry implementation in `services/api-gateway-service/internal/registry/service_registry.go`
- [ ] T025 Health checker service in `services/api-gateway-service/internal/health/checker.go`
- [ ] T026 Rate limiting middleware using token bucket algorithm in `services/api-gateway-service/internal/middleware/ratelimit.go`
- [ ] T027 JWT authentication middleware with auth service integration in `services/api-gateway-service/internal/middleware/auth.go`
- [ ] T028 Circuit breaker implementation using sony/gobreaker in `services/api-gateway-service/internal/middleware/circuit.go`
- [ ] T029 CORS middleware configuration in `services/api-gateway-service/internal/middleware/cors.go`
- [ ] T030 Structured logging middleware with correlation IDs in `services/api-gateway-service/internal/middleware/logging.go`
- [ ] T031 Reverse proxy handler using net/http/httputil in `services/api-gateway-service/internal/proxy/handler.go`
- [ ] T032 Request routing engine in `services/api-gateway-service/internal/router/engine.go`

## Phase 3.4: Gateway Management Endpoints
- [ ] T033 GET /health endpoint implementation in `services/api-gateway-service/internal/handlers/health.go`
- [ ] T034 GET /health/ready endpoint implementation in `services/api-gateway-service/internal/handlers/readiness.go`
- [ ] T035 GET /gateway/services endpoint implementation in `services/api-gateway-service/internal/handlers/services.go`
- [ ] T036 GET /gateway/routes endpoint implementation in `services/api-gateway-service/internal/handlers/routes.go`
- [ ] T037 GET /gateway/metrics endpoint implementation in `services/api-gateway-service/internal/handlers/metrics.go`

## Phase 3.5: Core Integration
- [ ] T038 HTTP server setup with Gin framework in `services/api-gateway-service/internal/server/server.go`
- [ ] T039 Middleware chain configuration and registration in `services/api-gateway-service/internal/server/middleware.go`
- [ ] T040 Route registration and proxy setup in `services/api-gateway-service/internal/server/routes.go`
- [ ] T041 Graceful shutdown handling in `services/api-gateway-service/internal/server/shutdown.go`
- [ ] T042 Main application entry point in `services/api-gateway-service/cmd/gateway/main.go`

## Phase 3.6: Error Handling and Resilience
- [ ] T043 [P] Error response formatting and handling in `services/api-gateway-service/internal/errors/handler.go`
- [ ] T044 [P] Service timeout and retry logic in `services/api-gateway-service/internal/retry/backoff.go`
- [ ] T045 Request correlation ID generation and propagation in `services/api-gateway-service/internal/tracing/correlation.go`

## Phase 3.7: Docker and Deployment
- [ ] T046 Complete Docker multi-stage build with Alpine base in `services/api-gateway-service/Dockerfile`
- [ ] T047 Docker Compose integration for gateway service in project root `docker-compose.yml`
- [ ] T048 Environment variable configuration and validation in `services/api-gateway-service/internal/config/env.go`

## Phase 3.8: Comprehensive Testing
- [ ] T049 [P] Unit tests for service registry in `services/api-gateway-service/tests/unit/test_service_registry.go`
- [ ] T050 [P] Unit tests for rate limiting logic in `services/api-gateway-service/tests/unit/test_rate_limit.go`
- [ ] T051 [P] Unit tests for circuit breaker behavior in `services/api-gateway-service/tests/unit/test_circuit_breaker.go`
- [ ] T052 [P] Unit tests for request routing logic in `services/api-gateway-service/tests/unit/test_routing.go`
- [ ] T053 [P] Unit tests for authentication middleware in `services/api-gateway-service/tests/unit/test_auth_middleware.go`
- [ ] T054 Build and test Docker container locally to verify containerization
- [ ] T055 Start all services via docker-compose and verify gateway routing functionality
- [ ] T056 Test authentication flow end-to-end through gateway with auth service integration
- [ ] T057 Verify rate limiting works properly under load with multiple concurrent requests
- [ ] T058 Test circuit breaker functionality by simulating service failures

## Phase 3.9: Documentation and Polish
- [ ] T059 [P] Create comprehensive README.md for gateway service in `services/api-gateway-service/README.md`
- [ ] T060 [P] Update project root README.md with gateway-specific information including routing patterns and configuration
- [ ] T061 [P] Create deployment documentation with configuration examples in `services/api-gateway-service/docs/deployment.md`
- [ ] T062 [P] Performance optimization and memory management improvements
- [ ] T063 Remove code duplication and refactor for maintainability

## Dependencies
- Setup (T001-T005) before everything
- Tests (T006-T016) before implementation (T017-T045)
- Models (T017-T022) before services (T023-T032)
- Core services (T023-T032) before endpoints (T033-T037)
- Core implementation before integration (T038-T042)
- Error handling can be parallel with core integration
- Docker tasks (T046-T048) after core implementation
- Unit tests (T049-T053) can be parallel after respective implementations
- Integration testing (T054-T058) after Docker setup
- Documentation (T059-T063) after implementation complete

## Parallel Example
```
# Launch T006-T016 together (Contract and Integration Tests):
Task: "Contract test GET /health in services/api-gateway-service/tests/contract/test_health.go"
Task: "Contract test GET /health/ready in services/api-gateway-service/tests/contract/test_readiness.go"
Task: "Contract test GET /gateway/services in services/api-gateway-service/tests/contract/test_services.go"
Task: "Integration test authentication flow through gateway in services/api-gateway-service/tests/integration/test_auth_flow.go"

# Launch T017-T022 together (Data Models):
Task: "ServiceConfig model in services/api-gateway-service/internal/models/service.go"
Task: "RouteConfig model in services/api-gateway-service/internal/models/route.go"
Task: "RateLimitPolicy model in services/api-gateway-service/internal/models/ratelimit.go"

# Launch T049-T053 together (Unit Tests):
Task: "Unit tests for service registry in services/api-gateway-service/tests/unit/test_service_registry.go"
Task: "Unit tests for rate limiting logic in services/api-gateway-service/tests/unit/test_rate_limit.go"
Task: "Unit tests for circuit breaker behavior in services/api-gateway-service/tests/unit/test_circuit_breaker.go"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Focus on simplicity first, following constitutional principles
- All middleware must integrate seamlessly with Gin framework
- Circuit breaker should fail fast and provide meaningful error responses
- Rate limiting must be performant and not impact valid requests significantly
- Authentication integration must be secure and handle token validation properly

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - gateway-api.yaml endpoints → contract test tasks [P]
   - Each endpoint group → implementation task

2. **From Data Model**:
   - Each entity (ServiceConfig, RouteConfig, etc.) → model creation task [P]
   - Configuration management → service layer tasks

3. **From User Stories (Quickstart)**:
   - Each test scenario → integration test [P]
   - Setup scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Docker container build and testing included
- [x] Service routing verification via docker-compose included
- [x] Authentication flow testing through gateway included
- [x] Rate limiting verification included
- [x] Project root README.md update included with gateway-specific information

## Final Verification Tasks
The implementation must include these specific final verification steps:

1. **T054-T058**: Comprehensive integration testing
   - Docker container build and local testing
   - Full service routing verification via docker-compose
   - End-to-end authentication flow testing
   - Rate limiting behavior validation under load
   - Circuit breaker functionality with simulated failures

2. **T060**: Documentation update
   - Project root README.md updated with gateway-specific information
   - Routing patterns documented
   - Configuration options explained
   - Integration details provided

These tasks ensure the gateway is production-ready and properly documented for the Project Zero App ecosystem.