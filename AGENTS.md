# Repository Guidelines

## Project Structure & Module Organization
- `frontend/` delivers the Next.js TypeScript client; main code resides in `src/`, shared utilities live under `src/lib`, tests sit in `tests/`, and static assets in `public/`.
- `services/` bundles the microservices: `auth-service/` and `product-catalog-service/` (FastAPI) plus `cart-service/` (Node/Express). Runtime logic is under `src/`; layer-specific suites live in `tests/{unit,integration,contract}`.
- `specs/` stores scenario briefs that guide delivery. Update the relevant doc whenever behaviour or acceptance criteria changes.
- Root orchestration (`docker-compose.yml`, `Makefile`) wires services together; each service owns its Dockerfile and environment sample.

## Build, Test, and Development Commands
- `make up`, `make down`, `make logs SERVICE=name`, and `make clean` manage the Docker lifecycle; scope to one component with `SERVICE=<service>`.
- Frontend: `npm install`, `npm run dev`, `npm run build`, `npm run lint`, and `npm run format:check` cover development, production builds, and formatting gates.
- Cart service: `npm install`, `npm run dev`, `npm run test:api`, `npm run lint:fix`, and `npm run db:reset` keep Express, Jest, and SQLite workflows healthy.
- Python services: create a virtualenv, `pip install -e .[dev,test]`, launch `uvicorn src.main:app --reload`, and run `pytest` for the bundled FastAPI suites.

## Coding Style & Naming Conventions
- JavaScript/TypeScript uses Prettier (2-space indentation) and the Next flat ESLint config. Prefer PascalCase for React components, camelCase for helpers, and kebab-case for filenames and directories.
- Python is auto-formatted with Black (88 columns) and linted by Flake8; modules remain snake_case, classes PascalCase, and async endpoints follow `verb_resource` naming.
- Commit generated types in `frontend/src/types` only when required by the build; otherwise regenerate locally.

## Testing Guidelines
- Jest drives the frontend and cart-service checks; place specs in the relevant `tests/` subfolder and name them `*.test.ts[x]` or `*.test.js`.
- Pytest discovers `tests/test_*.py`; `pytest-asyncio` is preconfigured, and coverage reports (`--cov=src --cov-report=term-missing`) run by default.
- Execute `npm run test:coverage` or `pytest` before PRs and reset SQLite fixtures via `npm run db:reset` or `make clean` when integration data drifts.

## Commit & Pull Request Guidelines
- Follow the existing history—short, present-tense subjects such as `lint fixes` or `docker setup update`, ideally under 60 characters.
- Branch from `main`, rebase before pushing, and confirm linting/tests are green locally or via CI.
- PRs should link the relevant `specs/` entry, summarise the change, list verification steps, and attach screenshots for UI adjustments; request review from the accountable service team.
