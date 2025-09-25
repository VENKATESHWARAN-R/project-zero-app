# Tasks: Order Processing Service

**Input**: Design documents from `/specs/005-build-an-order/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.13+, FastAPI, SQLAlchemy, SQLite (dev), PostgreSQL (prod)
   → Structure: Single microservice at services/order-service/
2. Load design documents:
   → data-model.md: 4 entities (Order, OrderItem, ShippingAddress, OrderModification)
   → contracts/openapi.yaml: 13 endpoints across 4 categories
   → quickstart.md: 3 integration scenarios with service coordination
3. Generate tasks by category:
   → Setup: project structure, dependencies, database configuration
   → Tests: contract tests (13 endpoints), integration tests (3 scenarios)
   → Core: 4 entity models, business logic, service integrations
   → API: 13 endpoint implementations grouped by functionality
   → Integration: Auth (8001), Cart (8007), Product Catalog (8004) services
   → Polish: health checks, containerization, documentation
4. Apply task rules:
   → Different files/services = mark [P] for parallel execution
   → Database models before services = sequential
   → Tests before implementation (TDD approach)
5. Number tasks T001-T035 with dependency ordering
6. Service integration tasks handle cross-service communication
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths for all tasks

## Path Conventions
**Microservice Structure**: `services/order-service/` following existing auth-service pattern
- `services/order-service/src/` for source code
- `services/order-service/tests/` for all test types
- `services/order-service/main.py` as FastAPI entry point

## Phase 3.1: Project Setup & Infrastructure

- [ ] **T001** Create project structure at services/order-service/ with src/, tests/, main.py, requirements.txt, Dockerfile
- [ ] **T002** Initialize Python project dependencies (FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic 2.0+, uvicorn, httpx, pytest, pytest-asyncio, psycopg2-binary, alembic) in services/order-service/requirements.txt
- [ ] **T003** [P] Configure environment variables and settings in services/order-service/src/config.py (DATABASE_URL with SQLite dev/PostgreSQL prod, JWT_SECRET_KEY, SERVICE_URLS, TAX_RATE, PORT=8008)
- [ ] **T004** [P] Setup database configuration with SQLAlchemy engine supporting both SQLite (dev) and PostgreSQL (prod) in services/order-service/src/database.py
- [ ] **T005** [P] Configure structured logging with correlation IDs in services/order-service/src/logging_config.py
- [ ] **T006** [P] Setup Alembic for database migrations with PostgreSQL production support in services/order-service/alembic.ini and services/order-service/alembic/

## Phase 3.2: Data Models & Database Schema (FOUNDATION - Must complete before services)

- [ ] **T007** [P] Order model with status enum, totals calculation, audit fields, PostgreSQL-compatible types in services/order-service/src/models/order.py
- [ ] **T008** [P] OrderItem model with product snapshots, pricing, weight, PostgreSQL decimal precision in services/order-service/src/models/order_item.py
- [ ] **T009** [P] ShippingAddress model with validation, country codes, PostgreSQL text fields in services/order-service/src/models/shipping_address.py
- [ ] **T010** [P] OrderModification model for audit trail, change tracking, PostgreSQL JSONB for old/new values in services/order-service/src/models/order_modification.py
- [ ] **T011** Database initialization script with table creation, constraints, indexes optimized for PostgreSQL in services/order-service/src/models/__init__.py
- [ ] **T012** Create initial Alembic migration for all order-related tables with PostgreSQL-specific optimizations in services/order-service/alembic/versions/001_initial_schema.py

## Phase 3.3: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.4
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Endpoints)
- [ ] **T013** [P] Contract test POST /orders (order creation) in services/order-service/tests/contract/test_orders_post.py
- [ ] **T014** [P] Contract test GET /orders (order history) in services/order-service/tests/contract/test_orders_get.py
- [ ] **T015** [P] Contract test GET /orders/{orderId} (order details) in services/order-service/tests/contract/test_orders_detail.py
- [ ] **T016** [P] Contract test PATCH /orders/{orderId} (order modification) in services/order-service/tests/contract/test_orders_patch.py
- [ ] **T017** [P] Contract test POST /orders/{orderId}/cancel (order cancellation) in services/order-service/tests/contract/test_orders_cancel.py
- [ ] **T018** [P] Contract test PUT /orders/{orderId}/status (status updates) in services/order-service/tests/contract/test_orders_status.py
- [ ] **T019** [P] Contract test GET /orders/{orderId}/status-history (status history) in services/order-service/tests/contract/test_status_history.py
- [ ] **T020** [P] Contract test GET /admin/orders (admin order management) in services/order-service/tests/contract/test_admin_orders.py
- [ ] **T021** [P] Contract test PUT /admin/orders/{orderId}/status (admin status updates) in services/order-service/tests/contract/test_admin_status.py
- [ ] **T022** [P] Contract test POST /shipping/calculate (shipping cost calculation) in services/order-service/tests/contract/test_shipping_calculate.py
- [ ] **T023** [P] Contract test GET /shipping/rates (shipping rates) in services/order-service/tests/contract/test_shipping_rates.py
- [ ] **T024** [P] Contract test GET /health and GET /health/ready (health checks) in services/order-service/tests/contract/test_health.py

### Integration Tests (End-to-End Scenarios)
- [ ] **T025** [P] Integration test: Complete order creation flow (cart→order→clear) in services/order-service/tests/integration/test_order_creation_flow.py
- [ ] **T026** [P] Integration test: Admin order management workflow (status transitions) in services/order-service/tests/integration/test_admin_workflow.py
- [ ] **T027** [P] Integration test: Order modification scenarios (status-based rules) in services/order-service/tests/integration/test_order_modifications.py

## Phase 3.4: Business Logic & Services (ONLY after tests are failing)

### Service Layer (Business Logic)
- [ ] **T028** OrderService class with order creation, modification, status management, PostgreSQL transaction handling in services/order-service/src/services/order_service.py
- [ ] **T029** [P] ShippingService class with cost calculation, weight-based tiers in services/order-service/src/services/shipping_service.py
- [ ] **T030** [P] TaxService class with 8.5% fixed rate calculation in services/order-service/src/services/tax_service.py

### External Service Integration
- [ ] **T031** [P] AuthService client for JWT validation, admin role checks in services/order-service/src/clients/auth_client.py
- [ ] **T032** [P] CartService client for cart retrieval, clearing after order in services/order-service/src/clients/cart_client.py
- [ ] **T033** [P] ProductCatalogService client for product details, inventory validation in services/order-service/src/clients/product_client.py

## Phase 3.5: API Implementation (Make tests pass)

### Pydantic Schemas & Validation
- [ ] **T034** [P] Request/Response schemas for all endpoints in services/order-service/src/schemas/
- [ ] **T035** [P] Input validation, error handling, status code mapping in services/order-service/src/utils/validation.py

### FastAPI Route Handlers
- [ ] **T036** Order management endpoints (POST, GET, PATCH /orders, /orders/{id}) in services/order-service/src/api/orders.py
- [ ] **T037** [P] Order status endpoints (PUT /orders/{id}/status, GET /orders/{id}/status-history) in services/order-service/src/api/order_status.py
- [ ] **T038** [P] Admin endpoints (GET /admin/orders, PUT /admin/orders/{id}/status) in services/order-service/src/api/admin.py
- [ ] **T039** [P] Shipping endpoints (POST /shipping/calculate, GET /shipping/rates) in services/order-service/src/api/shipping.py
- [ ] **T040** [P] Health check endpoints (GET /health, GET /health/ready) with database connectivity checks in services/order-service/src/api/health.py

### Application Assembly
- [ ] **T041** FastAPI application setup, middleware, CORS, exception handlers in services/order-service/main.py

## Phase 3.6: Infrastructure & Deployment

- [ ] **T042** [P] Dockerfile with multi-stage build, non-root user, health checks, PostgreSQL client libraries in services/order-service/Dockerfile
- [ ] **T043** [P] Docker Compose integration with PostgreSQL database, auth, cart, product services in services/order-service/docker-compose.yml
- [ ] **T044** [P] Environment configuration for development (SQLite) and production (PostgreSQL) in services/order-service/.env.example and services/order-service/.env.prod.example
- [ ] **T045** [P] Database migration scripts and deployment procedures for PostgreSQL in services/order-service/scripts/migrate.sh

## Phase 3.7: Testing & Validation

### Unit Tests (Business Logic)
- [ ] **T046** [P] Unit tests for OrderService business logic in services/order-service/tests/unit/test_order_service.py
- [ ] **T047** [P] Unit tests for shipping calculation logic in services/order-service/tests/unit/test_shipping_service.py
- [ ] **T048** [P] Unit tests for tax calculation logic in services/order-service/tests/unit/test_tax_service.py
- [ ] **T049** [P] Unit tests for order status transition validation in services/order-service/tests/unit/test_status_transitions.py

### Database & Migration Tests
- [ ] **T050** [P] Database migration tests for PostgreSQL schema changes in services/order-service/tests/migrations/test_migrations.py
- [ ] **T051** [P] PostgreSQL-specific tests for JSONB queries, indexing performance in services/order-service/tests/database/test_postgresql_features.py

### Service Integration Validation
- [ ] **T052** [P] Service communication tests with mocked external services in services/order-service/tests/integration/test_service_communication.py
- [ ] **T053** Test data seeding and database fixtures for both SQLite (dev) and PostgreSQL (test/prod) in services/order-service/tests/fixtures/

## Phase 3.8: Documentation & Polish

- [ ] **T054** [P] Service README with setup (dev SQLite + prod PostgreSQL), API docs, integration guide in services/order-service/README.md
- [ ] **T055** [P] Update project CLAUDE.md with order service details, database configuration, and integration points
- [ ] **T056** Manual testing using quickstart.md scenarios with both SQLite and PostgreSQL configurations

## Dependencies & Execution Order

**Critical Dependencies**:
- Setup tasks (T001-T006) → All other tasks
- Models (T007-T012) → Services (T028-T033) → API (T036-T041)
- Contract tests (T013-T024) → Implementation (T036-T041)
- Migration setup (T006, T012) → Database tests (T050-T051)
- External client setup (T031-T033) → Integration tests (T025-T027)
- Core implementation (T036-T041) → Unit tests (T046-T049)

**Blocking Relationships**:
- T011 blocks T028 (database must exist before OrderService)
- T012 blocks T050 (initial migration needed before migration tests)
- T028 blocks T036 (OrderService must exist before order endpoints)
- T031-T033 block T025-T027 (service clients needed for integration tests)
- T041 blocks T042-T045 (FastAPI app needed before containerization)

## Parallel Execution Examples

### Phase 3.2 - Models (All Independent)
```bash
# Launch T007-T010 together (different model files):
Task: "Order model with PostgreSQL-compatible types in services/order-service/src/models/order.py"
Task: "OrderItem model with PostgreSQL decimal precision in services/order-service/src/models/order_item.py"
Task: "ShippingAddress model with PostgreSQL text fields in services/order-service/src/models/shipping_address.py"
Task: "OrderModification model with PostgreSQL JSONB in services/order-service/src/models/order_modification.py"
```

### Phase 3.3 - Contract Tests (All Independent)
```bash
# Launch T013-T024 together (different test files):
Task: "Contract test POST /orders in services/order-service/tests/contract/test_orders_post.py"
Task: "Contract test GET /orders in services/order-service/tests/contract/test_orders_get.py"
Task: "Contract test GET /orders/{orderId} in services/order-service/tests/contract/test_orders_detail.py"
# ... (continue for all contract tests)
```

### Phase 3.4 - Service Clients (Independent Services)
```bash
# Launch T031-T033 together (different service integrations):
Task: "AuthService client for JWT validation in services/order-service/src/clients/auth_client.py"
Task: "CartService client for cart operations in services/order-service/src/clients/cart_client.py"
Task: "ProductCatalogService client for product details in services/order-service/src/clients/product_client.py"
```

## Database Configuration Strategy

**Development Environment**:
- SQLite database for local development simplicity
- File-based storage: `services/order-service/order_service.db`
- No external dependencies for quick setup

**Production Environment**:
- PostgreSQL database for production scalability and features
- Connection pooling and transaction management
- JSONB support for OrderModification audit trail
- Proper indexing for performance at scale

**Migration Strategy**:
- Alembic migrations compatible with both SQLite and PostgreSQL
- Environment-specific configuration in T004 (database.py)
- Migration testing in T050 to ensure PostgreSQL compatibility

## Service Integration Architecture

**Inter-Service Communication Flow**:
```
1. Order Creation: Order Service → Cart Service (get cart) → Product Service (validate) → Cart Service (clear)
2. Authentication: All endpoints → Auth Service (verify JWT, check admin roles)
3. Order Status: Order Service → Internal status validation → External notifications (future)
```

**Service Coordination Points**:
- **T032** (Cart client): Handles cart retrieval and clearing after successful order
- **T031** (Auth client): Manages JWT validation and admin role verification
- **T033** (Product client): Validates product availability and fetches current pricing
- **T025** (Integration test): Validates complete service coordination flow

## Key Implementation Notes

**Database Design Considerations**:
- PostgreSQL JSONB for OrderModification old/new values (T010)
- Proper decimal precision for monetary values (T008)
- Database-agnostic SQLAlchemy models with PostgreSQL optimizations (T007-T010)
- Connection pooling and transaction management for PostgreSQL (T004)

**Status Transition Workflow**:
- PENDING → CONFIRMED (payment) → PROCESSING → SHIPPED → DELIVERED
- PENDING/CONFIRMED → CANCELLED (with business rules)
- Implemented in T028 (OrderService) and validated in T026 (admin workflow test)

**Business Logic Calculations**:
- **Tax**: 8.5% fixed rate on subtotal (T030)
- **Shipping**: Weight-based tiers (≤1lb=$5.99, ≤5lb=$8.99, ≤20lb=$15.99, >20lb=$25.99) (T029)
- **Total**: subtotal + tax_amount + shipping_cost

**Security & Authorization**:
- JWT validation for all authenticated endpoints (T031)
- Admin role checks for admin endpoints (T031, T038)
- Order ownership validation for user-specific operations (T036)

## Validation Checklist
*GATE: Checked before task execution completion*

- [x] All 13 API endpoints have corresponding contract tests (T013-T024)
- [x] All 4 data entities have model creation tasks (T007-T010)
- [x] All contract tests come before implementation (T013-T024 → T036-T041)
- [x] All parallel tasks are truly independent (different files/services)
- [x] Each task specifies exact file path in services/order-service/
- [x] Database configuration supports both SQLite (dev) and PostgreSQL (prod)
- [x] Migration strategy handles PostgreSQL-specific features (JSONB, indexing)
- [x] Service integration properly handles auth, cart, and product catalog coordination
- [x] TDD approach: tests must fail before implementation begins
- [x] Complete e-commerce workflow: browse → cart → authenticate → order → track
- [x] Status-based order modification rules implemented and tested
- [x] Health checks and containerization for production deployment with PostgreSQL