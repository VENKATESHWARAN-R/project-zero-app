const axios = require('axios');

// JWT authentication middleware
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        error: {
          code: 'MISSING_TOKEN',
          message: 'Authentication token required',
        },
        timestamp: new Date().toISOString(),
        request_id: req.id,
      });
    }

    // Verify token with auth service
    const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:8001';

    try {
      const response = await axios.get(`${authServiceUrl}/auth/verify`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        timeout: 5000,
      });

      // Attach user info to request
      req.user = response.data.user;
      req.token = token;
      next();
    } catch (authError) {
      if (authError.response && authError.response.status === 401) {
        return res.status(401).json({
          error: {
            code: 'INVALID_TOKEN',
            message: 'Invalid or expired authentication token',
          },
          timestamp: new Date().toISOString(),
          request_id: req.id,
        });
      }

      // Auth service unavailable
      return res.status(503).json({
        error: {
          code: 'AUTH_SERVICE_UNAVAILABLE',
          message: 'Authentication service is currently unavailable',
          details: {
            service: 'auth-service',
            retry_after: '30s',
          },
        },
        timestamp: new Date().toISOString(),
        request_id: req.id,
      });
    }
  } catch (error) {
    console.error('Authentication middleware error:', error);
    return res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Internal authentication error',
      },
      timestamp: new Date().toISOString(),
      request_id: req.id,
    });
  }
};

// Optional authentication middleware (doesn't fail if no token)
const optionalAuth = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return next(); // Continue without authentication
  }

  try {
    const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:8001';
    const response = await axios.get(`${authServiceUrl}/auth/verify`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      timeout: 5000,
    });

    req.user = response.data.user;
    req.token = token;
  } catch (error) {
    // Ignore auth errors for optional auth
    console.warn('Optional auth failed:', error.message);
  }

  next();
};

module.exports = {
  authenticateToken,
  optionalAuth,
};