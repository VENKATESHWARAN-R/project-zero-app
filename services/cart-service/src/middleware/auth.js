const authService = require('../services/authService');
const logger = require('../services/logger');

const authMiddleware = async (req, res, next) => {
  const startTime = Date.now();

  try {
    const authHeader = req.headers.authorization;
    const token = authService.extractTokenFromHeader(authHeader);

    if (!token) {
      logger.authEvent('token_missing', null, false, {
        correlationId: req.correlationId,
        ip: req.ip,
      });

      return res.status(401).json({
        error: 'Unauthorized - missing or invalid authorization header',
        timestamp: new Date().toISOString(),
        correlation_id: req.correlationId,
      });
    }

    const verificationResult = await authService.verifyToken(token);

    if (!verificationResult.valid) {
      logger.authEvent('token_invalid', null, false, {
        correlationId: req.correlationId,
        error: verificationResult.error,
        ip: req.ip,
      });

      return res.status(401).json({
        error: 'Unauthorized - invalid token',
        timestamp: new Date().toISOString(),
        correlation_id: req.correlationId,
      });
    }

    // Attach user info to request
    req.user = {
      id: verificationResult.user_id,
      email: verificationResult.email,
    };

    const responseTime = Date.now() - startTime;
    logger.authEvent('token_verified', verificationResult.user_id, true, {
      correlationId: req.correlationId,
      responseTime: `${responseTime}ms`,
    });

    next();
  } catch (error) {
    const responseTime = Date.now() - startTime;

    if (error.message.includes('unavailable')) {
      logger.error('Auth service unavailable', error, {
        correlationId: req.correlationId,
        responseTime: `${responseTime}ms`,
      });

      return res.status(503).json({
        error: 'Authentication service unavailable',
        timestamp: new Date().toISOString(),
        correlation_id: req.correlationId,
      });
    }

    logger.error('Authentication middleware error', error, {
      correlationId: req.correlationId,
      responseTime: `${responseTime}ms`,
    });

    return res.status(500).json({
      error: 'Internal server error during authentication',
      timestamp: new Date().toISOString(),
      correlation_id: req.correlationId,
    });
  }
};

module.exports = authMiddleware;
