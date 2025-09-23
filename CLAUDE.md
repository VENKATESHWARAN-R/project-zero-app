<!--
CLAUDE.md
Purpose: Single, concise source of truth for AI (Claude) and humans about
project background, active service scope, run instructions, environment, endpoints,
dependencies, and required documentation hygiene.
Keep focused: project + plan + background + operational contract. No sprawling guides.
If you (Claude) modify code, you MUST update impacted service README(s) and this file if scope changes.
-->

# Project Zero App – Core Background & AI Collaboration Guide

Last Updated: 2025-09-23

## 1. Project Background

Project Zero App is an e-commerce demonstration platform built as a polyglot microservice system to showcase: (a) realistic service boundaries, (b) security analysis targets, (c) DevOps & observability patterns, and (d) specification‑driven delivery. The current focus is a hardened Authentication Service (Auth Service) providing identity and token lifecycle management for future product, order, cart, payment, and notification domains.

Core Objectives:

- Demonstrate clean, auditable microservice patterns
- Provide security primitives (JWT, rate limiting, password hygiene)
- Maintain explicit, minimal architecture documentation for AI agents
- Enforce a change discipline: code ↔ docs ↔ specs stay synchronized

## 2. High-Level Architecture (Current Snapshot)

```text
Frontend (Planned) ──► API Gateway (Planned, Go)
                                                     │
                                                     ├── Auth Service (Active, FastAPI)
                                                     ├── Product Catalog (Planned)
                                                     ├── Cart (Planned)
                                                     ├── Order (Planned)
                                                     ├── Payment (Planned)
                                                     ├── User Profile (Planned)
                                                     └── Notification (Planned)
```

Foundational Infra (incremental): Docker, future Kubernetes (GKE), Terraform (GCP), PostgreSQL (primary RDBMS), Redis (caching/session/token blacklist), structured logging.

## 3. Active Service: Auth Service

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

## 4. API Surface (Auth Service)

Implemented:

- POST `/auth/login` – Authenticate user; returns access + refresh tokens
- POST `/auth/logout` – Invalidate a refresh token
- POST `/auth/refresh` – Exchange refresh for new access token
- GET  `/auth/verify` – Validate access token (used by other services)
- GET  `/health` – Liveness & basic DB check
- GET  `/health/ready` – Readiness probe

Planned (Not Yet Exposed):

- POST `/auth/register` – User self‑registration (service logic baseline exists)

Response & error formats follow FastAPI / Pydantic conventions with JSON bodies and standard HTTP status codes (200 / 401 / 422 / 429 / 500). Rate limiting surfaces 429 with a retry message.

## 5. Environment Variables (Auth Service)

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

If adding new environment variables: (1) update this table, (2) update `services/auth-service/README.md`, (3) ensure tests reflect new configuration.

## 6. Local Development (Auth Service)

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

## 7. Docker Packaging & Execution

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

## 8. Service Dependencies & External Interactions

Current External Dependencies:

- Database: SQLite (dev) / PostgreSQL (planned prod)
- In-Memory / Cache (Planned): Redis for token blacklist / rate data

Incoming Callers (Future): Product, Order, Cart, Payment, Profile services will call `GET /auth/verify` to validate tokens. API Gateway will forward auth endpoints transparently.

No outbound calls to other microservices are currently implemented. When adding any new outbound integration, document: (a) target base URL / discovery mechanism, (b) request contract, (c) failure handling & timeout policy, (d) retry/backoff strategy.

## 9. AI Assistant (Claude) Contribution Protocol

When acting on this repository, follow Anthropic-aligned engineering collaboration principles:

Golden Rules:

1. Minimize Diff Surface: Change only what the requirement demands.
2. Keep Docs Synchronized: Any code change impacting behavior, interface, configuration, or environment MUST update:
   - `services/auth-service/README.md` (service operational detail)
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
- Order: Order orchestration from cart & payment
- Payment: Payment intent capture (mock or gateway integration)
- User Profile: Non-auth user data (addresses, preferences)
- Notification: Email/SMS/Webhook delivery

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
```

## 14. Changelog (High-Level)

| Date | Change |
|------|--------|
| 2025-09-23 | Initial condensed CLAUDE.md authored; established AI protocol |

---
Maintain this file as a compact operational contract. If it becomes bloated, refactor detail into service-specific READMEs or specs and relink.
