# Tasks: Shopping Cart Service

**Input**: Design documents from `/specs/003-build-a-shopping/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/cart-api.yaml, quickstart.md

## Execution Flow
```
1. Load plan.md: Node.js/Express, Sequelize ORM, SQLite/PostgreSQL
2. Load data-model.md: Cart and CartItem entities with relationships
3. Load contracts/cart-api.yaml: 7 endpoints (health, cart operations)
4. Load quickstart.md: Test scenarios and integration flows
5. Generate 30 ordered tasks with TDD approach
6. Mark [P] for parallel execution (different files)
7. Dependencies: Setup → Tests → Models → Services → Endpoints → Polish
```

## Path Convention: Single Project (Microservice)
- **Source**: `services/cart-service/src/`
- **Tests**: `services/cart-service/tests/`
- **Config**: `services/cart-service/` (package.json, .env, etc.)

## Phase 3.1: Project Setup

- [X] T001 Create cart service directory structure at services/cart-service/
- [X] T002 Initialize Node.js project with package.json using yarn
- [X] T003 [P] Install core dependencies (express, sequelize, sqlite3, express-validator)
- [X] T004 [P] Install dev dependencies (jest, supertest, nodemon)
- [X] T005 [P] Configure ESLint and Prettier for code standards
- [X] T006 [P] Create .env.example with required environment variables
- [X] T007 [P] Setup basic project structure (src/, tests/, config/)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Specification)
- [X] T008 [P] Contract test GET /health in tests/contract/test_health.js
- [X] T009 [P] Contract test GET /health/ready in tests/contract/test_ready.js
- [X] T010 [P] Contract test POST /cart/add in tests/contract/test_cart_add.js
- [X] T011 [P] Contract test GET /cart in tests/contract/test_cart_get.js
- [X] T012 [P] Contract test PUT /cart/items/:product_id in tests/contract/test_cart_update.js
- [X] T013 [P] Contract test DELETE /cart/items/:product_id in tests/contract/test_cart_remove.js
- [X] T014 [P] Contract test DELETE /cart in tests/contract/test_cart_clear.js

### Integration Tests (User Stories)
- [X] T015 [P] Integration test complete shopping flow in tests/integration/test_shopping_flow.js
- [X] T016 [P] Integration test authentication middleware in tests/integration/test_auth_integration.js
- [X] T017 [P] Integration test product validation flow in tests/integration/test_product_validation.js
- [X] T018 [P] Integration test cart persistence and expiry in tests/integration/test_cart_lifecycle.js

## Phase 3.3: Database Layer (ONLY after tests are failing)

### Data Models
- [X] T019 [P] Cart model with Sequelize in src/models/Cart.js
- [X] T020 [P] CartItem model with Sequelize in src/models/CartItem.js
- [X] T021 Setup model associations and database connection in src/models/index.js
- [X] T022 Database migration for Cart table in migrations/001-create-cart.js
- [X] T023 Database migration for CartItem table in migrations/002-create-cart-item.js

## Phase 3.4: Business Logic Services

### Core Services
- [X] T024 [P] Auth service integration client in src/services/authService.js
- [X] T025 [P] Product service integration client in src/services/productService.js
- [X] T026 CartService for cart operations in src/services/cartService.js
- [X] T027 [P] Logger service with Winston in src/services/logger.js

## Phase 3.5: API Layer Implementation

### Middleware
- [X] T028 [P] Authentication middleware for JWT verification in src/middleware/auth.js
- [X] T029 [P] Request validation middleware using express-validator in src/middleware/validation.js
- [X] T030 [P] Error handling middleware in src/middleware/errorHandler.js
- [X] T031 [P] Request logging middleware in src/middleware/requestLogger.js

### Route Handlers
- [X] T032 Health check endpoints in src/routes/health.js
- [X] T033 Cart operations routes in src/routes/cart.js
- [X] T034 Main Express app setup in src/app.js
- [X] T035 Server startup script in src/server.js

## Phase 3.6: Configuration and Environment

- [X] T036 [P] Environment configuration loader in src/config/env.js
- [X] T037 [P] Database configuration for Sequelize in src/config/database.js
- [X] T038 [P] Service URLs configuration in src/config/services.js

## Phase 3.7: Integration and Polish

### Testing Infrastructure
- [X] T039 [P] Jest configuration and test setup in jest.config.js
- [X] T040 [P] Test database setup and teardown in tests/setup.js
- [X] T041 [P] Mock services for testing in tests/mocks/

### Performance and Quality
- [X] T042 [P] Unit tests for cart service logic in tests/unit/test_cart_service.js
- [X] T043 [P] Unit tests for validation helpers in tests/unit/test_validation.js
- [X] T044 [P] Performance tests for cart operations in tests/performance/test_cart_performance.js
- [X] T045 [P] Package.json scripts for dev, test, build in package.json

### Documentation and Deployment
- [X] T046 [P] Service README with setup instructions in README.md
- [X] T047 [P] Dockerfile for containerization in Dockerfile
- [X] T048 [P] Docker compose integration in docker-compose.yml
- [X] T049 Execute quickstart.md validation scenarios manually
- [X] T050 Run full test suite and validate <200ms response times

## Dependencies

### Critical Path
- Setup (T001-T007) before all other phases
- Contract tests (T008-T014) before any implementation
- Integration tests (T015-T018) before business logic
- Models (T019-T023) before services (T024-T027)
- Services before API layer (T028-T035)
- Core implementation before polish (T039-T050)

### Specific Dependencies
- T021 requires T019, T020 (model associations need models)
- T026 requires T019, T020, T024, T025 (CartService needs models and external services)
- T033 requires T026, T028, T029 (routes need services and middleware)
- T034 requires T028-T033 (app setup needs all middleware and routes)
- T042, T043 require T026 (unit tests need service implementation)

## Parallel Execution Examples

### Phase 3.2 - All Contract Tests Together
```bash
# Launch contract tests in parallel (different files):
Task: "Contract test GET /health in tests/contract/test_health.js"
Task: "Contract test POST /cart/add in tests/contract/test_cart_add.js"
Task: "Contract test GET /cart in tests/contract/test_cart_get.js"
Task: "Contract test PUT /cart/items/:product_id in tests/contract/test_cart_update.js"
```

### Phase 3.3 - Data Layer Setup
```bash
# Launch model creation in parallel (different files):
Task: "Cart model with Sequelize in src/models/Cart.js"
Task: "CartItem model with Sequelize in src/models/CartItem.js"
```

### Phase 3.4 - Service Layer
```bash
# Launch service integrations in parallel (different files):
Task: "Auth service integration client in src/services/authService.js"
Task: "Product service integration client in src/services/productService.js"
Task: "Logger service with Winston in src/services/logger.js"
```

### Phase 3.5 - Middleware Setup
```bash
# Launch middleware in parallel (different files):
Task: "Authentication middleware for JWT verification in src/middleware/auth.js"
Task: "Request validation middleware using express-validator in src/middleware/validation.js"
Task: "Error handling middleware in src/middleware/errorHandler.js"
Task: "Request logging middleware in src/middleware/requestLogger.js"
```

## Task Generation Rules Applied

1. **From cart-api.yaml contracts**: 7 endpoints → 7 contract tests (T008-T014) [P]
2. **From data-model.md entities**: Cart, CartItem → 2 model tasks (T019-T020) [P]
3. **From quickstart.md user stories**: 4 integration scenarios → 4 integration tests (T015-T018) [P]
4. **From research.md decisions**: Express, Sequelize, Winston → corresponding implementation tasks
5. **TDD ordering**: All tests (T008-T018) before implementation (T019+)
6. **File independence**: Tasks marked [P] modify different files and can run in parallel

## Validation Checklist

- [x] All 7 contract endpoints have corresponding tests (T008-T014)
- [x] All 2 entities (Cart, CartItem) have model tasks (T019-T020)
- [x] All contract/integration tests (T008-T018) come before implementation (T019+)
- [x] Parallel tasks [P] are truly independent (different files)
- [x] Each task specifies exact file path in services/cart-service/
- [x] No task modifies same file as another [P] task
- [x] Dependencies clearly specified (critical path defined)
- [x] Test-driven development enforced (tests must fail before implementation)

## Completion Criteria

**Definition of Done for this feature:**
1. All 50 tasks completed in order
2. All contract tests pass (API specification compliance)
3. All integration tests pass (user story validation)
4. Service responds <200ms for cart operations
5. Quickstart.md scenarios execute successfully
6. Service integrates with auth (port 8001) and product (port 8004) services
7. Health checks return proper status
8. Code coverage >80% for business logic
9. ESLint passes with zero violations
10. Service runs on port 8007 with proper logging

This task breakdown provides 30-60 minute focused tasks following constitutional simplicity principles while ensuring comprehensive test coverage and proper service integration patterns.