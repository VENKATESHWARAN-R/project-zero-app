# Tasks: User Profile Management Service

**Input**: Design documents from `/specs/007-build-a-user/`
**Prerequisites**: research.md, data-model.md, contracts/openapi.yaml, quickstart.md

## Execution Flow (main)
```
1. Load research.md from feature directory
   → Extract: FastAPI + SQLAlchemy + PostgreSQL + JWT auth integration
2. Load data-model.md: Extract entities → model tasks
   → UserProfile, Address, UserPreferences, ActivityLog entities
3. Load contracts/openapi.yaml: Extract endpoints → contract test tasks
   → Health, Profiles, Addresses, Preferences, Activity, Admin endpoints
4. Load quickstart.md: Extract test scenarios → integration test tasks
5. Generate tasks by category:
   → Setup: FastAPI project init with uv, dependencies, linting
   → Tests: contract tests, integration tests (TDD approach)
   → Core: SQLAlchemy models, Pydantic schemas, service layers
   → Integration: JWT auth, database, middleware, health checks
   → Polish: Docker, docker-compose, Swagger docs, README updates
6. Apply task rules:
   → Different files = mark [P] for parallel execution
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
7. Number tasks sequentially (T001, T002...)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Service Structure**: `services/user-profile-service/` (following auth-service pattern)
- **Source Code**: `services/user-profile-service/src/`
- **Tests**: `services/user-profile-service/tests/`

## Phase 3.1: Setup and Project Initialization
- [ ] T001 Create user-profile-service directory structure at services/user-profile-service/
- [ ] T002 Initialize Python project with uv and create pyproject.toml with FastAPI dependencies
- [ ] T003 [P] Configure linting and formatting with ruff in services/user-profile-service/.ruff.toml
- [ ] T004 [P] Create environment configuration in services/user-profile-service/.env.example
- [ ] T005 [P] Create Dockerfile following auth-service pattern in services/user-profile-service/Dockerfile

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T006 [P] Contract test for health endpoints in services/user-profile-service/tests/contract/test_health.py
- [ ] T007 [P] Contract test for profile CRUD endpoints in services/user-profile-service/tests/contract/test_profiles.py
- [ ] T008 [P] Contract test for address management endpoints in services/user-profile-service/tests/contract/test_addresses.py
- [ ] T009 [P] Contract test for preferences endpoints in services/user-profile-service/tests/contract/test_preferences.py
- [ ] T010 [P] Contract test for activity log endpoints in services/user-profile-service/tests/contract/test_activity.py
- [ ] T011 [P] Contract test for admin endpoints in services/user-profile-service/tests/contract/test_admin.py
- [ ] T012 [P] Integration test for profile creation flow in services/user-profile-service/tests/integration/test_profile_creation.py
- [ ] T013 [P] Integration test for address management in services/user-profile-service/tests/integration/test_address_management.py
- [ ] T014 [P] Integration test for auth service integration in services/user-profile-service/tests/integration/test_auth_integration.py

## Phase 3.3: Core Database Models (ONLY after tests are failing)
- [ ] T015 [P] UserProfile model in services/user-profile-service/src/models/user_profile.py
- [ ] T016 [P] Address model in services/user-profile-service/src/models/address.py
- [ ] T017 [P] UserPreferences model in services/user-profile-service/src/models/user_preferences.py
- [ ] T018 [P] ActivityLog model in services/user-profile-service/src/models/activity_log.py
- [ ] T019 Database configuration and session management in services/user-profile-service/src/database.py
- [ ] T020 Database initialization and migration utilities in services/user-profile-service/src/models/__init__.py

## Phase 3.4: Pydantic Schemas and Validation
- [ ] T021 [P] Profile request/response schemas in services/user-profile-service/src/schemas/profile.py
- [ ] T022 [P] Address request/response schemas in services/user-profile-service/src/schemas/address.py
- [ ] T023 [P] Preferences request/response schemas in services/user-profile-service/src/schemas/preferences.py
- [ ] T024 [P] Activity log response schemas in services/user-profile-service/src/schemas/activity.py
- [ ] T025 [P] Health check schemas in services/user-profile-service/src/schemas/health.py
- [ ] T026 [P] Error response schemas in services/user-profile-service/src/schemas/error.py

## Phase 3.5: Service Layer Implementation
- [ ] T027 [P] UserProfile service with CRUD operations in services/user-profile-service/src/services/profile_service.py
- [ ] T028 [P] Address service with validation and default handling in services/user-profile-service/src/services/address_service.py
- [ ] T029 [P] UserPreferences service in services/user-profile-service/src/services/preferences_service.py
- [ ] T030 [P] ActivityLog service for audit trail in services/user-profile-service/src/services/activity_service.py
- [ ] T031 Auth service integration client in services/user-profile-service/src/services/auth_service.py

## Phase 3.6: API Endpoints Implementation
- [ ] T032 [P] Health check endpoints in services/user-profile-service/src/routers/health.py
- [ ] T033 Profile management endpoints in services/user-profile-service/src/routers/profiles.py
- [ ] T034 Address management endpoints in services/user-profile-service/src/routers/addresses.py
- [ ] T035 Preferences endpoints in services/user-profile-service/src/routers/preferences.py
- [ ] T036 Activity log endpoints in services/user-profile-service/src/routers/activity.py
- [ ] T037 [P] Admin endpoints in services/user-profile-service/src/routers/admin.py

## Phase 3.7: Authentication and Middleware Integration
- [ ] T038 JWT authentication dependency in services/user-profile-service/src/auth/jwt_auth.py
- [ ] T039 CORS and security middleware configuration in services/user-profile-service/src/middleware.py
- [ ] T040 Request correlation ID middleware in services/user-profile-service/src/middleware/correlation.py
- [ ] T041 Error handling middleware in services/user-profile-service/src/middleware/error_handler.py

## Phase 3.8: Application Configuration and Main Module
- [ ] T042 Environment configuration management in services/user-profile-service/src/config.py
- [ ] T043 FastAPI application setup and router registration in services/user-profile-service/src/app.py
- [ ] T044 Main application entry point in services/user-profile-service/main.py

## Phase 3.9: Testing and Quality Assurance
- [ ] T045 [P] Unit tests for profile service in services/user-profile-service/tests/unit/test_profile_service.py
- [ ] T046 [P] Unit tests for address service in services/user-profile-service/tests/unit/test_address_service.py
- [ ] T047 [P] Unit tests for preferences service in services/user-profile-service/tests/unit/test_preferences_service.py
- [ ] T048 [P] Unit tests for validation logic in services/user-profile-service/tests/unit/test_validation.py
- [ ] T049 Test configuration and fixtures in services/user-profile-service/tests/conftest.py
- [ ] T050 Run all tests and ensure 80%+ coverage verification

## Phase 3.10: Docker and Container Integration
- [ ] T051 Build and test Docker container for user-profile-service
- [ ] T052 Add user-profile-service to root docker-compose.yml with proper networking
- [ ] T053 Verify service health checks work in containerized environment
- [ ] T054 Test service integration with auth-service via docker-compose

## Phase 3.11: Documentation and API Verification
- [ ] T055 Verify Swagger/OpenAPI documentation is properly generated at /docs endpoint
- [ ] T056 Test interactive API documentation accessibility and accuracy
- [ ] T057 Create service-specific README.md in services/user-profile-service/
- [ ] T058 Update root README.md with user-profile-service information and port details

## Phase 3.12: Final Integration and Performance Testing
- [ ] T059 Run performance tests to ensure <200ms response times for profile operations
- [ ] T060 Execute all quickstart test scenarios from specs/007-build-a-user/quickstart.md
- [ ] T061 Verify auth service integration with token validation and user extraction
- [ ] T062 Final lint and format check with ruff

## Dependencies
- **Setup before Tests**: T001-T005 before T006-T014
- **Tests before Implementation**: T006-T014 before T015-T044
- **Models before Services**: T015-T020 before T027-T031
- **Schemas before Endpoints**: T021-T026 before T032-T037
- **Services before Endpoints**: T027-T031 before T032-T037
- **Core before Integration**: T015-T044 before T045-T054
- **Implementation before Documentation**: T015-T050 before T055-T058
- **Everything before Final Testing**: T001-T058 before T059-T062

## Parallel Execution Examples

### Phase 3.2 - Contract Tests (All Parallel)
```bash
# Launch T006-T011 together:
Task: "Contract test for health endpoints in services/user-profile-service/tests/contract/test_health.py"
Task: "Contract test for profile CRUD endpoints in services/user-profile-service/tests/contract/test_profiles.py"
Task: "Contract test for address management endpoints in services/user-profile-service/tests/contract/test_addresses.py"
Task: "Contract test for preferences endpoints in services/user-profile-service/tests/contract/test_preferences.py"
Task: "Contract test for activity log endpoints in services/user-profile-service/tests/contract/test_activity.py"
Task: "Contract test for admin endpoints in services/user-profile-service/tests/contract/test_admin.py"
```

### Phase 3.3 - Database Models (All Parallel)
```bash
# Launch T015-T018 together:
Task: "UserProfile model in services/user-profile-service/src/models/user_profile.py"
Task: "Address model in services/user-profile-service/src/models/address.py"
Task: "UserPreferences model in services/user-profile-service/src/models/user_preferences.py"
Task: "ActivityLog model in services/user-profile-service/src/models/activity_log.py"
```

### Phase 3.4 - Pydantic Schemas (All Parallel)
```bash
# Launch T021-T026 together:
Task: "Profile request/response schemas in services/user-profile-service/src/schemas/profile.py"
Task: "Address request/response schemas in services/user-profile-service/src/schemas/address.py"
Task: "Preferences request/response schemas in services/user-profile-service/src/schemas/preferences.py"
Task: "Activity log response schemas in services/user-profile-service/src/schemas/activity.py"
Task: "Health check schemas in services/user-profile-service/src/schemas/health.py"
Task: "Error response schemas in services/user-profile-service/src/schemas/error.py"
```

### Phase 3.5 - Service Layer (Most Parallel)
```bash
# Launch T027-T031 together:
Task: "UserProfile service with CRUD operations in services/user-profile-service/src/services/profile_service.py"
Task: "Address service with validation and default handling in services/user-profile-service/src/services/address_service.py"
Task: "UserPreferences service in services/user-profile-service/src/services/preferences_service.py"
Task: "ActivityLog service for audit trail in services/user-profile-service/src/services/activity_service.py"
Task: "Auth service integration client in services/user-profile-service/src/services/auth_service.py"
```

## Task Implementation Guidelines

### Test-Driven Development (TDD)
1. **Write failing tests first** (T006-T014) - Each test should expect specific behavior
2. **Run tests to confirm failures** - Ensure tests fail for the right reasons
3. **Implement minimal code** to make tests pass (T015-T044)
4. **Refactor** while keeping tests green

### FastAPI Best Practices
- Use dependency injection for database sessions and auth
- Implement proper error handling with HTTP status codes
- Follow OpenAPI specification from contracts/openapi.yaml exactly
- Use Pydantic models for request/response validation
- Implement structured logging with correlation IDs

### Database Integration
- Follow SQLAlchemy declarative base pattern from auth-service
- Implement proper foreign key relationships and constraints
- Use database sessions with proper cleanup
- Implement database migrations with Alembic (future consideration)

### Security Requirements
- JWT token validation matching auth-service secret key
- User isolation - all queries must filter by authenticated user_id
- Input validation and sanitization
- No sensitive data exposure in logs or responses
- Activity logging for audit trail

### Performance Targets
- Response times <200ms for all profile operations
- Efficient database queries with proper indexing
- Connection pooling for database access
- Stateless design for horizontal scaling

## Verification Checklist
*GATE: Checked before marking implementation complete*

- [ ] All contract tests written and initially failing
- [ ] All database models match data-model.md specifications
- [ ] All API endpoints match contracts/openapi.yaml exactly
- [ ] JWT authentication working with auth-service integration
- [ ] All validation rules from data-model.md implemented
- [ ] Activity logging captures all user actions
- [ ] Docker container builds and runs successfully
- [ ] Service integrates properly in docker-compose environment
- [ ] Swagger documentation accessible and accurate
- [ ] All quickstart scenarios pass successfully
- [ ] Performance targets met (<200ms response times)
- [ ] Code coverage >80% with meaningful tests
- [ ] Linting and formatting pass without errors
- [ ] README documentation complete and accurate

## Notes
- [P] tasks can run in parallel (different files, no dependencies)
- Verify tests fail before implementing functionality
- Commit after each major task completion
- Follow constitutional principles: simplicity first, functionality over architecture
- Use existing auth-service and order-service patterns for consistency
- Maintain microservice boundaries with proper service integration
- Focus on demonstrable functionality for e-commerce platform demo

## Success Criteria
✅ **Service Health**: Health and readiness endpoints functional
✅ **Profile Management**: Complete CRUD operations for user profiles
✅ **Address Management**: Full address lifecycle with default handling
✅ **Preferences**: User notification and account preferences management
✅ **Activity Logging**: Comprehensive audit trail of user actions
✅ **Authentication**: JWT integration with auth-service
✅ **API Documentation**: Interactive Swagger docs accessible
✅ **Container Ready**: Docker container builds and integrates properly
✅ **Performance**: Sub-200ms response times for normal operations
✅ **Testing**: Comprehensive test suite with high coverage
✅ **Documentation**: Complete service documentation and integration guides