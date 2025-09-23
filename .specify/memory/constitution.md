# Project Zero App Constitution

## Core Philosophy

- **Simplicity First**: Choose the simplest solution that works
- **Functionality Over Complexity**: Working features beat elaborate architectures
- **Progressive Enhancement**: Start minimal, add complexity only when needed
- **Demo-Focused**: Prioritize demonstrable features over production-scale optimizations

## Development Standards

- **Backend Simplicity**: Use FastAPI with minimal dependencies
- **One Responsibility**: Each service does exactly one thing well
- **Stateless Services**: Services should be stateless and independently deployable
- **Rich Frontend**: UI can be visually appealing while keeping logic simple
- **Mock External Dependencies**: Payment gateways, email services, etc. should be mocked

## Security

- Include common security patterns
- All services must implement basic authentication/authorization
- Secrets management
- Input validation
- Dependencies with known vulnerabilities for scanning demos

## Observability (Simple but Functional)

- Basic structured logging (JSON format)
- Simple health checks (/health endpoint)
- Basic metrics (request count, response time...)
- Avoid complex monitoring setup initially

## Technology Constraints

- **Frontend**: Next.js with TypeScript + Tailwind CSS + Shadcn UI
- **Python Services**: FastAPI + SQLAlchemy + Pydantic
- **Node.js Services**: Express.js (for 1-2 simple services)
- **Databases**: PostgreSQL primary, Redis for caching
- **Container**: Docker for all services
- **Local Development**: Docker Compose

**Version**: 0.0.1 | **Ratified**: 2025-09-23 | **Last Amended**: 2025-09-23
