# Tasks: Payment Processing Service

**Input**: Design documents from `/specs/006-build-a-payment/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.13+ with FastAPI framework
   → Libraries: SQLAlchemy, Pydantic, bcrypt, PyJWT, httpx, python-jose, passlib, alembic
   → Structure: Single microservice in services/payment-service/
2. Load design documents:
   → data-model.md: Payment Transaction, Payment Method, Payment Status History, Webhook Event
   → contracts/payment-api.yaml: 8 endpoints with comprehensive API specification
   → research.md: Mock payment processing with realistic simulation features
3. Generate tasks by category:
   → Setup: project structure, dependencies, Docker configuration
   → Tests: contract tests for all 8 endpoints, integration tests for payment flows
   → Core: 4 SQLAlchemy models, payment processor, validation services
   → Integration: auth service client, order service client, webhook simulation
   → Polish: unit tests, performance optimization, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel execution
   → Same file = sequential (no [P])
   → Contract tests before implementation (TDD approach)
5. Number tasks sequentially (T001-T032)
6. Generate dependency graph with critical path through models → services → endpoints
7. Create parallel execution examples for independent tasks
8. Validation: All 8 endpoints have tests, all 4 entities have models, comprehensive coverage
9. Return: SUCCESS (32 tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single microservice**: `services/payment-service/src/`, `services/payment-service/tests/`
- Paths follow existing Python service pattern in the project

## Phase 3.1: Setup & Infrastructure

- [ ] T001 Create payment service project structure at `services/payment-service/` following existing Python service pattern
- [ ] T002 Initialize Python project with FastAPI dependencies in `services/payment-service/pyproject.toml`
- [ ] T003 [P] Configure Docker setup with `services/payment-service/Dockerfile` and `services/payment-service/docker-compose.yml`
- [ ] T004 [P] Set up environment configuration in `services/payment-service/.env.example`
- [ ] T005 [P] Configure linting and formatting tools (Black, Flake8, mypy) in `services/payment-service/pyproject.toml`
- [ ] T006 [P] Create database initialization script in `services/payment-service/src/models/database.py`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (from payment-api.yaml)
- [ ] T007 [P] Contract test POST /api/v1/payments in `services/payment-service/tests/contract/test_payments_post.py`
- [ ] T008 [P] Contract test GET /api/v1/payments in `services/payment-service/tests/contract/test_payments_get.py`
- [ ] T009 [P] Contract test GET /api/v1/payments/{payment_id} in `services/payment-service/tests/contract/test_payment_details.py`
- [ ] T010 [P] Contract test GET /api/v1/payments/{payment_id}/status in `services/payment-service/tests/contract/test_payment_status.py`
- [ ] T011 [P] Contract test POST /api/v1/payment-methods in `services/payment-service/tests/contract/test_payment_methods_post.py`
- [ ] T012 [P] Contract test GET /api/v1/payment-methods in `services/payment-service/tests/contract/test_payment_methods_get.py`
- [ ] T013 [P] Contract test DELETE /api/v1/payment-methods/{method_id} in `services/payment-service/tests/contract/test_payment_methods_delete.py`
- [ ] T014 [P] Contract test POST /api/v1/webhooks/payment in `services/payment-service/tests/contract/test_webhooks.py`

### Integration Tests (from quickstart.md scenarios)
- [ ] T015 [P] Integration test successful payment flow in `services/payment-service/tests/integration/test_payment_flow.py`
- [ ] T016 [P] Integration test payment failure scenarios in `services/payment-service/tests/integration/test_payment_failures.py`
- [ ] T017 [P] Integration test payment method management in `services/payment-service/tests/integration/test_payment_methods.py`
- [ ] T018 [P] Integration test webhook simulation in `services/payment-service/tests/integration/test_webhook_simulation.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (from data-model.md)
- [ ] T019 [P] Payment Transaction model in `services/payment-service/src/models/payment.py`
- [ ] T020 [P] Payment Method model in `services/payment-service/src/models/payment_method.py`
- [ ] T021 [P] Payment Status History model in `services/payment-service/src/models/payment_status_history.py`
- [ ] T022 [P] Webhook Event model in `services/payment-service/src/models/webhook_event.py`

### Business Logic Services
- [ ] T023 Mock payment processor with realistic simulation in `services/payment-service/src/services/payment_processor.py`
- [ ] T024 Payment validation service in `services/payment-service/src/services/payment_validator.py`
- [ ] T025 Webhook simulator with async delivery in `services/payment-service/src/services/webhook_simulator.py`

### API Endpoints
- [ ] T026 FastAPI application setup and health endpoints in `services/payment-service/src/main.py`
- [ ] T027 Payment processing endpoints in `services/payment-service/src/api/payments.py`
- [ ] T028 Payment method management endpoints in `services/payment-service/src/api/payment_methods.py`
- [ ] T029 Webhook endpoints in `services/payment-service/src/api/webhooks.py`

## Phase 3.4: Integration & Security

- [ ] T030 Auth service integration client in `services/payment-service/src/integrations/auth_service.py`
- [ ] T031 Order service integration client in `services/payment-service/src/integrations/order_service.py`
- [ ] T032 JWT authentication middleware and security utilities in `services/payment-service/src/utils/security.py`

## Phase 3.5: Polish & Documentation

- [ ] T033 [P] Unit tests for payment processor in `services/payment-service/tests/unit/test_payment_processor.py`
- [ ] T034 [P] Unit tests for payment validator in `services/payment-service/tests/unit/test_payment_validator.py`
- [ ] T035 [P] Unit tests for webhook simulator in `services/payment-service/tests/unit/test_webhook_simulator.py`
- [ ] T036 [P] Performance tests for concurrent payment processing in `services/payment-service/tests/performance/test_concurrent_payments.py`
- [ ] T037 [P] Service documentation in `services/payment-service/README.md`
- [ ] T038 [P] Structured logging setup in `services/payment-service/src/utils/logging.py`

