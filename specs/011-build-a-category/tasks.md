# Tasks: Category Management Service

**Input**: Design documents from `/specs/011-build-a-category/`
**Prerequisites**: data-model.md, research.md, contracts/api-specification.yaml, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Node.js/Express, Sequelize, Yarn, Swagger
2. Load design documents:
   → data-model.md: Category entity with hierarchy
   → contracts/: API specification with 11 endpoints
   → research.md: Tech decisions and integration patterns
   → quickstart.md: Validation scenarios
3. Generate tasks by category:
   → Setup: project init with yarn, dependencies, linting
   → Tests: contract tests, integration tests for each endpoint
   → Core: models, services, middleware, endpoints
   → Integration: DB, auth, product catalog, logging
   → Polish: docs, Docker, performance tests
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

## Phase 3.1: Setup

- [x] T001 Create category service project structure: `services/category-service/` with Node.js/Express/Sequelize architecture
- [x] T002 Initialize Node.js project with yarn: package.json, yarn.lock, and dependencies (express, sequelize, swagger-jsdoc, etc.)
- [x] T003 [P] Configure ESLint and Prettier: `.eslintrc.js`, `.prettierrc` for code quality
- [x] T004 [P] Configure environment variables: `.env.example` and `config/database.js` for SQLite/PostgreSQL support
- [x] T005 [P] Setup project scripts: yarn dev, yarn test, yarn lint, yarn format, yarn db:migrate

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T006 [P] Contract test GET /health in `tests/contract/health.test.js`
- [x] T007 [P] Contract test GET /health/ready in `tests/contract/health-ready.test.js`
- [x] T008 [P] Contract test GET /categories in `tests/contract/categories-get.test.js`
- [x] T009 [P] Contract test POST /categories in `tests/contract/categories-post.test.js`
- [x] T010 [P] Contract test GET /categories/{id} in `tests/contract/categories-get-by-id.test.js`
- [x] T011 [P] Contract test PUT /categories/{id} in `tests/contract/categories-put.test.js`
- [x] T012 [P] Contract test DELETE /categories/{id} in `tests/contract/categories-delete.test.js`
- [x] T013 [P] Contract test GET /categories/{id}/hierarchy in `tests/contract/categories-hierarchy.test.js`
- [x] T014 [P] Contract test GET /categories/{id}/products in `tests/contract/categories-products.test.js`
- [x] T015 [P] Contract test GET /categories/search in `tests/contract/categories-search.test.js`
- [x] T016 [P] Integration test category hierarchy creation in `tests/integration/hierarchy.test.js`
- [x] T017 [P] Integration test circular hierarchy prevention in `tests/integration/circular-prevention.test.js`
- [x] T018 [P] Integration test auth service integration in `tests/integration/auth-integration.test.js`
- [x] T019 [P] Integration test product catalog integration in `tests/integration/product-integration.test.js`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Layer
- [x] T020 [P] Category Sequelize model in `src/models/Category.js` with self-referencing associations
- [x] T021 [P] Database migrations in `src/migrations/001-create-categories.js` for SQLite/PostgreSQL
- [x] T022 [P] Database indexes in `src/migrations/002-add-category-indexes.js` for performance
- [x] T023 [P] Database seeders in `src/seeders/001-sample-categories.js` for testing

### Service Layer
- [x] T024 [P] CategoryService CRUD operations in `src/services/CategoryService.js`
- [x] T025 [P] HierarchyService for tree operations in `src/services/HierarchyService.js`
- [x] T026 [P] ValidationService for business rules in `src/services/ValidationService.js`
- [x] T027 [P] SlugService for URL-friendly slugs in `src/services/SlugService.js`

### Middleware
- [x] T028 [P] Auth middleware for JWT verification in `src/middleware/auth.js`
- [x] T029 [P] Admin middleware for admin-only routes in `src/middleware/admin.js`
- [x] T030 [P] Validation middleware with express-validator in `src/middleware/validation.js`
- [x] T031 [P] Error handling middleware in `src/middleware/errorHandler.js`
- [x] T032 [P] Request logging middleware in `src/middleware/logger.js`

### External Integration
- [x] T033 [P] Auth service client in `src/integrations/authService.js`
- [x] T034 [P] Product catalog client in `src/integrations/productService.js`
- [x] T035 [P] HTTP client utilities in `src/utils/httpClient.js`

### API Routes Implementation
- [x] T036 Health endpoints: GET /health, GET /health/ready in `src/routes/health.js`
- [x] T037 Category listing: GET /categories with filtering in `src/routes/categories.js`
- [x] T038 Category creation: POST /categories with validation in `src/routes/categories.js`
- [x] T039 Category retrieval: GET /categories/{id} with hierarchy options in `src/routes/categories.js`
- [x] T040 Category update: PUT /categories/{id} with circular prevention in `src/routes/categories.js`
- [x] T041 Category deletion: DELETE /categories/{id} with children validation in `src/routes/categories.js`
- [x] T042 Hierarchy endpoint: GET /categories/{id}/hierarchy in `src/routes/categories.js`
- [x] T043 Products endpoint: GET /categories/{id}/products with pagination in `src/routes/categories.js`
- [x] T044 Search endpoint: GET /categories/search with text matching in `src/routes/categories.js`

