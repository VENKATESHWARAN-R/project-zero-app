# Tasks: User Authentication Service

**Input**: Design documents from `/specs/001-build-a-user/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

## Execution Flow (main)
```
1. Load plan.md from feature directory
   ✓ Extracted: FastAPI, SQLAlchemy, bcrypt, PyJWT, SQLite, Python 3.13+
2. Load optional design documents:
   ✓ data-model.md: User entity, JWT tokens, rate limiting
   ✓ contracts/auth-api.yml: 4 endpoints + health check
   ✓ quickstart.md: 6 user story scenarios
3. Generate tasks by category:
   ✓ Setup: FastAPI project init, dependencies, structure
   ✓ Tests: 5 contract tests, 6 integration tests
   ✓ Core: User model, auth services, JWT utils, endpoints
   ✓ Integration: Database, middleware, logging, rate limiting
   ✓ Polish: unit tests, performance validation
4. Apply task rules:
   ✓ Different files = mark [P] for parallel
   ✓ Same file = sequential (no [P])
   ✓ Tests before implementation (TDD)
5. Number tasks sequentially (T001-T035)
6. Generate dependency graph and parallel examples
7. Validate task completeness:
   ✓ All 5 endpoints have contract tests
   ✓ User entity has model task
   ✓ All 6 user stories have integration tests
