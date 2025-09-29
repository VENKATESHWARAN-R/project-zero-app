<!--
GEMINI.md
Purpose: Single, concise source of truth for AI (Claude) and humans about
project background, active service scope, run instructions, environment, endpoints,
dependencies, and required documentation hygiene.
Keep focused: project + plan + background + operational contract. No sprawling guides.
If you (Claude) modify code, you MUST update impacted service README(s) and this file if scope changes.
-->

# Project Zero App – Core Background & AI Collaboration Guide

Last Updated: 2025-09-28

## 1. Project Background

Project Zero App is an e-commerce demonstration platform built as a polyglot microservice system to showcase: (a) realistic service boundaries, (b) security analysis targets, (c) DevOps & observability patterns, and (d) specification‑driven delivery. Active services include a hardened Authentication Service (Auth Service) for identity and token lifecycle management, an Order Processing Service (Order Service) handling complete order workflows from cart checkout to delivery, and a Notification Service managing all user communications via email, SMS, and in-app channels.

Core Objectives:

- Demonstrate clean, auditable microservice patterns
- Provide security primitives (JWT, rate limiting, password hygiene)
- Maintain explicit, minimal architecture documentation for AI agents
- Enforce a change discipline: code ↔ docs ↔ specs stay synchronized

## 2. High-Level Architecture (Current Snapshot)

```text
Frontend (Planned) ──► API Gateway (Active, Go)
                                                     │
                                                     ├── Auth Service (Active, FastAPI)
                                                     ├── Order Service (Active, FastAPI)
                                                     ├── User Profile Service (Active, FastAPI)
                                                     ├── Product Catalog (Active, FastAPI)
                                                     ├── Cart Service (Active, Node.js)
                                                     ├── Payment Service (Active, FastAPI)
                                                     └── Notification Service (Active, Node.js)
```

Foundational Infra (incremental): Docker, future Kubernetes (GKE), Terraform (GCP), PostgreSQL (primary RDBMS), Redis (caching/session/token blacklist), structured logging.

## 3. Active Services

### API Gateway Service

Purpose: Single entry point for all client requests to the Project Zero App platform. Provides intelligent request routing, authentication middleware, rate limiting, circuit breaking, and observability for the microservices ecosystem.

Responsibilities (In-Scope Now):

- Request routing to backend microservices (auth:8001, profile:8002, products:8004, cart:8007, orders:8008, payments:8009)
- JWT authentication middleware with central auth service integration
- Rate limiting using token bucket algorithm (configurable per-IP, per-user, or global)
- Circuit breaker patterns for resilience and automatic failure detection
- Service discovery with health checks for all registered services
- CORS support for cross-origin requests
- Structured JSON logging with correlation IDs for distributed tracing
- Graceful shutdown handling and resource cleanup

Out of Scope (Until Explicitly Planned):

- Load balancing algorithms beyond round-robin
- Advanced routing features (path rewriting, request transformation)
- OAuth2/OIDC integration beyond JWT validation
- API versioning and backward compatibility
- Advanced observability (Prometheus metrics, distributed tracing)

### Auth Service

Purpose: Central authority for user identity, credential validation, token issuance (access + refresh), token verification, logout / invalidation, and basic account protection (failed login throttling & lockout).

Responsibilities (In-Scope Now):

- Email/password authentication
- bcrypt password hashing (12 rounds default)
- JWT access + refresh token issuance & rotation
- Token verification endpoint for other services
- Rate limiting & failed login lockout logic
- Health & readiness reporting

Out of Scope (Until Explicitly Planned):

- OAuth/OIDC social login
- MFA / TOTP
- Password reset flows
- User profile management (beyond authentication basics)
- Inter-service event publishing

### Order Service

Purpose: Complete order lifecycle management for e-commerce operations. Handles order creation from cart checkout, tax and shipping calculations, status tracking, and integration with auth, cart, and product catalog services.

Responsibilities (In-Scope Now):

- Order creation from cart with tax and shipping calculation
- Complete CRUD operations for orders with status-based workflows
- Admin interface for order management across all users
- Weight-based shipping cost calculation with multiple tiers
- Status tracking with complete order lifecycle management and audit trails
- Service integration with auth, cart, and product catalog services

