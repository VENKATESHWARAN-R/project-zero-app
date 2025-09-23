// Mock auth service for testing
const mockAuthService = {
  responses: new Map(),

  // Configure mock responses
  setMockResponse: (token, response) => {
    mockAuthService.responses.set(token, response);
  },

  // Clear all mock responses
  clearMocks: () => {
    mockAuthService.responses.clear();
  },

  // Mock implementation
  async verifyToken(token) {
    if (mockAuthService.responses.has(token)) {
      return mockAuthService.responses.get(token);
    }

    // Default responses for known test tokens
    const defaultResponses = {
      'Bearer mock-jwt-token': { valid: true, user_id: 'user-123', email: 'test@example.com' },
      'Bearer mock-valid-jwt-token': { valid: true, user_id: 'user-456', email: 'valid@example.com' },
      'Bearer valid-jwt-token-from-auth-service': { valid: true, user_id: 'user-789', email: 'auth@example.com' },
      'Bearer valid-user-token': { valid: true, user_id: 'user-999', email: 'user@example.com' },
      'Bearer consistent-user-token': { valid: true, user_id: 'user-consistent', email: 'consistent@example.com' },
      'Bearer user-lifecycle-token': { valid: true, user_id: 'user-lifecycle', email: 'lifecycle@example.com' },
      'Bearer expired-cart-user-token': { valid: true, user_id: 'user-expired', email: 'expired@example.com' },
      'Bearer cart-limits-token': { valid: true, user_id: 'user-limits', email: 'limits@example.com' },
      'Bearer concurrent-ops-token': { valid: true, user_id: 'user-concurrent', email: 'concurrent@example.com' },
      'Bearer timestamp-test-token': { valid: true, user_id: 'user-timestamp', email: 'timestamp@example.com' },
      'Bearer invalid-token': { valid: false, error: 'Invalid token' },
      'Bearer expired-token': { valid: false, error: 'Token expired' },
      'Bearer malformed.token.here': { valid: false, error: 'Malformed token' },
    };

    if (defaultResponses[token]) {
      return defaultResponses[token];
    }

    // Default invalid response
    return { valid: false, error: 'Unknown token' };
  },

  async checkHealth() {
    return true;
  },

  extractTokenFromHeader(authHeader) {
    if (!authHeader) {
      return null;
    }

    if (authHeader.startsWith('Bearer ')) {
      return authHeader;
    }

    return null;
  },
};

module.exports = mockAuthService;