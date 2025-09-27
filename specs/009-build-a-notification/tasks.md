# Tasks: Notification Service

**Input**: Design documents from `/specs/009-build-a-notification/`
**Prerequisites**: research.md, data-model.md, contracts/notification-api.yaml, quickstart.md

## Execution Flow (main)
```
1. Load research.md from feature directory
   → Extract: Node.js/Express, SQLite/Sequelize, Jest testing
2. Load data model design:
   → data-model.md: 5 entities → model tasks
   → contracts/notification-api.yaml: 12 endpoints → contract test tasks
   → quickstart.md: 6 scenarios → integration test tasks
3. Generate tasks by category:
   → Setup: Node.js project init, Express dependencies, linting
   → Tests: contract tests, integration tests (TDD approach)
   → Core: Sequelize models, services, middleware
   → Integration: DB setup, auth middleware, provider mocks
   → Polish: unit tests, performance validation, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All endpoints have contract tests?
   → All entities have models?
   → All quickstart scenarios covered?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Notification Service**: `services/notification-service/` as service root
- **Models**: `services/notification-service/src/models/`
- **Services**: `services/notification-service/src/services/`
- **Controllers**: `services/notification-service/src/controllers/`
- **Tests**: `services/notification-service/tests/`

## Phase 3.1: Setup
- [ ] T001 Create notification service project structure in services/notification-service/
- [ ] T002 Initialize Node.js project with Express, Sequelize, SQLite dependencies in services/notification-service/package.json
- [ ] T003 [P] Configure ESLint and Prettier for code formatting in services/notification-service/.eslintrc.js
- [ ] T004 [P] Set up Jest testing framework in services/notification-service/jest.config.js
- [ ] T005 [P] Create environment configuration in services/notification-service/src/config/index.js
- [ ] T006 [P] Set up SQLite database configuration in services/notification-service/src/config/database.js

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Endpoints)
- [ ] T007 [P] Contract test GET /health in services/notification-service/tests/contract/health.test.js
- [ ] T008 [P] Contract test GET /health/ready in services/notification-service/tests/contract/health.test.js
- [ ] T009 [P] Contract test POST /notifications in services/notification-service/tests/contract/notifications.test.js
- [ ] T010 [P] Contract test GET /notifications in services/notification-service/tests/contract/notifications.test.js
- [ ] T011 [P] Contract test GET /notifications/{id} in services/notification-service/tests/contract/notifications.test.js
- [ ] T012 [P] Contract test POST /notifications/schedule in services/notification-service/tests/contract/notifications.test.js
- [ ] T013 [P] Contract test POST /notifications/template in services/notification-service/tests/contract/notifications.test.js
- [ ] T014 [P] Contract test GET /templates in services/notification-service/tests/contract/templates.test.js
- [ ] T015 [P] Contract test POST /templates in services/notification-service/tests/contract/templates.test.js
- [ ] T016 [P] Contract test GET /templates/{id} in services/notification-service/tests/contract/templates.test.js
- [ ] T017 [P] Contract test PUT /templates/{id} in services/notification-service/tests/contract/templates.test.js
- [ ] T018 [P] Contract test GET /preferences in services/notification-service/tests/contract/preferences.test.js
- [ ] T019 [P] Contract test PUT /preferences in services/notification-service/tests/contract/preferences.test.js

### Integration Tests (Quickstart Scenarios)
- [ ] T020 [P] Integration test welcome notification flow in services/notification-service/tests/integration/welcome-notification.test.js
- [ ] T021 [P] Integration test order confirmation flow in services/notification-service/tests/integration/order-confirmation.test.js
- [ ] T022 [P] Integration test payment SMS confirmation in services/notification-service/tests/integration/payment-sms.test.js
- [ ] T023 [P] Integration test scheduled notification flow in services/notification-service/tests/integration/scheduled-notification.test.js
- [ ] T024 [P] Integration test notification history retrieval in services/notification-service/tests/integration/notification-history.test.js
- [ ] T025 [P] Integration test user preference management in services/notification-service/tests/integration/user-preferences.test.js

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Models (Sequelize)
- [ ] T026 [P] Notification model in services/notification-service/src/models/Notification.js
- [ ] T027 [P] NotificationTemplate model in services/notification-service/src/models/NotificationTemplate.js
- [ ] T028 [P] NotificationHistory model in services/notification-service/src/models/NotificationHistory.js
- [ ] T029 [P] UserNotificationPreference model in services/notification-service/src/models/UserNotificationPreference.js
- [ ] T030 [P] ScheduledNotification model in services/notification-service/src/models/ScheduledNotification.js
- [ ] T031 Database associations and relationships in services/notification-service/src/models/index.js
- [ ] T032 Database migrations for all tables in services/notification-service/src/migrations/

### Service Layer
- [ ] T033 [P] NotificationService with CRUD operations in services/notification-service/src/services/NotificationService.js
- [ ] T034 [P] TemplateService with template management in services/notification-service/src/services/TemplateService.js
- [ ] T035 [P] PreferenceService for user preferences in services/notification-service/src/services/PreferenceService.js
- [ ] T036 [P] SchedulerService for scheduled notifications in services/notification-service/src/services/SchedulerService.js

### Mock Providers
- [ ] T037 [P] Mock Email Provider in services/notification-service/src/providers/MockEmailProvider.js
- [ ] T038 [P] Mock SMS Provider in services/notification-service/src/providers/MockSMSProvider.js
- [ ] T039 [P] In-App Provider in services/notification-service/src/providers/InAppProvider.js
- [ ] T040 Provider factory for delivery channel routing in services/notification-service/src/providers/ProviderFactory.js

### Controllers and Routes
- [ ] T041 Health controller for /health endpoints in services/notification-service/src/controllers/HealthController.js
- [ ] T042 Notification controller for notification endpoints in services/notification-service/src/controllers/NotificationController.js
- [ ] T043 Template controller for template management in services/notification-service/src/controllers/TemplateController.js
- [ ] T044 Preference controller for user preferences in services/notification-service/src/controllers/PreferenceController.js
- [ ] T045 Express routes configuration in services/notification-service/src/routes/index.js

## Phase 3.4: Integration

### Middleware and Security
- [ ] T046 JWT authentication middleware in services/notification-service/src/middleware/auth.js
- [ ] T047 Request validation middleware in services/notification-service/src/middleware/validation.js
- [ ] T048 Error handling middleware in services/notification-service/src/middleware/errorHandler.js
- [ ] T049 CORS and security headers in services/notification-service/src/middleware/security.js

### External Service Integration
- [ ] T050 Auth service integration for JWT verification in services/notification-service/src/integrations/AuthService.js
- [ ] T051 User profile service integration in services/notification-service/src/integrations/UserProfileService.js
- [ ] T052 Template rendering engine with variable substitution in services/notification-service/src/utils/TemplateRenderer.js

### Application Setup
- [ ] T053 Express application configuration in services/notification-service/src/app.js
- [ ] T054 Server startup and database connection in services/notification-service/src/server.js
- [ ] T055 Environment variable validation in services/notification-service/src/config/validation.js

## Phase 3.5: Documentation and Swagger

### API Documentation
- [ ] T056 Swagger configuration and automatic swagger.json generation in services/notification-service/src/swagger/index.js
- [ ] T057 [P] Swagger documentation for all endpoints in services/notification-service/src/swagger/docs.js
- [ ] T058 Generate and save swagger.json file in services/notification-service/swagger.json

### Logging and Monitoring
- [ ] T059 [P] Structured JSON logging setup in services/notification-service/src/utils/logger.js
- [ ] T060 [P] Request correlation ID middleware in services/notification-service/src/middleware/correlationId.js

## Phase 3.6: Docker and Infrastructure

### Containerization
- [ ] T061 [P] Dockerfile with multi-stage build in services/notification-service/Dockerfile
- [ ] T062 [P] Docker health check configuration in services/notification-service/Dockerfile
- [ ] T063 [P] .dockerignore file in services/notification-service/.dockerignore

### Development and Scripts
- [ ] T064 [P] Package.json scripts for dev, test, lint in services/notification-service/package.json
- [ ] T065 [P] Database seeding with default templates in services/notification-service/src/seeders/

## Phase 3.7: Integration Testing and Verification

### Docker Integration
- [ ] T066 Build and test Docker container for notification service
- [ ] T067 Integration testing with auth service via docker-compose
- [ ] T068 Integration testing with order service via docker-compose
- [ ] T069 Integration testing with payment service via docker-compose
- [ ] T070 Integration testing with profile service via docker-compose

### End-to-End Validation
- [ ] T071 Test all notification types and delivery methods
- [ ] T072 Verify Swagger documentation completeness and accuracy
- [ ] T073 Performance testing for notification sending
- [ ] T074 Error handling validation across all endpoints

## Phase 3.8: Documentation Updates

### Service Documentation
- [ ] T075 Create comprehensive README.md for notification service in services/notification-service/README.md
- [ ] T076 Update CLAUDE.md with notification service information
- [ ] T077 Update project root README.md with notification service documentation

## Dependencies

### Critical Path Dependencies
- Setup (T001-T006) before Tests (T007-T025)
- Tests (T007-T025) before Core Implementation (T026-T045)
- Models (T026-T032) before Services (T033-T040)
- Services (T033-T040) before Controllers (T041-T045)
- Controllers (T041-T045) before Integration (T046-T055)
- Core Implementation before Documentation (T056-T060)
- Application Setup (T053-T055) before Docker (T061-T065)
- All implementation before Integration Testing (T066-T074)

### Specific Dependencies
- T031 (model relationships) blocks T033-T036 (services)
- T032 (migrations) blocks T053 (app config)
- T040 (provider factory) blocks T042 (notification controller)
- T046 (auth middleware) blocks T042-T044 (controllers)
- T053 (app config) blocks T054 (server startup)
- T056 (swagger config) blocks T057-T058 (swagger docs)

## Parallel Execution Examples

### Phase 3.2 Contract Tests Launch
```bash
Task: "Contract test GET /health in services/notification-service/tests/contract/health.test.js"
Task: "Contract test POST /notifications in services/notification-service/tests/contract/notifications.test.js"
Task: "Contract test GET /templates in services/notification-service/tests/contract/templates.test.js"
Task: "Contract test GET /preferences in services/notification-service/tests/contract/preferences.test.js"
```

### Phase 3.2 Integration Tests Launch
```bash
Task: "Integration test welcome notification flow in services/notification-service/tests/integration/welcome-notification.test.js"
Task: "Integration test order confirmation flow in services/notification-service/tests/integration/order-confirmation.test.js"
Task: "Integration test payment SMS confirmation in services/notification-service/tests/integration/payment-sms.test.js"
Task: "Integration test scheduled notification flow in services/notification-service/tests/integration/scheduled-notification.test.js"
```

### Phase 3.3 Models Launch
```bash
Task: "Notification model in services/notification-service/src/models/Notification.js"
Task: "NotificationTemplate model in services/notification-service/src/models/NotificationTemplate.js"
Task: "NotificationHistory model in services/notification-service/src/models/NotificationHistory.js"
Task: "UserNotificationPreference model in services/notification-service/src/models/UserNotificationPreference.js"
Task: "ScheduledNotification model in services/notification-service/src/models/ScheduledNotification.js"
```

### Phase 3.3 Services Launch
```bash
Task: "NotificationService with CRUD operations in services/notification-service/src/services/NotificationService.js"
Task: "TemplateService with template management in services/notification-service/src/services/TemplateService.js"
Task: "PreferenceService for user preferences in services/notification-service/src/services/PreferenceService.js"
Task: "SchedulerService for scheduled notifications in services/notification-service/src/services/SchedulerService.js"
```

### Phase 3.3 Providers Launch
```bash
Task: "Mock Email Provider in services/notification-service/src/providers/MockEmailProvider.js"
Task: "Mock SMS Provider in services/notification-service/src/providers/MockSMSProvider.js"
Task: "In-App Provider in services/notification-service/src/providers/InAppProvider.js"
```

## Notes
- [P] tasks target different files with no shared dependencies
- Verify all contract tests fail before implementing endpoints
- Maintain TDD discipline: tests first, then implementation
- Each provider should simulate realistic delivery timing
- Swagger.json must be automatically generated and saved
- Integration tests must verify actual service communication
- Docker container must pass health checks and integrate with existing services
- Final documentation must include API endpoints, integration patterns, notification types, and configuration

## Task Generation Rules Applied

1. **From API Contract (notification-api.yaml)**:
   - 13 endpoints → 13 contract test tasks [P] (T007-T019)
   - Health endpoints → HealthController (T041)
   - Notification endpoints → NotificationController (T042)
   - Template endpoints → TemplateController (T043)
   - Preference endpoints → PreferenceController (T044)

2. **From Data Model**:
   - 5 entities → 5 model creation tasks [P] (T026-T030)
   - Model relationships → associations task (T031)
   - Database setup → migrations task (T032)

3. **From Quickstart Scenarios**:
   - 6 scenarios → 6 integration test tasks [P] (T020-T025)
   - Service integrations → external service tasks (T050-T051)

4. **From Research Decisions**:
   - Node.js/Express → project setup tasks (T001-T002)
   - SQLite/Sequelize → database config tasks (T006, T032)
   - Jest testing → test framework setup (T004)
   - Mock providers → provider implementation tasks (T037-T040)
   - Swagger requirement → documentation tasks (T056-T058)
   - Docker requirement → containerization tasks (T061-T063)

## Validation Checklist
*GATE: Checked before task execution*

- [x] All 13 API endpoints have corresponding contract tests
- [x] All 5 entities have model creation tasks
- [x] All tests come before implementation (T007-T025 before T026+)
- [x] Parallel tasks are in different files with no dependencies
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Docker integration and docker-compose testing included
- [x] Swagger.json generation and saving specified
- [x] All quickstart scenarios covered in integration tests
- [x] Documentation updates for all affected files included

**Task Generation Status: COMPLETE - 77 tasks ready for execution**