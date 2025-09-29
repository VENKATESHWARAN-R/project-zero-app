# Tasks: Comprehensive Integration Testing and PostgreSQL Migration

**Input**: Design documents from `/specs/010-create-a-comprehensive/`
**Prerequisites**: research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)

```text
1. Database migration tasks (T001-T009) - setup PostgreSQL for all services
2. Test infrastructure setup (T010-T013) - create testing framework
3. Service health verification (T014-T017) - verify all services operational
4. Authentication flow testing (T018-T021) - test auth workflows
5. Integration flow testing (T022-T026) - test service interactions
6. Error handling and reporting (T027-T029) - comprehensive test reporting
7. Documentation and verification (T030-T034) - finalize and document
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 1: Database Migration (SQLite → PostgreSQL)

### Core Database Configuration

- [x] T001 [P] Update auth-service SQLAlchemy configuration in `services/auth-service/src/config/database.py` to support PostgreSQL connection strings and create database initialization script in `services/auth-service/scripts/init_db.py` with table creation and test user seeding
- [x] T002 [P] Update product-catalog-service SQLAlchemy configuration in `services/product-catalog-service/src/config/database.py` for PostgreSQL support and create initialization script in `services/product-catalog-service/scripts/init_db.py` with sample product data seeding (20+ products across electronics, clothing, books, home categories)
- [x] T003 [P] Update order-service SQLAlchemy configuration in `services/order-service/src/config/database.py` for PostgreSQL with schema initialization script in `services/order-service/scripts/init_db.py`
- [x] T004 [P] Update payment-service SQLAlchemy configuration in `services/payment-service/src/config/database.py` for PostgreSQL with schema initialization script in `services/payment-service/scripts/init_db.py`
- [x] T005 [P] Update user-profile-service SQLAlchemy configuration in `services/user-profile-service/src/config/database.py` for PostgreSQL with schema initialization script in `services/user-profile-service/scripts/init_db.py`
- [x] T006 [P] Update cart-service Sequelize configuration in `services/cart-service/src/config/database.js` for PostgreSQL support and create initialization script in `services/cart-service/scripts/init_db.js`
- [x] T007 [P] Update notification-service database configuration in `services/notification-service/src/config/database.js` for PostgreSQL support and create initialization script in `services/notification-service/scripts/init_db.js`

### Docker and Environment Configuration

- [x] T008 Update `docker-compose.yml` to add PostgreSQL service and update environment variables for all services to use PostgreSQL connection strings
- [x] T009 Test each service individually with PostgreSQL by running health checks: `curl http://localhost:800X/health` for each service (auth:8001, profile:8002, products:8004, cart:8007, orders:8008, payments:8009, notifications:8011) to verify database connectivity

## Phase 2: Test Infrastructure Setup

### Test Framework Creation

- [x] T010 Create test directory structure: create `tests/` directory with subdirectories `tests/unit/`, `tests/integration/`, `tests/e2e/`, and `tests/fixtures/`
- [x] T011 Create main test orchestration script `tests/integration/test-runner.sh` with proper error handling, service startup verification, and detailed logging
- [x] T012 Create test utilities in `tests/utils/` directory: HTTP request helper (`http_client.sh`), response validation utility (`validate_response.sh`), and result reporting script (`test_reporter.sh`)
- [x] T013 Create test data fixtures in `tests/fixtures/`: user fixtures (`users.json`), product fixtures (`products.json`), and order fixtures (`orders.json`)

## Phase 3: Service Health Check Tests

### Basic Service Verification

- [ ] T014 Create health check test suite in `tests/integration/health_tests.sh` for all 9 services: verify `/health` endpoints respond with 200 status for auth-service:8001, user-profile:8002, products:8004, cart:8007, orders:8008, payments:8009, notifications:8011, api-gateway:8000
- [ ] T015 [P] Create database connectivity tests in `tests/integration/db_tests.sh` for each service to verify PostgreSQL connections are working
- [ ] T016 [P] Create Swagger documentation accessibility tests in `tests/integration/docs_tests.sh` for backend services (verify `/docs` endpoints respond)
- [ ] T017 Create API Gateway routing tests in `tests/integration/gateway_tests.sh` to verify routing to all downstream services through gateway endpoints

## Phase 4: Authentication Flow Tests

### Core Auth Testing

