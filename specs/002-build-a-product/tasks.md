# Tasks: Product Catalog Service

**Input**: Design documents from `/specs/002-build-a-product/`
**Prerequisites**: research.md, data-model.md, contracts/openapi.yaml, quickstart.md

## Execution Flow (main)
```
1. Load research.md from feature directory
   → Tech stack: FastAPI, SQLAlchemy, SQLite/PostgreSQL
   → Auth integration: HTTP calls to auth-service
   → Structure: microservice pattern matching auth-service
2. Load design documents:
   → data-model.md: Product entity → model tasks
   → contracts/openapi.yaml: 8 endpoints → contract test tasks
   → quickstart.md: 3 test scenarios → integration tests
3. Generate tasks by category:
   → Setup: FastAPI project, dependencies, structure
   → Tests: contract tests, integration tests (TDD)
   → Core: models, services, endpoints
   → Integration: DB, auth middleware, sample data
   → Polish: unit tests, linting, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Convention: Microservice Structure
- **Service**: `services/product-catalog-service/`
- **Source**: `services/product-catalog-service/src/`
- **Tests**: `services/product-catalog-service/tests/`

## Phase 3.1: Setup
- [x] T001 Create service directory structure at services/product-catalog-service/
- [x] T002 Initialize FastAPI project with pyproject.toml and uv dependencies
- [x] T003 [P] Configure linting (ruff) and formatting tools in services/product-catalog-service/
- [x] T004 [P] Create Dockerfile matching auth-service pattern in services/product-catalog-service/
- [x] T005 [P] Configure environment variables and settings in services/product-catalog-service/src/config.py

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (from openapi.yaml)
- [x] T006 [P] Contract test GET /products in services/product-catalog-service/tests/contract/test_products_list.py
- [x] T007 [P] Contract test POST /products in services/product-catalog-service/tests/contract/test_products_create.py
- [x] T008 [P] Contract test GET /products/{id} in services/product-catalog-service/tests/contract/test_products_get.py
- [x] T009 [P] Contract test PUT /products/{id} in services/product-catalog-service/tests/contract/test_products_update.py
- [x] T010 [P] Contract test GET /products/category/{category} in services/product-catalog-service/tests/contract/test_products_category.py
- [x] T011 [P] Contract test GET /products/search in services/product-catalog-service/tests/contract/test_products_search.py
- [x] T012 [P] Contract test GET /health in services/product-catalog-service/tests/contract/test_health.py
- [x] T013 [P] Contract test GET /health/ready in services/product-catalog-service/tests/contract/test_health_ready.py

### Integration Tests (from quickstart.md scenarios)
- [x] T014 [P] Integration test customer browsing experience in services/product-catalog-service/tests/integration/test_customer_browsing.py
- [x] T015 [P] Integration test admin product management in services/product-catalog-service/tests/integration/test_admin_management.py
- [x] T016 [P] Integration test error handling scenarios in services/product-catalog-service/tests/integration/test_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Layer
- [x] T017 [P] Product model with SQLAlchemy in services/product-catalog-service/src/models/product.py
- [x] T018 [P] Database configuration and connection in services/product-catalog-service/src/database.py
- [x] T019 [P] Pydantic schemas (ProductCreate, ProductUpdate, ProductResponse) in services/product-catalog-service/src/schemas/product.py

### Business Logic
- [x] T020 [P] ProductService CRUD operations in services/product-catalog-service/src/services/product_service.py
- [x] T021 [P] Authentication dependency for admin endpoints in services/product-catalog-service/src/auth/dependencies.py
- [x] T022 [P] Sample data seeding logic in services/product-catalog-service/src/data/seed_data.py

### API Endpoints
- [x] T023 GET /products endpoint with pagination in services/product-catalog-service/src/api/products.py
- [x] T024 POST /products admin endpoint in services/product-catalog-service/src/api/products.py
- [x] T025 GET /products/{id} endpoint in services/product-catalog-service/src/api/products.py
- [x] T026 PUT /products/{id} admin endpoint in services/product-catalog-service/src/api/products.py
- [x] T027 GET /products/category/{category} endpoint in services/product-catalog-service/src/api/products.py
- [x] T028 GET /products/search endpoint in services/product-catalog-service/src/api/products.py
- [x] T029 [P] Health endpoints (/health, /health/ready) in services/product-catalog-service/src/api/health.py

### Application Assembly
- [x] T030 FastAPI application setup and router registration in services/product-catalog-service/src/main.py

## Phase 3.4: Integration
- [x] T031 Database initialization and sample data seeding on startup
- [x] T032 Auth service integration middleware
- [x] T033 Request/response logging and error handling
- [x] T034 CORS configuration for frontend integration

## Phase 3.5: Polish
- [ ] T035 [P] Unit tests for ProductService in services/product-catalog-service/tests/unit/test_product_service.py
- [ ] T036 [P] Unit tests for Pydantic schemas in services/product-catalog-service/tests/unit/test_schemas.py
- [ ] T037 [P] Unit tests for auth dependencies in services/product-catalog-service/tests/unit/test_auth_dependencies.py
- [ ] T038 Performance validation (response times < 200ms)
- [ ] T039 [P] Service README documentation in services/product-catalog-service/README.md
- [ ] T040 Code cleanup and remove any duplication
- [ ] T041 Run linting and formatting checks
- [ ] T042 Execute quickstart.md manual testing scenarios

## Dependencies

### Critical Path
```
T001-T005 (Setup) → T006-T016 (Tests) → T017-T030 (Implementation) → T031-T034 (Integration) → T035-T042 (Polish)
```

### Specific Dependencies
- **Database**: T017 (models) blocks T018 (database), T020 (service)
- **Schemas**: T019 (schemas) blocks T020 (service), T023-T028 (endpoints)
- **Service**: T020 (service) blocks T023-T028 (endpoints)
- **Auth**: T021 (auth deps) blocks T024, T026 (admin endpoints)
- **Main App**: T023-T029 (all endpoints) block T030 (main.py)
- **Implementation**: T030 (main.py) blocks T031-T034 (integration)

### Same-File Dependencies (Sequential)
- **products.py**: T023 → T024 → T025 → T026 → T027 → T028 (all endpoints in same file)
- **main.py**: T030 depends on all endpoint files

## Parallel Execution Examples

### Phase 3.1 Setup (parallel)
```bash
# Launch T003-T005 together:
Task: "Configure linting (ruff) and formatting tools"
Task: "Create Dockerfile matching auth-service pattern"
Task: "Configure environment variables and settings"
```

### Phase 3.2 Contract Tests (parallel)
```bash
# Launch T006-T013 together (all different files):
Task: "Contract test GET /products"
Task: "Contract test POST /products"
Task: "Contract test GET /products/{id}"
Task: "Contract test PUT /products/{id}"
Task: "Contract test GET /products/category/{category}"
Task: "Contract test GET /products/search"
Task: "Contract test GET /health"
Task: "Contract test GET /health/ready"
```

### Phase 3.2 Integration Tests (parallel)
```bash
# Launch T014-T016 together:
Task: "Integration test customer browsing experience"
Task: "Integration test admin product management"
Task: "Integration test error handling scenarios"
```

### Phase 3.3 Data Layer (parallel)
```bash
# Launch T017-T019 together (different files):
Task: "Product model with SQLAlchemy"
Task: "Database configuration and connection"
Task: "Pydantic schemas (ProductCreate, ProductUpdate, ProductResponse)"
```

### Phase 3.3 Business Logic (parallel)
```bash
# Launch T020-T022 together (different files):
Task: "ProductService CRUD operations"
Task: "Authentication dependency for admin endpoints"
Task: "Sample data seeding logic"
```

### Phase 3.5 Unit Tests (parallel)
```bash
# Launch T035-T037 together:
Task: "Unit tests for ProductService"
Task: "Unit tests for Pydantic schemas"
Task: "Unit tests for auth dependencies"
```

## Notes
- [P] tasks = different files, no dependencies
- **TDD Critical**: Verify all tests fail before implementing features
- **Auth Integration**: Admin endpoints require JWT from auth-service:8001
- **Database**: SQLite for development, PostgreSQL configuration for production
- **Sample Data**: 20+ products across 4 categories (electronics, clothing, books, home_goods)
- **Port**: Service runs on port 8004
- **Consistency**: Follow auth-service patterns for structure and configuration
- Commit after each major task completion
- Run `uv run ruff check .` and `uv run ruff format .` after each implementation task

## Task Generation Rules Applied

1. **From openapi.yaml**: 8 endpoints → 8 contract tests (T006-T013) + 6 implementation tasks (T023-T029)
2. **From data-model.md**: Product entity → model task (T017) + schemas (T019) + service (T020)
3. **From quickstart.md**: 3 scenarios → 3 integration tests (T014-T016)
4. **From research.md**: FastAPI + SQLAlchemy + JWT → setup tasks (T001-T005)

## Validation Checklist ✅

- [x] All contracts have corresponding tests (T006-T013)
- [x] All entities have model tasks (T017 for Product)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks truly independent (different files marked [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD flow enforced (tests must fail before implementation)
- [x] Microservice structure matches project patterns
- [x] Auth integration planned for admin endpoints
- [x] Sample data seeding included
- [x] Health endpoints included
- [x] Performance validation included