Out of Scope (Until Explicitly Planned):

- Payment processing integration
- Real-time order notifications
- Advanced shipping provider integrations
- Order fulfillment automation
- Inventory reservation

### Notification Service

Purpose: Comprehensive communication hub for all user notifications in the Project Zero App ecosystem. Handles multi-channel notifications (email, SMS, in-app), template management, user preferences, and scheduled delivery for order confirmations, welcome messages, payment confirmations, and system alerts.

Responsibilities (In-Scope Now):

- Multi-channel notification delivery (email, SMS, in-app) with mock providers
- Template-based notification system with variable substitution
- Immediate and scheduled notification delivery with retry logic
- User notification preference management with granular controls
- Notification history and audit trail for all communications
- JWT authentication integration with auth service
- RESTful API for notification triggering from other services
- Health monitoring and readiness checks with dependency validation

Out of Scope (Until Explicitly Planned):

- Real email/SMS provider integration (Sendgrid, Twilio)
- Advanced notification batching and bulk operations
- Real-time push notifications and WebSocket integration
- Notification analytics and delivery tracking
- A/B testing for notification content
- Rich media notifications (images, attachments)

## 4. API Surface

### API Gateway Service

Implemented:

- GET `/health` – Gateway health check
- GET `/health/ready` – Gateway readiness check including dependency health
- GET `/gateway/services` – List registered services with health status
- GET `/gateway/routes` – List configured routing rules
- GET `/gateway/metrics` – Performance and usage metrics
- ANY `/api/*` – Proxy routing to backend services based on path patterns

Routing Configuration:

- `/api/auth/*` → Auth Service (no authentication required)
- `/api/profile/*` → User Profile Service (authentication required)
- `/api/products/*` → Product Catalog Service (no authentication required)
- `/api/cart/*` → Cart Service (authentication required)
- `/api/orders/*` → Order Service (authentication required)
- `/api/payments/*` → Payment Service (authentication required)
- `/api/notifications/*` → Notification Service (authentication required)

### Auth Service

Implemented:

- POST `/auth/login` – Authenticate user; returns access + refresh tokens
- POST `/auth/logout` – Invalidate a refresh token
- POST `/auth/refresh` – Exchange refresh for new access token
- GET  `/auth/verify` – Validate access token (used by other services)
- GET  `/health` – Liveness & basic DB check
- GET  `/health/ready` – Readiness probe

Planned (Not Yet Exposed):

- POST `/auth/register` – User self‑registration (service logic baseline exists)

### Order Service

Implemented:

- POST `/orders` – Create order from cart
- GET `/orders` – Get user order history
- GET `/orders/{id}` – Get order details
- PATCH `/orders/{id}` – Modify order (status-dependent)
- POST `/orders/{id}/cancel` – Cancel order
- PUT `/orders/{id}/status` – Update order status (admin)
- GET `/orders/{id}/status-history` – Get status history
- GET `/admin/orders` – Get all orders (admin only)
- PUT `/admin/orders/{id}/status` – Admin status updates
- POST `/shipping/calculate` – Calculate shipping cost
- GET `/shipping/rates` – Get available shipping rates
- GET `/health` – Basic health check
- GET `/health/ready` – Readiness check with dependencies

Response & error formats follow FastAPI / Pydantic conventions with JSON bodies and standard HTTP status codes (200 / 401 / 422 / 429 / 500). Rate limiting surfaces 429 with a retry message.

### Notification Service

Implemented:

- POST `/notifications` – Send immediate notification to user
- GET `/notifications` – Get user notification history (paginated, filtered)
- GET `/notifications/{id}` – Get specific notification details
- POST `/notifications/schedule` – Schedule notification for future delivery
- POST `/notifications/template` – Send notification using predefined template
- GET `/templates` – List available notification templates (filtered)
- POST `/templates` – Create new notification template (admin only)
- GET `/templates/{id}` – Get template details and variables
- PUT `/templates/{id}` – Update existing template (admin only)
- GET `/preferences` – Get user notification preferences
- PUT `/preferences` – Update user notification preferences
- GET `/health` – Basic health check
- GET `/health/ready` – Readiness check with auth service connectivity

