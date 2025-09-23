# Research: Authentication Service Best Practices

**Feature**: User Authentication Service
**Date**: 2025-09-23
**Status**: Complete

## JWT Token Management

### Decision: Access Token 15 minutes, Refresh Token 7 days
**Rationale**: Short access token lifespan minimizes security exposure while 7-day refresh tokens maintain user experience
**Alternatives considered**:
- 1-hour access tokens (too long for demo security)
- 1-day refresh tokens (poor user experience)

### Decision: HS256 algorithm with minimal claims
**Rationale**: Simpler implementation for demo purposes, includes only user_id, exp, iat, type claims
**Alternatives considered**: RS256 (too complex for single service demo)

## Password Security

### Decision: bcrypt with 12 salt rounds
**Rationale**: Provides strong security (~250ms per hash) while maintaining reasonable performance
**Alternatives considered**:
- 10 rounds (slightly weaker)
- 14 rounds (slower performance)
- Argon2id (more complex dependency)

### Decision: Basic password validation (8+ chars, mixed case, numbers)
**Rationale**: Balances security with user experience for demo application
**Alternatives considered**:
- Stricter requirements (poor demo UX)
- No requirements (insufficient security)

## Rate Limiting

### Decision: 5 failed attempts per 15 minutes per IP
**Rationale**: Prevents brute force attacks while allowing legitimate user retries
**Alternatives considered**:
- Per-account limiting (more complex implementation)
- Shorter timeouts (poor legitimate user experience)

### Decision: In-memory dict for demo, Redis for production
**Rationale**: Simplifies demo deployment while providing upgrade path
**Alternatives considered**: SQLite storage (slower lookups)

## API Architecture

### Decision: FastAPI dependency injection for authentication
**Rationale**: Clean separation of concerns, easy testing through dependency overrides
**Alternatives considered**: Middleware approach (less flexible)

### Decision: OAuth2PasswordBearer for token handling
**Rationale**: Standards-compliant implementation with automatic OpenAPI documentation
**Alternatives considered**: Custom header handling (reinventing standards)

## Database Design

### Decision: Minimal user model (id, email, password_hash)
**Rationale**: Meets requirements while allowing future extension
**Alternatives considered**: Extended user profile (exceeds current scope)

### Decision: SQLite for development, PostgreSQL upgrade path
**Rationale**: Zero-setup development experience with production upgrade capability
**Alternatives considered**: PostgreSQL from start (complex local setup)

## Token Blacklisting

### Decision: In-memory dict with TTL cleanup for demo
**Rationale**: Simple implementation suitable for single-instance demo
**Alternatives considered**:
- Redis (additional infrastructure for demo)
- Database storage (slower performance)

### Decision: JTI (JWT ID) claims for blacklist tracking
**Rationale**: Standard approach for JWT revocation
**Alternatives considered**: Full token storage (memory inefficient)

## Error Handling

### Decision: Standard HTTP status codes (401, 403, 422, 429)
**Rationale**: Follows REST conventions and enables proper client handling
**Alternatives considered**: Custom error codes (non-standard)

### Decision: Consistent JSON error response format
**Rationale**: Predictable API behavior for client applications
**Alternatives considered**: Plain text errors (less structured)

## Testing Strategy

### Decision: Pytest with FastAPI TestClient
**Rationale**: Official testing approach with dependency override support
**Alternatives considered**: unittest (less FastAPI integration)

### Decision: Separate test database with cleanup
**Rationale**: Isolated tests with predictable state
**Alternatives considered**: Mocked database (less integration coverage)

## Logging and Monitoring

### Decision: Structured JSON logging
**Rationale**: Machine-readable logs for monitoring and debugging
**Alternatives considered**: Plain text logs (harder to parse)

### Decision: Basic health check endpoint
**Rationale**: Enables container orchestration health monitoring
**Alternatives considered**: No health check (operational blind spot)

## Security Considerations Resolved

- **Password storage**: Never store plaintext, always bcrypt hash
- **Token expiration**: Implement proper JWT exp claim validation
- **Input validation**: Use Pydantic models for all API inputs
- **SQL injection**: SQLAlchemy ORM prevents direct SQL construction
- **Rate limiting**: Prevent brute force authentication attacks
- **Token revocation**: Blacklist mechanism for logout functionality

## Implementation Dependencies Finalized

**Core**: fastapi, sqlalchemy, bcrypt, pyjwt, uvicorn
**Validation**: pydantic (included with FastAPI)
**Database**: sqlite3 (Python standard library)
**Testing**: pytest, httpx (for async testing)
**Rate Limiting**: slowapi or manual implementation
**Logging**: Python standard logging module

All technical uncertainties resolved. Ready for Phase 1 design.