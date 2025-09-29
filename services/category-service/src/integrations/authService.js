const { createServiceClient } = require('../utils/httpClient');

class AuthService {
  constructor() {
    const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:8001';

    this.client = createServiceClient('auth-service', authServiceUrl, {
      timeout: 5000,
      retries: 2
    });

    this.cache = new Map();
    this.cacheTimeout = 300000; // 5 minutes
  }

  // Verify JWT token with auth service
  async verifyToken(token) {
    try {
      // Check cache first
      const cacheKey = `token:${token}`;
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }

      const response = await this.client.get('/auth/verify', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const tokenData = {
        valid: true,
        user: response.data.user,
        expiresAt: response.data.expires_at
      };

      // Cache the result
      this.cache.set(cacheKey, {
        data: tokenData,
        timestamp: Date.now()
      });

      return tokenData;
    } catch (error) {
      if (error.response && error.response.status === 401) {
        return {
          valid: false,
          error: 'Invalid or expired token'
        };
      }

      throw new AuthServiceError(
        `Token verification failed: ${error.message}`,
        error.response?.status || 500,
        'TOKEN_VERIFICATION_FAILED'
      );
    }
  }

  // Check if user has admin privileges
  async isAdmin(token) {
    try {
      const tokenData = await this.verifyToken(token);

      if (!tokenData.valid) {
        return false;
      }

      const user = tokenData.user;
      return user.is_admin === true || user.role === 'admin';
    } catch (error) {
      console.error('Admin check failed:', error.message);
      return false;
    }
  }

  // Get user information from token
  async getUserInfo(token) {
    try {
      const tokenData = await this.verifyToken(token);

      if (!tokenData.valid) {
        throw new AuthServiceError('Invalid token', 401, 'INVALID_TOKEN');
      }

      return tokenData.user;
    } catch (error) {
      if (error instanceof AuthServiceError) {
        throw error;
      }

      throw new AuthServiceError(
        `Failed to get user info: ${error.message}`,
        500,
        'USER_INFO_FAILED'
      );
    }
  }

  // Refresh token
  async refreshToken(refreshToken) {
    try {
      const response = await this.client.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        expires_in: response.data.expires_in
      };
    } catch (error) {
      if (error.response && error.response.status === 401) {
        throw new AuthServiceError('Invalid refresh token', 401, 'INVALID_REFRESH_TOKEN');
      }

      throw new AuthServiceError(
        `Token refresh failed: ${error.message}`,
        error.response?.status || 500,
        'TOKEN_REFRESH_FAILED'
      );
    }
  }

  // Logout and invalidate token
  async logout(refreshToken) {
    try {
      await this.client.post('/auth/logout', {
        refresh_token: refreshToken
      });

      // Clear cache for this refresh token
      this.clearTokenCache();

      return { success: true };
    } catch (error) {
      console.error('Logout failed:', error.message);
      // Don't throw error for logout failures
      return { success: false, error: error.message };
    }
  }

  // Health check for auth service
  async checkHealth() {
    try {
      return await this.client.checkHealth();
    } catch (error) {
      return {
        status: 'unhealthy',
        service: 'auth-service',
        error: error.message
      };
    }
  }

  // Get service status including circuit breaker
  getServiceStatus() {
    const circuitStatus = this.client.getCircuitStatus();

    return {
      serviceName: 'auth-service',
      baseURL: this.client.baseURL,
      circuit: circuitStatus,
      cache: {
        size: this.cache.size,
        timeout: this.cacheTimeout
      }
    };
  }

  // Clear token cache (useful for logout or security events)
  clearTokenCache() {
    this.cache.clear();
  }

  // Clear expired cache entries
  clearExpiredCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp >= this.cacheTimeout) {
        this.cache.delete(key);
      }
    }
  }

  // Validate token format (basic check before service call)
  isValidTokenFormat(token) {
    if (!token || typeof token !== 'string') {
      return false;
    }

    // Basic JWT format check (3 parts separated by dots)
    const parts = token.split('.');
    return parts.length === 3;
  }

  // Extract token from Authorization header
  extractTokenFromHeader(authHeader) {
    if (!authHeader || typeof authHeader !== 'string') {
      return null;
    }

    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0] !== 'Bearer') {
      return null;
    }

    return parts[1];
  }

  // Middleware factory for token verification
  createAuthMiddleware(options = {}) {
    const { required = true, adminRequired = false } = options;

    return async (req, res, next) => {
      try {
        const authHeader = req.headers.authorization;
        const token = this.extractTokenFromHeader(authHeader);

        if (!token) {
          if (required) {
            return res.status(401).json({
              error: {
                code: 'MISSING_TOKEN',
                message: 'Authentication token required'
              },
              timestamp: new Date().toISOString(),
              request_id: req.id
            });
          }
          return next();
        }

        if (!this.isValidTokenFormat(token)) {
          return res.status(401).json({
            error: {
              code: 'INVALID_TOKEN_FORMAT',
              message: 'Invalid token format'
            },
            timestamp: new Date().toISOString(),
            request_id: req.id
          });
        }

        const tokenData = await this.verifyToken(token);

        if (!tokenData.valid) {
          return res.status(401).json({
            error: {
              code: 'INVALID_TOKEN',
              message: tokenData.error || 'Invalid or expired token'
            },
            timestamp: new Date().toISOString(),
            request_id: req.id
          });
        }

        // Check admin requirement
        if (adminRequired) {
          const isAdmin = await this.isAdmin(token);
          if (!isAdmin) {
            return res.status(403).json({
              error: {
                code: 'ADMIN_REQUIRED',
                message: 'Admin privileges required'
              },
              timestamp: new Date().toISOString(),
              request_id: req.id
            });
          }
        }

        // Attach user info to request
        req.user = tokenData.user;
        req.token = token;
        next();
      } catch (error) {
        console.error('Auth middleware error:', error);

        if (error instanceof AuthServiceError) {
          return res.status(error.statusCode).json({
            error: {
              code: error.code,
              message: error.message
            },
            timestamp: new Date().toISOString(),
            request_id: req.id
          });
        }

        return res.status(503).json({
          error: {
            code: 'AUTH_SERVICE_UNAVAILABLE',
            message: 'Authentication service is currently unavailable'
          },
          timestamp: new Date().toISOString(),
          request_id: req.id
        });
      }
    };
  }

  // Start cache cleanup interval
  startCacheCleanup(intervalMs = 300000) { // 5 minutes
    setInterval(() => {
      this.clearExpiredCache();
    }, intervalMs);
  }
}

// Custom error class for auth service errors
class AuthServiceError extends Error {
  constructor(message, statusCode = 500, code = 'AUTH_ERROR') {
    super(message);
    this.name = 'AuthServiceError';
    this.statusCode = statusCode;
    this.code = code;
  }
}

// Singleton instance
let authServiceInstance = null;

function getAuthService() {
  if (!authServiceInstance) {
    authServiceInstance = new AuthService();
    authServiceInstance.startCacheCleanup();
  }
  return authServiceInstance;
}

module.exports = {
  AuthService,
  AuthServiceError,
  getAuthService
};