Response & error formats follow Express.js conventions with JSON bodies and standard HTTP status codes (200 / 401 / 422 / 429 / 500). Rate limiting surfaces 429 with retry-after headers. Authentication required for all endpoints except health checks.

## 5. Environment Variables

### API Gateway Service

| Name | Purpose | Typical Value (Dev) | Required | Notes |
|------|---------|---------------------|----------|-------|
| `GATEWAY_SERVER_HOST` | Bind address | `0.0.0.0` | No | Set explicitly in containers |
| `GATEWAY_SERVER_PORT` | Service port | `8000` | No | Main entry point for all requests |
| `GATEWAY_AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | Yes | Used for JWT token validation |
| `GATEWAY_RATE_LIMIT_REQUESTS` | Requests per window | `100` | No | Rate limiting threshold |
| `GATEWAY_RATE_LIMIT_WINDOW` | Rate limit window | `1m` | No | Time window for rate limiting |
| `GATEWAY_RATE_LIMIT_BURST` | Burst capacity | `200` | No | Maximum burst requests allowed |
| `GATEWAY_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Failure threshold | `0.6` | No | Circuit breaker trigger ratio |
| `GATEWAY_LOGGING_LEVEL` | Log level | `info` | No | debug, info, warn, error |

### Auth Service

| Name | Purpose | Typical Value (Dev) | Required | Notes |
|------|---------|---------------------|----------|-------|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./auth_service.db` | No | Use PostgreSQL in prod (`postgresql://user:pass@host:5432/db`) |
| `JWT_SECRET_KEY` | HMAC secret for JWT signing | (generated if absent) | Recommended | Provide strong 256-bit value in prod |
| `JWT_ALGORITHM` | Signing algorithm | `HS256` | No | Keep consistent system‑wide |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `15` | No | Short-lived, security boundary |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `30` | No | Rotation & revocation supported |
| `BCRYPT_ROUNDS` | Password hashing cost | `12` | No | Adjust carefully; impacts latency |
| `HOST` | Bind host | `0.0.0.0` | No | Set explicitly in containers |
| `PORT` | Service port | `8001` | No | Exposed internally via gateway |

### Order Service

| Name | Purpose | Typical Value (Dev) | Required | Notes |
|------|---------|---------------------|----------|-------|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./order_service.db` | No | Use PostgreSQL in prod (`postgresql://user:pass@host:5432/db`) |
| `JWT_SECRET_KEY` | HMAC secret for JWT signing (must match auth service) | Auto-generated | Recommended | Provide strong 256-bit value in prod |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | Yes | Used for token verification |
| `CART_SERVICE_URL` | Cart service URL | `http://localhost:8007` | Yes | Used for cart retrieval |
| `PRODUCT_SERVICE_URL` | Product catalog URL | `http://localhost:8004` | Yes | Used for product validation |
| `TAX_RATE` | Fixed tax rate | `0.085` (8.5%) | No | Applied to order subtotal |
| `HOST` | Bind host | `0.0.0.0` | No | Set explicitly in containers |
| `PORT` | Service port | `8008` | No | Exposed internally via gateway |

### Notification Service

| Name | Purpose | Typical Value (Dev) | Required | Notes |
|------|---------|---------------------|----------|-------|
| `DATABASE_URL` | SQLite database URL | `sqlite:///notification_service.db` | No | Use PostgreSQL in prod (`postgresql://user:pass@host:5432/db`) |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` | Yes | Used for JWT token verification |
| `USER_PROFILE_SERVICE_URL` | User profile service URL | `http://localhost:8002` | No | Used for user contact information |
| `JWT_SECRET_KEY` | HMAC secret for JWT verification (must match auth service) | Auto-generated | Recommended | Provide strong 256-bit value in prod |
| `NODE_ENV` | Environment mode | `development` | No | Controls features and logging |
| `LOG_LEVEL` | Logging verbosity | `info` | No | debug, info, warn, error |
| `HOST` | Bind host | `0.0.0.0` | No | Set explicitly in containers |
| `PORT` | Service port | `8011` | No | Exposed internally via gateway |

If adding new environment variables: (1) update this table, (2) update respective service README, (3) ensure tests reflect new configuration.

