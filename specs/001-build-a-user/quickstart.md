# Quickstart: Authentication Service

**Feature**: User Authentication Service
**Date**: 2025-09-23
**Purpose**: Validate implementation against user stories

## Prerequisites
- Python 3.13+
- pip or poetry package manager
- SQLite (included with Python)

## Quick Setup

### 1. Install Dependencies
```bash
pip install fastapi sqlalchemy bcrypt pyjwt uvicorn python-multipart pytest httpx
```

### 2. Start Service
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Verify Health
```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy", "timestamp": "...", "database": "connected"}
```

## User Story Validation

### Story 1: User Login with Valid Credentials
**Scenario**: A customer authenticates with correct email/password

#### Test Steps
```bash
# 1. Create a test user first (implementation detail)
# 2. Login with valid credentials
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

#### Expected Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Success Criteria
- ✅ Returns 200 HTTP status
- ✅ Provides both access and refresh tokens
- ✅ Tokens are valid JWT format
- ✅ Response time < 500ms

### Story 2: Token Verification by Other Services
**Scenario**: Another microservice validates user authentication

#### Test Steps
```bash
# Use access token from Story 1
export ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8001/auth/verify
```

#### Expected Response
```json
{
  "valid": true,
  "user_id": 123,
  "email": "test@example.com"
}
```

#### Success Criteria
- ✅ Returns 200 HTTP status
- ✅ Confirms token validity
- ✅ Provides user information
- ✅ Response time < 100ms

### Story 3: Token Refresh
**Scenario**: User refreshes expired access token

#### Test Steps
```bash
# Use refresh token from Story 1
export REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

#### Expected Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Success Criteria
- ✅ Returns 200 HTTP status
- ✅ Provides new access token
- ✅ New token is different from original
- ✅ Original access token still works until expiry

### Story 4: User Logout
**Scenario**: User safely logs out and invalidates tokens

#### Test Steps
```bash
# Use refresh token from Story 1
curl -X POST http://localhost:8001/auth/logout \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

#### Expected Response
```json
{
  "message": "Successfully logged out"
}
```

#### Verification: Test Token Invalidation
```bash
# Try to use the refresh token again - should fail
curl -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

#### Success Criteria
- ✅ Logout returns 200 HTTP status
- ✅ Subsequent refresh attempts return 401
- ✅ Access token still works until natural expiry
- ✅ Blacklisted tokens are remembered

### Story 5: Rate Limiting Protection
**Scenario**: System blocks brute force login attempts

#### Test Steps
```bash
# Make 6 failed login attempts rapidly
for i in {1..6}; do
  curl -X POST http://localhost:8001/auth/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "WrongPassword"
    }'
  echo "Attempt $i"
done
```

#### Expected Behavior
- Attempts 1-5: Return 401 with "Invalid email or password"
- Attempt 6: Return 429 with "Too many login attempts"

#### Success Criteria
- ✅ First 5 attempts return 401
- ✅ 6th attempt returns 429
- ✅ Account lockout lasts 15 minutes
- ✅ Rate limiting per email/IP

### Story 6: Input Validation
**Scenario**: API handles malformed requests gracefully

#### Test Steps
```bash
# Test missing fields
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Test invalid email format
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "password": "SecurePass123"
  }'
```

#### Expected Responses
- Missing password: 422 with validation error
- Invalid email: 422 with format error

#### Success Criteria
- ✅ Returns 422 for validation errors
- ✅ Provides clear error messages
- ✅ Rejects malformed JSON
- ✅ Handles missing required fields

## Integration Test Scenarios

### End-to-End Authentication Flow
```bash
#!/bin/bash
echo "Testing complete authentication flow..."

# 1. Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123"}')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token')

# 2. Verify token
VERIFY_RESPONSE=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8001/auth/verify)

# 3. Refresh token
NEW_TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

NEW_ACCESS_TOKEN=$(echo $NEW_TOKEN_RESPONSE | jq -r '.access_token')

# 4. Verify new token
NEW_VERIFY_RESPONSE=$(curl -s -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  http://localhost:8001/auth/verify)

# 5. Logout
LOGOUT_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/logout \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

echo "All tests completed. Check responses manually."
```

## Performance Validation

### Load Testing (Optional)
```bash
# Install apache bench
sudo apt-get install apache2-utils

# Test login endpoint
ab -n 100 -c 10 -p login_data.json -T 'application/json' \
  http://localhost:8001/auth/login

# Test verify endpoint
ab -n 1000 -c 50 -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8001/auth/verify
```

### Expected Performance
- Login: < 500ms p95 (bcrypt overhead)
- Verify: < 100ms p95 (JWT validation)
- Health: < 50ms p95 (simple check)
- Refresh: < 200ms p95 (JWT generation)

## Troubleshooting

### Common Issues
1. **503 on /health**: Database connection failed
2. **500 on /login**: Check bcrypt installation
3. **401 on valid credentials**: Verify user exists in database
4. **Token validation errors**: Check JWT secret configuration

### Debug Commands
```bash
# Check database connection
sqlite3 auth.db ".tables"

# View application logs
tail -f app.log

# Decode JWT token (debugging only)
echo $ACCESS_TOKEN | cut -d. -f2 | base64 -d | jq
```

## Cleanup
```bash
# Stop service
pkill -f uvicorn

# Remove test database
rm -f auth.db

# Clear any test data
rm -f *.log
```

This quickstart validates all functional requirements from the feature specification and provides a foundation for automated testing.