### Application Setup
- [x] T045 Express app configuration in `src/app.js` with middleware chain
- [x] T046 Database connection setup in `src/config/database.js`
- [x] T047 Server startup script in `src/server.js` with graceful shutdown

## Phase 3.4: Integration

- [x] T048 Sequelize database connection with retry logic
- [x] T049 Auth service integration with token verification endpoint
- [x] T050 Product catalog integration with graceful fallback
- [x] T051 Request correlation IDs for distributed tracing
- [x] T052 Structured JSON logging with Winston
- [x] T053 CORS and security headers configuration

## Phase 3.5: Documentation & API

- [x] T054 [P] Swagger/OpenAPI setup with swagger-jsdoc in `src/docs/swagger.js`
- [x] T055 [P] API documentation comments on route handlers
- [x] T056 [P] Generate swagger.json file in service root directory
- [x] T057 [P] Swagger UI endpoint at /docs for interactive testing

## Phase 3.6: Docker & Deployment

- [x] T058 [P] Dockerfile with multi-stage build and yarn optimization
- [x] T059 [P] Docker-compose service definition in `docker-compose.yml`
- [x] T060 [P] Health check configuration for Docker
- [x] T061 [P] Environment variable documentation in service README

## Phase 3.7: Polish & Testing

- [x] T062 [P] Unit tests for business logic in `tests/unit/services/`
- [x] T063 [P] Unit tests for utilities in `tests/unit/utils/`
- [x] T064 [P] Performance tests with autocannon in `tests/performance/`
- [x] T065 [P] Database migration tests in `tests/integration/migrations/`
- [x] T066 [P] Error handling tests in `tests/integration/errors/`

## Phase 3.8: Documentation Updates

- [x] T067 Service README.md with API documentation, setup instructions, and integration guide
- [x] T068 Update project root CLAUDE.md with category service details
- [x] T069 Update project root README.md with category management patterns and service documentation

## Dependencies

- Tests (T006-T019) before implementation (T020-T047)
- T020 (Category model) blocks T024 (CategoryService), T036-T044 (routes)
- T028-T032 (middleware) blocks T036-T044 (routes)
- T033-T034 (integrations) blocks T043 (products endpoint), T018-T019 (integration tests)
- T045-T047 (app setup) blocks T048-T053 (integration)
- Implementation before Docker (T058-T061)
- Implementation before documentation (T067-T069)

## Parallel Example

```
# Launch contract tests together (T006-T015):
Task: "Contract test GET /health in tests/contract/health.test.js"
Task: "Contract test GET /health/ready in tests/contract/health-ready.test.js"
Task: "Contract test GET /categories in tests/contract/categories-get.test.js"
Task: "Contract test POST /categories in tests/contract/categories-post.test.js"

# Launch integration tests together (T016-T019):
Task: "Integration test category hierarchy creation in tests/integration/hierarchy.test.js"
Task: "Integration test circular hierarchy prevention in tests/integration/circular-prevention.test.js"
Task: "Integration test auth service integration in tests/integration/auth-integration.test.js"
Task: "Integration test product catalog integration in tests/integration/product-integration.test.js"

# Launch models and services together (T020-T027):
Task: "Category Sequelize model in src/models/Category.js with self-referencing associations"
Task: "CategoryService CRUD operations in src/services/CategoryService.js"
Task: "HierarchyService for tree operations in src/services/HierarchyService.js"
Task: "ValidationService for business rules in src/services/ValidationService.js"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Use yarn consistently for all package management
- Ensure swagger.json is generated and saved in service root
- Follow simplicity principles while maintaining functionality
- Commit after each task group completion

## Task Generation Rules
*Applied during main() execution*

1. **From API Specification**:
   - Each endpoint → contract test task [P] + implementation task
   - 10 endpoints → 10 contract tests + route implementations

2. **From Data Model**:
   - Category entity → model creation task [P]
   - Hierarchical relationships → service layer tasks [P]
   - Database schema → migration tasks [P]

3. **From Quickstart Scenarios**:
   - Each validation scenario → integration test [P]
   - Docker validation → containerization tasks [P]
   - Performance testing → load test tasks [P]

4. **From Research Decisions**:
   - Yarn package manager → setup tasks with yarn
   - Swagger documentation → API doc generation tasks
   - Auth/Product integration → service client tasks

## Validation Checklist
*GATE: Checked before task completion*

- [ ] All API endpoints have corresponding contract tests
- [ ] Category entity has complete model implementation
- [ ] All tests come before implementation (TDD)
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
- [ ] Yarn used consistently throughout project
- [ ] Swagger.json generated in service folder
- [ ] Docker container builds and runs successfully
- [ ] Integration with auth and product services verified
- [ ] Project documentation updated comprehensively

## Success Criteria

Upon completion, the category management service must:
- Run on port 8005 with health checks
- Support hierarchical categories up to 5 levels
- Integrate with auth service for admin operations
- Integrate with product catalog for product associations
- Prevent circular hierarchies and enforce business rules
- Generate comprehensive Swagger documentation
- Run in Docker containers with yarn optimization
- Include complete test coverage (contract, integration, unit)
- Update all project documentation with service details