## 6. Local Development

### API Gateway Service

Prerequisites: Go 1.20+, Docker (optional).

Quick Start:

```bash
cd services/api-gateway-service
go mod tidy
go build -o gateway ./cmd/gateway
./gateway
# Visit: http://localhost:8000/health
```

Run Tests:

```bash
go test ./...                           # all tests
go test ./tests/contract/...            # contract tests
go test -cover ./...                    # with coverage
```

Lint & Format:

```bash
gofmt -w .
golangci-lint run
```

### Auth Service

Prerequisites: Python 3.13+, `uv` installed, optional Docker / PostgreSQL.

Quick Start:

```bash
cd services/auth-service
uv sync                                    # install deps
uv run uvicorn main:app --reload --port 8001
# Visit: http://localhost:8001/docs
```

Using SQLite (default) requires no extra setup. For PostgreSQL:

```bash
export DATABASE_URL=postgresql://authuser:pass@localhost:5432/authdb
uv run uvicorn main:app --port 8001
```

Run Tests:

```bash
uv run pytest            # all tests
uv run pytest tests/contract/
uv run pytest --cov=src --cov-report=term-missing
```

Lint & Format:

```bash
uv run ruff check .
uv run ruff format .
```

### Order Service

Prerequisites: Python 3.13+, `uv` installed, optional Docker / PostgreSQL.

Quick Start:

```bash
cd services/order-service
uv sync                                    # install deps
uv run uvicorn main:app --reload --port 8008
# Visit: http://localhost:8008/docs
```

Using SQLite (default) requires no extra setup. For PostgreSQL:

```bash
export DATABASE_URL=postgresql://orderuser:pass@localhost:5432/orderdb
uv run uvicorn main:app --port 8008
```

Run Tests:

```bash
uv run pytest            # all tests
uv run pytest tests/contract/
uv run pytest --cov=src --cov-report=term-missing
```

Lint & Format:

```bash
uv run ruff check .
uv run ruff format .
```

### Notification Service

Prerequisites: Node.js 18+, npm installed, optional Docker.

Quick Start:

```bash
cd services/notification-service
npm install                             # install deps
npm run dev                            # start with nodemon
# Visit: http://localhost:8011/health
# Visit: http://localhost:8011/docs
```

Using SQLite (default) requires no extra setup. For PostgreSQL:

```bash
export DATABASE_URL=postgresql://notificationuser:pass@localhost:5432/notificationdb
export AUTH_SERVICE_URL=http://localhost:8001
npm start
```

Run Tests:

```bash
npm test                               # all tests
npm run test:contract                  # contract tests
npm run test:coverage                  # with coverage
```

Lint & Format:

```bash
npm run lint                           # check code quality
npm run lint:fix                       # auto-fix issues
npm run format                         # format code
```

## 7. Docker Packaging & Execution

### Auth Service

Build Image:

```bash
cd services/auth-service
docker build -t auth-service:latest .
```

Run Container (ephemeral SQLite):

```bash
docker run -p 8001:8001 \
    -e JWT_SECRET_KEY="change-me-dev" \
    auth-service:latest
```

Run with PostgreSQL:

```bash
docker network create project-zero-net || true
docker run -d --name auth-db --network project-zero-net \
    -e POSTGRES_DB=authdb -e POSTGRES_USER=authuser -e POSTGRES_PASSWORD=pass \
    postgres:15

docker run --rm -p 8001:8001 --network project-zero-net \
    -e DATABASE_URL=postgresql://authuser:pass@auth-db:5432/authdb \
    -e JWT_SECRET_KEY="strong-dev-secret" \
    auth-service:latest
```

Health Check: `curl http://localhost:8001/health`

### Order Service

Build Image:

```bash
cd services/order-service
docker build -t order-service:latest .
```

Run Container (ephemeral SQLite):

```bash
docker run -p 8008:8008 \
    -e JWT_SECRET_KEY="change-me-dev" \
    -e AUTH_SERVICE_URL="http://host.docker.internal:8001" \
    -e CART_SERVICE_URL="http://host.docker.internal:8007" \
    -e PRODUCT_SERVICE_URL="http://host.docker.internal:8004" \
    order-service:latest
```