8. Return: SUCCESS (35 tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- File paths use backend/ structure for web microservice

## Path Conventions
- **Web backend microservice**: `backend/src/`, `backend/tests/`
- Structure follows FastAPI best practices per implementation plan

## Phase 3.1: Setup
- [x] T001 Create backend project structure with src/models, src/services, src/api, src/utils directories
- [x] T002 Initialize Python project with FastAPI, SQLAlchemy, bcrypt, PyJWT, uvicorn dependencies in backend/requirements.txt
- [x] T003 [P] Configure pytest, black, and flake8 in backend/pyproject.toml and .pre-commit-config.yaml
- [x] T004 [P] Create main.py with FastAPI app initialization and basic configuration
- [x] T005 [P] Create database.py with SQLAlchemy configuration for SQLite

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (from auth-api.yml)
- [x] T006 [P] Contract test POST /auth/login in backend/tests/contract/test_auth_login.py
- [x] T007 [P] Contract test POST /auth/logout in backend/tests/contract/test_auth_logout.py
- [x] T008 [P] Contract test POST /auth/refresh in backend/tests/contract/test_auth_refresh.py
- [x] T009 [P] Contract test GET /auth/verify in backend/tests/contract/test_auth_verify.py
- [x] T010 [P] Contract test GET /health in backend/tests/contract/test_health.py

### Integration Tests (from quickstart.md user stories)
- [x] T011 [P] Integration test valid user login flow in backend/tests/integration/test_login_flow.py
- [x] T012 [P] Integration test token verification by services in backend/tests/integration/test_token_verification.py
- [x] T013 [P] Integration test token refresh functionality in backend/tests/integration/test_token_refresh.py
- [x] T014 [P] Integration test logout and token invalidation in backend/tests/integration/test_logout_flow.py
- [x] T015 [P] Integration test rate limiting protection in backend/tests/integration/test_rate_limiting.py
- [x] T016 [P] Integration test input validation and error handling in backend/tests/integration/test_validation.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (from data-model.md)
- [x] T017 [P] User model with id, email, password_hash, security fields in backend/src/models/user.py
- [x] T018 [P] Database schema initialization and migrations in backend/src/models/__init__.py

### Authentication Utilities
- [x] T019 [P] Password hashing utilities with bcrypt in backend/src/utils/password.py
- [x] T020 [P] JWT token generation and validation utilities in backend/src/utils/jwt_utils.py
- [x] T021 [P] Rate limiting utilities with in-memory storage in backend/src/utils/rate_limiter.py
- [x] T022 [P] Token blacklist management utilities in backend/src/utils/token_blacklist.py

### Services Layer
- [x] T023 User authentication service with login/register logic in backend/src/services/auth_service.py
- [x] T024 Token management service for refresh/verify operations in backend/src/services/token_service.py

### API Endpoints (from contracts/auth-api.yml)
- [x] T025 POST /auth/login endpoint with email/password authentication
- [x] T026 POST /auth/logout endpoint with token invalidation
- [x] T027 POST /auth/refresh endpoint for access token renewal
- [x] T028 GET /auth/verify endpoint for token validation
- [x] T029 GET /health endpoint with database connectivity check

### Pydantic Models
- [x] T030 [P] Request/response models for all auth endpoints in backend/src/schemas/auth.py

## Phase 3.4: Integration
- [ ] T031 Connect authentication services to SQLite database with proper error handling
- [ ] T032 JWT authentication middleware for protected endpoints
- [ ] T033 Request/response logging with structured JSON format
- [ ] T034 CORS, security headers, and rate limiting middleware integration

## Phase 3.5: Polish
- [ ] T035 [P] Unit tests for password hashing and JWT utilities in backend/tests/unit/test_utils.py
- [ ] T036 [P] Performance validation tests for <500ms login, <100ms verify in backend/tests/performance/
- [ ] T037 [P] Create Dockerfile and docker-compose.yml for containerized deployment
- [ ] T038 [P] Update README.md with API documentation and deployment instructions
- [ ] T039 Run quickstart.md validation scenarios to verify all user stories work

## Dependencies
**Critical TDD Dependencies:**
- Contract tests (T006-T010) → Implementation (T017-T030)
- Integration tests (T011-T016) → Services & Endpoints (T023-T029)

**Implementation Dependencies:**
- T001,T002 → All other tasks (project setup required)
- T005,T017,T018 → T023,T024,T031 (database models before services)
- T019,T020,T021,T022 → T023,T024 (utilities before services)
- T023,T024 → T025,T026,T027,T028 (services before endpoints)
- T030 → T025,T026,T027,T028 (schemas before endpoints)
- T031 → T032,T033,T034 (database connection before middleware)
- All implementation → Polish tasks (T035-T039)

## Parallel Execution Examples

### Phase 3.2: Run all contract tests simultaneously
```bash
# All contract tests can run in parallel (different files)
Task: "Contract test POST /auth/login in backend/tests/contract/test_auth_login.py"
Task: "Contract test POST /auth/logout in backend/tests/contract/test_auth_logout.py"
Task: "Contract test POST /auth/refresh in backend/tests/contract/test_auth_refresh.py"
Task: "Contract test GET /auth/verify in backend/tests/contract/test_auth_verify.py"
Task: "Contract test GET /health in backend/tests/contract/test_health.py"
```

### Phase 3.2: Run all integration tests simultaneously
```bash
# All integration tests can run in parallel (different files)
Task: "Integration test valid user login flow in backend/tests/integration/test_login_flow.py"
Task: "Integration test token verification by services in backend/tests/integration/test_token_verification.py"
Task: "Integration test token refresh functionality in backend/tests/integration/test_token_refresh.py"
Task: "Integration test logout and token invalidation in backend/tests/integration/test_logout_flow.py"
Task: "Integration test rate limiting protection in backend/tests/integration/test_rate_limiting.py"
Task: "Integration test input validation and error handling in backend/tests/integration/test_validation.py"
```

### Phase 3.3: Parallel utility development
```bash
# Utilities can be developed in parallel (different files)
Task: "Password hashing utilities with bcrypt in backend/src/utils/password.py"
Task: "JWT token generation and validation utilities in backend/src/utils/jwt_utils.py"
Task: "Rate limiting utilities with in-memory storage in backend/src/utils/rate_limiter.py"
Task: "Token blacklist management utilities in backend/src/utils/token_blacklist.py"
```

## Notes
- **[P] tasks** = different files, no dependencies between them
- **Verify tests fail** before implementing (TDD principle)
- **Commit after each task** for atomic changes
- **Port 8001** as specified in implementation requirements
- **SQLite database** for development, PostgreSQL upgrade path maintained

## Task Generation Rules Applied

1. **From Contracts (auth-api.yml)**:
   ✓ POST /auth/login → T006 contract test + T025 implementation
   ✓ POST /auth/logout → T007 contract test + T026 implementation
   ✓ POST /auth/refresh → T008 contract test + T027 implementation
   ✓ GET /auth/verify → T009 contract test + T028 implementation
   ✓ GET /health → T010 contract test + T029 implementation

2. **From Data Model (data-model.md)**:
   ✓ User entity → T017 model creation
   ✓ JWT tokens → T020 JWT utilities
   ✓ Rate limiting → T021 rate limiter
   ✓ Token blacklist → T022 blacklist utilities

3. **From User Stories (quickstart.md)**:
   ✓ Login flow → T011 integration test
   ✓ Token verification → T012 integration test
   ✓ Token refresh → T013 integration test
   ✓ Logout flow → T014 integration test
   ✓ Rate limiting → T015 integration test
   ✓ Input validation → T016 integration test

4. **Ordering Applied**:
   ✓ Setup (T001-T005) → Tests (T006-T016) → Implementation (T017-T034) → Polish (T035-T039)
   ✓ Dependencies prevent parallel execution conflicts

## Validation Checklist ✅

- [x] All 5 endpoints have corresponding contract tests (T006-T010)
- [x] User entity has model creation task (T017)
- [x] All contract tests come before implementation (T006-T010 → T025-T029)
- [x] Parallel tasks truly independent (different files verified)
- [x] Each task specifies exact file path in backend/ structure
- [x] No [P] task modifies same file as another [P] task
- [x] All 6 user stories have integration tests (T011-T016)
- [x] TDD principles enforced (tests before implementation)
- [x] Dependencies properly sequenced for atomic development