- [ ] T018 Create user registration test in `tests/integration/auth_tests.sh`: POST `/api/auth/register` with test user data and verify successful registration
- [ ] T019 Create user login test in `tests/integration/auth_tests.sh`: POST `/api/auth/login` with valid credentials and verify JWT token reception and structure
- [ ] T020 Create token verification test in `tests/integration/auth_tests.sh`: test JWT token validation across different services using received token
- [ ] T021 Create token refresh test in `tests/integration/auth_tests.sh`: POST `/api/auth/refresh` with refresh token and verify new access token reception

## Phase 5: Integration Flow Tests

### End-to-End Service Integration

- [ ] T022 Create product browsing test in `tests/integration/product_tests.sh`: GET `/api/products` with various filters (category, search, pagination) and verify response structure
- [ ] T023 Create cart operations test in `tests/integration/cart_tests.sh`: test full cart lifecycle (add item, update quantity, get cart contents, remove item) using authenticated requests
- [ ] T024 Create user profile test in `tests/integration/profile_tests.sh`: test profile operations (create profile, add address, update preferences) with authenticated user
- [ ] T025 Create end-to-end order flow test in `tests/integration/order_flow_tests.sh`: complete workflow from cart creation → order placement → payment processing → notification sending
- [ ] T026 Create service-to-service communication test in `tests/integration/service_communication_tests.sh`: verify cart service fetches product details, order service calls cart service, notification service integration

## Phase 6: Error Handling and Reporting

### Test Quality and Reporting

- [ ] T027 Implement detailed error reporting in test utilities: create `tests/utils/error_handler.sh` with specific failure messages, service status checks, and common issue diagnostics
- [ ] T028 Create test summary report generator in `tests/utils/generate_report.sh`: show pass/fail statistics, execution time, and detailed failure analysis
- [ ] T029 Add troubleshooting guidance in `tests/troubleshooting.md`: document common failures (connection refused, auth failed, timeout issues) with remediation steps

## Phase 7: Documentation and Verification

### Final Documentation

- [ ] T030 Create comprehensive testing README in `tests/README.md` with setup instructions, execution guide, and test scenario explanations
- [ ] T031 Run complete test suite using `tests/integration/test-runner.sh` and document results in `tests/RESULTS.md`
- [ ] T032 Fix any integration issues discovered during testing: address service communication problems, authentication flows, and database connectivity issues
- [ ] T033 Update project root `README.md` with new testing section: add PostgreSQL setup instructions, testing commands, and verification procedures
- [ ] T034 Create quick-start testing guide in `TESTING_GUIDE.md` for demo preparation: one-command setup and execution for stakeholder demonstrations

## Parallel Execution Examples

### Phase 1 (Database Migration) - Can run in parallel

```bash
# Run database configuration updates simultaneously
Task T001 & Task T002 & Task T003 & Task T004 & Task T005 & Task T006 & Task T007
wait  # Wait for all parallel tasks to complete
```

### Phase 3 (Health Checks) - Can run in parallel

```bash
# Run health verifications simultaneously
Task T015 & Task T016
wait  # Wait for all parallel tasks to complete
```

## Dependencies

- **T008** depends on T001-T007 (all database configs must be updated before docker-compose)
- **T009** depends on T008 (PostgreSQL must be running before individual service tests)
- **T010-T013** can run independently after T009
- **T014-T017** depend on T009-T013 (services must be running and test infrastructure ready)
- **T018-T021** depend on T014 (health checks must pass before auth testing)
- **T022-T026** depend on T018-T021 (authentication must work before integration flows)
- **T027-T029** depend on T022-T026 (integration tests must exist before error handling)
- **T030-T034** depend on T027-T029 (all testing must be complete before final documentation)

## Success Criteria

Each task includes verification that confirms specific functionality:

1. **Database Migration**: All services start with PostgreSQL, health checks pass
2. **Test Infrastructure**: Test runner executes successfully, reports generated
3. **Health Checks**: All 9 services respond to health endpoints
4. **Authentication**: User can register, login, and use tokens across services
5. **Integration**: Full order flow from cart to notification works end-to-end
6. **Reporting**: Clear pass/fail reporting with troubleshooting guidance
7. **Documentation**: Complete setup and execution guide for stakeholders

## Quick Verification Commands

```bash
# Verify PostgreSQL migration
docker-compose up -d && sleep 30
for port in 8001 8002 8004 8007 8008 8009 8011; do curl -s http://localhost:$port/health | jq; done

# Run full integration test suite
cd tests && ./integration/test-runner.sh

# Generate test report
cd tests/utils && ./generate_report.sh
```