Run with PostgreSQL:

```bash
docker network create project-zero-net || true
docker run -d --name order-db --network project-zero-net \
    -e POSTGRES_DB=orderdb -e POSTGRES_USER=orderuser -e POSTGRES_PASSWORD=orderpass \
    postgres:15

docker run --rm -p 8008:8008 --network project-zero-net \
    -e DATABASE_URL=postgresql://orderuser:orderpass@order-db:5432/orderdb \
    -e JWT_SECRET_KEY="strong-dev-secret" \
    -e AUTH_SERVICE_URL="http://auth-service:8001" \
    -e CART_SERVICE_URL="http://cart-service:8007" \
    -e PRODUCT_SERVICE_URL="http://product-service:8004" \
    order-service:latest
```

Health Check: `curl http://localhost:8008/health`

### Notification Service

Build Image:

```bash
cd services/notification-service
docker build -t notification-service:latest .
```

Run Container (ephemeral SQLite):

```bash
docker run -p 8011:8011 \
    -e AUTH_SERVICE_URL="http://host.docker.internal:8001" \
    -e USER_PROFILE_SERVICE_URL="http://host.docker.internal:8002" \
    notification-service:latest
```

Run with PostgreSQL:

```bash
docker network create project-zero-net || true
docker run -d --name notification-db --network project-zero-net \
    -e POSTGRES_DB=notificationdb -e POSTGRES_USER=notificationuser -e POSTGRES_PASSWORD=notificationpass \
    postgres:15

docker run --rm -p 8011:8011 --network project-zero-net \
    -e DATABASE_URL=postgresql://notificationuser:notificationpass@notification-db:5432/notificationdb \
    -e AUTH_SERVICE_URL="http://auth-service:8001" \
    -e USER_PROFILE_SERVICE_URL="http://user-profile-service:8002" \
    -e NODE_ENV="production" \
    notification-service:latest
```

Health Check: `curl http://localhost:8011/health`

## 8. Service Dependencies & External Interactions

### Auth Service

External Dependencies:
- Database: SQLite (dev) / PostgreSQL (planned prod)
- In-Memory / Cache (Planned): Redis for token blacklist / rate data

Incoming Callers: Order Service calls `GET /auth/verify` to validate tokens. API Gateway will forward auth endpoints transparently.

Outbound Calls: None currently implemented.

### Order Service

External Dependencies:
- Database: SQLite (dev) / PostgreSQL (planned prod)
- Auth Service: JWT token verification via `GET /auth/verify`
- Cart Service: Cart retrieval and clearing (planned integration)
- Product Service: Product validation and details (planned integration)

Incoming Callers: Frontend and API Gateway will call order management endpoints.

Outbound Calls:
- Auth Service for token validation
- Cart Service for cart operations (when implemented)
- Product Service for product validation (when implemented)

When adding new outbound integrations, document: (a) target base URL / discovery mechanism, (b) request contract, (c) failure handling & timeout policy, (d) retry/backoff strategy.

### Notification Service

External Dependencies:
- Database: SQLite (dev) / PostgreSQL (planned prod)
- Auth Service: JWT token verification via `GET /auth/verify`
- User Profile Service: User contact information and preferences (optional graceful degradation)

Incoming Callers: Order Service, Payment Service, and other services will call notification endpoints to trigger user communications.

Outbound Calls:
- Auth Service for JWT token validation (required)
- User Profile Service for user contact information (optional with graceful fallback)

The service implements graceful degradation when external services are unavailable, maintaining core notification functionality even when user profile service is down.

## 9. AI Assistant (Claude) Contribution Protocol

When acting on this repository, follow Anthropic-aligned engineering collaboration principles:

Golden Rules:

1. Minimize Diff Surface: Change only what the requirement demands.
2. Keep Docs Synchronized: Any code change impacting behavior, interface, configuration, or environment MUST update:
   - Affected service README (`services/{service-name}/README.md`)
   - `CLAUDE.md` (if architectural scope or protocol changes)
   - Relevant spec file under `specs/` (if requirement/story altered)