## Dependencies

**Critical Path**: T001-T006 → T007-T018 → T019-T022 → T023-T025 → T026-T029 → T030-T032 → T033-T038

### Phase Dependencies
- **Setup** (T001-T006): Must complete before any other work
- **Tests** (T007-T018): Must complete and FAIL before implementation
- **Models** (T019-T022): Required before services and endpoints
- **Services** (T023-T025): Required before API endpoints
- **API** (T026-T029): Requires models and services
- **Integration** (T030-T032): Can run after basic API structure exists
- **Polish** (T033-T038): Final phase after core functionality

### Specific Dependencies
- T019-T022 (models) block T023-T025 (services)
- T023-T025 (services) block T026-T029 (endpoints)
- T030-T032 (integrations) require T026 (main app setup)
- T033-T038 (polish) require corresponding implementation tasks

## Parallel Execution Examples

### Phase 3.1 Setup (can run T003-T006 in parallel after T001-T002)
```bash
# After T001-T002 complete:
Task: "Configure Docker setup with services/payment-service/Dockerfile"
Task: "Set up environment configuration in services/payment-service/.env.example"
Task: "Configure linting and formatting tools in services/payment-service/pyproject.toml"
Task: "Create database initialization script in services/payment-service/src/models/database.py"
```

### Phase 3.2 Contract Tests (T007-T014 can run in parallel)
```bash
# All contract tests are independent:
Task: "Contract test POST /api/v1/payments in services/payment-service/tests/contract/test_payments_post.py"
Task: "Contract test GET /api/v1/payments in services/payment-service/tests/contract/test_payments_get.py"
Task: "Contract test GET /api/v1/payments/{payment_id} in services/payment-service/tests/contract/test_payment_details.py"
Task: "Contract test GET /api/v1/payments/{payment_id}/status in services/payment-service/tests/contract/test_payment_status.py"
Task: "Contract test POST /api/v1/payment-methods in services/payment-service/tests/contract/test_payment_methods_post.py"
Task: "Contract test GET /api/v1/payment-methods in services/payment-service/tests/contract/test_payment_methods_get.py"
Task: "Contract test DELETE /api/v1/payment-methods/{method_id} in services/payment-service/tests/contract/test_payment_methods_delete.py"
Task: "Contract test POST /api/v1/webhooks/payment in services/payment-service/tests/contract/test_webhooks.py"
```

### Phase 3.2 Integration Tests (T015-T018 can run in parallel)
```bash
# All integration tests are independent:
Task: "Integration test successful payment flow in services/payment-service/tests/integration/test_payment_flow.py"
Task: "Integration test payment failure scenarios in services/payment-service/tests/integration/test_payment_failures.py"
Task: "Integration test payment method management in services/payment-service/tests/integration/test_payment_methods.py"
Task: "Integration test webhook simulation in services/payment-service/tests/integration/test_webhook_simulation.py"
```

### Phase 3.3 Models (T019-T022 can run in parallel)
```bash
# All models are independent:
Task: "Payment Transaction model in services/payment-service/src/models/payment.py"
Task: "Payment Method model in services/payment-service/src/models/payment_method.py"
Task: "Payment Status History model in services/payment-service/src/models/payment_status_history.py"
Task: "Webhook Event model in services/payment-service/src/models/webhook_event.py"
```

### Phase 3.5 Polish (T033-T038 can run in parallel)
```bash
# All polish tasks are independent:
Task: "Unit tests for payment processor in services/payment-service/tests/unit/test_payment_processor.py"
Task: "Unit tests for payment validator in services/payment-service/tests/unit/test_payment_validator.py"
Task: "Unit tests for webhook simulator in services/payment-service/tests/unit/test_webhook_simulator.py"
Task: "Performance tests for concurrent payment processing in services/payment-service/tests/performance/test_concurrent_payments.py"
Task: "Service documentation in services/payment-service/README.md"
Task: "Structured logging setup in services/payment-service/src/utils/logging.py"
```

## Implementation Notes

### Realistic Payment Processing Features
- **Processing Delays**: 1-3 seconds (configurable via environment)
- **Success Rate**: 95% (configurable via PAYMENT_SUCCESS_RATE)
- **Failure Scenarios**: Insufficient funds, card declined, network errors, invalid methods
- **Transaction IDs**: UUID-based with realistic gateway prefixes
- **Different Logic**: Credit cards, debit cards, PayPal processing variations

### Security & Integration
- **JWT Authentication**: All endpoints except health and webhooks
- **Auth Service**: User validation via HTTP client (port 8001)
- **Order Service**: Status updates via HTTP client (port 8008)
- **Webhook Simulation**: Async delivery with retry logic and exponential backoff

### Database Strategy
- **Development**: SQLite for simplicity and quick setup
- **Production**: PostgreSQL support via environment configuration
- **Migrations**: Alembic for schema versioning
- **Indexing**: Optimized for payment queries and audit trails

## Validation Checklist
*GATE: Checked before task execution*

- [x] All 8 API endpoints have corresponding contract tests (T007-T014)
- [x] All 4 entities have model implementation tasks (T019-T022)
- [x] All contract tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path in services/payment-service/
- [x] No task modifies same file as another [P] task
- [x] Critical path clearly defined: Setup → Tests → Models → Services → API → Integration → Polish
- [x] Comprehensive coverage: 38 tasks covering all aspects from infrastructure to documentation

**READY FOR EXECUTION**: All tasks are properly ordered, dependencies mapped, and parallel execution opportunities identified.
