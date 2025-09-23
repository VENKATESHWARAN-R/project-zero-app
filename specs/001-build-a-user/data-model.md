# Data Model: Authentication Service

**Feature**: User Authentication Service
**Date**: 2025-09-23
**Status**: Draft

## Entity Design

### User Entity
**Purpose**: Represents an authenticated user account in the system

#### Core Fields
- `id` (Integer, Primary Key): Unique user identifier
- `email` (String, Unique, Indexed): User's email address for authentication
- `password_hash` (String): Bcrypt-hashed password (never store plaintext)

#### Security Fields
- `is_active` (Boolean, Default: True): Account status flag
- `created_at` (Timestamp): Account creation time
- `failed_login_attempts` (Integer, Default: 0): Counter for rate limiting
- `locked_until` (Timestamp, Nullable): Account lockout expiration time

#### Validation Rules
- **Email**: RFC 5322 compliant, unique across system
- **Password**: Minimum 8 characters, mixed case, numbers required
- **Password Hash**: Always bcrypt with 12 salt rounds
- **Account Lockout**: 15 minutes after 5 failed attempts

#### Relationships
- None (minimal authentication service)

### Access Token Entity (JWT)
**Purpose**: Short-lived token for API access authorization

#### JWT Claims
- `user_id` (Integer): Reference to User.id
- `type` (String): "access" token type identifier
- `exp` (Timestamp): Expiration time (15 minutes from issue)
- `iat` (Timestamp): Issued at time
- `jti` (String, UUID): Unique token identifier for blacklisting

#### Security Rules
- **Algorithm**: HS256 for demo simplicity
- **Expiration**: 15 minutes maximum lifetime
- **Validation**: Must verify signature and expiration
- **Revocation**: Support blacklisting via JTI

### Refresh Token Entity (JWT)
**Purpose**: Long-lived token for obtaining new access tokens

#### JWT Claims
- `user_id` (Integer): Reference to User.id
- `type` (String): "refresh" token type identifier
- `exp` (Timestamp): Expiration time (7 days from issue)
- `iat` (Timestamp): Issued at time
- `jti` (String, UUID): Unique token identifier for blacklisting

#### Security Rules
- **Algorithm**: HS256 for demo simplicity
- **Expiration**: 7 days maximum lifetime
- **Single Use**: Should be rotated on refresh (future enhancement)
- **Revocation**: Support blacklisting via JTI

### Token Blacklist Entity (In-Memory)
**Purpose**: Track revoked tokens until natural expiration

#### Structure
```python
blacklisted_tokens = {
    "jti_uuid_string": expiration_timestamp,
    # Cleaned up when expiration_timestamp < current_time
}
```

#### Operations
- **Add**: Store JTI with expiration time on logout
- **Check**: Verify JTI not in blacklist during validation
- **Cleanup**: Remove expired entries periodically

### Rate Limit Entity (In-Memory)
**Purpose**: Track login attempts for brute force protection

#### Structure
```python
rate_limits = {
    "user_email_or_ip": {
        "attempts": count,
        "window_start": timestamp,
        "locked_until": timestamp_or_none
    }
}
```

#### Rules
- **Window**: 15 minutes rolling window
- **Limit**: 5 attempts per window
- **Lockout**: 15 minutes after exceeding limit
- **Reset**: Clear counter after successful login

## State Transitions

### User Authentication State
```
[Unregistered] → [Active] → [Locked] → [Active]
                     ↓
                [Inactive]
```

#### State Rules
- **Active**: Can authenticate and use services
- **Locked**: Temporarily blocked due to failed attempts
- **Inactive**: Account disabled (future enhancement)

### Token Lifecycle
```
[Issued] → [Valid] → [Expired/Revoked]
            ↓
        [Blacklisted]
```

#### Lifecycle Rules
- **Issued**: Generated during successful authentication
- **Valid**: Can be used for API access until expiration
- **Expired**: Natural expiration, no longer valid
- **Blacklisted**: Manually revoked via logout
- **Revoked**: Explicitly invalidated (security incident)

## Data Integrity Constraints

### Database Constraints
- `users.email` UNIQUE INDEX for fast lookups
- `users.id` PRIMARY KEY auto-increment
- `users.password_hash` NOT NULL (never empty)
- `users.created_at` DEFAULT CURRENT_TIMESTAMP

### Application Constraints
- Never store plaintext passwords
- Always validate JWT signatures
- Check token blacklist before accepting tokens
- Enforce rate limits before authentication attempts
- Clean up expired in-memory data structures

### Security Constraints
- Passwords must meet complexity requirements
- Tokens must have proper expiration times
- Failed attempts must increment counters
- Account lockouts must be time-limited
- All authentication events should be logged

## Performance Considerations

### Database Indexes
- `users.email` (unique, for login lookups)
- `users.id` (primary key, for token validation)

### Memory Management
- Blacklist cleanup every 5 minutes
- Rate limit cleanup every hour
- Maximum 1000 entries per in-memory structure

### Query Patterns
- User lookup by email (login)
- User lookup by ID (token validation)
- Blacklist check by JTI (token validation)
- Rate limit check by email/IP (login protection)

This data model supports all functional requirements while maintaining simplicity and performance for a demo authentication service.