3. Explicit Contracts: Before altering endpoints or env vars, restate the proposed contract (input shape, output shape, error modes) in commit message or PR description.
4. Security Preservation: Do not weaken password hashing, token lifetimes, or secret handling without explicit rationale.
5. Test Discipline: Add or adjust tests FIRST (or same diff) to reflect new/changed behavior.
6. Deterministic Steps: Provide reproducible commands for new workflows.
7. Transparency: Summarize rationale for non-trivial refactors (why + impact).

Checklist Before Completing a Change:

- [ ] Code compiles / lints cleanly
- [ ] Tests added/updated & passing
- [ ] README for affected service updated
- [ ] `CLAUDE.md` updated if cross-cutting change
- [ ] API and env var tables aligned
- [ ] Security considerations re-evaluated

Forbidden Without Justification: silent schema changes, secret hardcoding, removing validations, broad refactors lacking necessity.

## 10. Minimal Plan Template (For New Service or Major Feature)

Use this lightweight structure (avoid over‑specifying early):

```text
Title: <Concise Feature Name>
Goal: <Business / platform outcome>
Scope: <In / Out of scope bullets>
Interfaces: <Endpoints + payload summary>
Data: <New tables / fields / migrations>
Risks: <Top 3>
Test Strategy: <Key categories>
Done Criteria: <Observable conditions>
```

Store detailed expansions in `specs/<feature-id>/`.

## 11. Documentation Update Matrix

| Change Type | Update README | Update CLAUDE.md | Update Specs | Notes |
|-------------|---------------|------------------|--------------|-------|
| Add/Modify Endpoint | Yes | If cross-service impact | Yes | Include request/response |
| New Env Var | Yes | Yes | Maybe | Add to env table |
| Security Policy Change | Yes | Yes | Yes | Justify risk/benefit |
| Internal Refactor (no interface change) | Optional | No | No | Note in changelog if large |
| Dependency Upgrade (security/major) | Yes | Maybe | Maybe | Capture migration notes |

## 12. Future Services (Outline Only)

Do not expand here until activated. Each future service will replicate documentation pattern: purpose, endpoints, env, run, dependencies.

- Product Catalog: Read/search products
- Cart: Session-based cart aggregation
- Payment: Payment intent capture (mock or gateway integration)
- User Profile: Non-auth user data (addresses, preferences)
- ~~Notification: Email/SMS/Webhook delivery~~ (COMPLETED)

## 13. Quick Reference Commands

```bash
# Auth service dev
cd services/auth-service && uv sync && uv run uvicorn main:app --reload --port 8001

# Tests & coverage
uv run pytest --cov=src --cov-report=term-missing

# Lint & format
uv run ruff check . && uv run ruff format .

# Docker build & run
docker build -t auth-service:latest services/auth-service
docker run -p 8001:8001 auth-service:latest

# Health probe
curl -s http://localhost:8001/health | jq '.'

# Order service dev
cd services/order-service && uv sync && uv run uvicorn main:app --reload --port 8008

# Docker build & run order service
docker build -t order-service:latest services/order-service
docker run -p 8008:8008 order-service:latest

# Order service health probe
curl -s http://localhost:8008/health | jq '.'

# Notification service dev
cd services/notification-service && npm install && npm run dev

# Tests & coverage
npm test && npm run test:coverage

# Lint & format
npm run lint && npm run format

# Docker build & run notification service
docker build -t notification-service:latest services/notification-service
docker run -p 8011:8011 -e AUTH_SERVICE_URL=http://host.docker.internal:8001 notification-service:latest

# Notification service health probe
curl -s http://localhost:8011/health | jq '.'

# Test notification API
curl -s http://localhost:8011/docs
```

## 14. Changelog (High-Level)

| Date | Change |
|------|--------|
| 2025-09-23 | Initial condensed CLAUDE.md authored; established AI protocol |
| 2025-09-25 | Order Processing Service implemented with complete order lifecycle management, tax/shipping calculation, status tracking, and microservice integrations |
| 2025-09-28 | Notification Service implemented with multi-channel communications (email, SMS, in-app), template management, user preferences, scheduled delivery, and comprehensive API documentation |

---
Maintain this file as a compact operational contract. If it becomes bloated, refactor detail into service-specific READMEs or specs and relink.
