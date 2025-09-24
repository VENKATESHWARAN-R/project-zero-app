# AI Coding Assistant Guide (Project Zero App)

Single-page operational rules for productive, safe changes. Keep code ↔ docs ↔ specs in sync.

## Snapshot
Active services: `auth-service` (FastAPI), `product-catalog-service` (FastAPI), `cart-service` (Node/Express), `frontend` (Next.js). Shared: `/health` + `/health/ready`, OpenAPI at `/:port/docs`, JWT verify via `GET /auth/verify` only.

## Boundaries
Auth = identity + access/refresh issuance + verify. Product = public catalog + admin CRUD (JWT). Cart = per‑user cart; validates product + token (no refresh). Frontend consumes REST only.

## Change Discipline
Touch minimum. If endpoint/env/schema/response shape changes: update affected README + `CLAUDE.md` (if cross‑service) + spec. Add/adjust tests same diff. No silent schema or security downgrades.

## Critical Conventions
1. Health endpoints stay trivial (<1 lightweight DB call max).
2. Product routes: declare `/products/search` & `/products/category/{c}` before `/products/{id}`.
3. Product service seeds 20 deterministic products – keep IDs/categories stable when extending.
4. Only auth service handles refresh logic; others just validate access tokens.
5. Reuse existing error/validation schema patterns (FastAPI models; cart structured JSON errors).

## Env Vars
When adding: (a) doc table in service README, (b) add to `CLAUDE.md` if cross‑cutting, (c) safe default or mark required, (d) load via config/env lookup—not hardcoded.

## Testing Rules
Contract tests for API shape/status changes; integration for multi‑step flows (e.g., product CRUD, cart modify cycle); unit for logic. Frontend: new interactive component → minimal RTL render + key interaction.

## Security Guardrails
Bcrypt rounds = 12 (auth). Access TTL ≈15m / refresh 30d. Never log secrets/tokens/passwords. Rate limit / lockout changes must add boundary tests.

## Pitfalls to Avoid
Circular service calls (only downstream → auth verify). Undocumented DB migrations. Over‑abstracting utilities early. Expanding frontend API usage without updating `src/services/*`.

## Quick Commands
```bash
# Auth
cd services/auth-service && uv sync && uv run uvicorn main:app --reload --port 8001
# Product
cd services/product-catalog-service && uv sync && uv run uvicorn src.main:app --reload --port 8004
# Cart
cd services/cart-service && yarn install && yarn db:migrate && yarn dev
# Frontend
cd frontend && npm install && npm run dev
```

Tests: Python `uv run pytest`; Cart `yarn test[:integration|:contract]`; Frontend `npm run test && npm run type-check`.
Lint/Format: Auth = black/flake8; Product = ruff; Cart/Frontend = eslint + prettier.

## When Unsure
Read `CLAUDE.md` → service README → relevant `specs/*`. Mirror patterns; do not invent new workflow.

PR Exit Check: build, lint, tests green; docs updated; security posture unchanged or improved.
