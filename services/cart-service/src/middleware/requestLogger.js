// Using crypto.randomUUID() as a built-in alternative to avoid UUID import issues
const crypto = require('crypto');
const logger = require('../services/logger');

const requestLogger = (req, res, next) => {
  // Generate correlation ID for request tracing using built-in crypto
  const generateUUID = () => {
    return crypto.randomUUID();
  };
  
  req.correlationId = req.headers['x-correlation-id'] || generateUUID();

  // Set correlation ID in response headers
  res.setHeader('X-Correlation-ID', req.correlationId);

  const startTime = Date.now();

  // Log request start
  logger.info('HTTP request started', {
    correlationId: req.correlationId,
    method: req.method,
    url: req.url,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
    contentLength: req.get('Content-Length'),
  });

  // Override res.end to capture response details
  const originalEnd = res.end;
  res.end = function (...args) {
    const responseTime = Date.now() - startTime;

    // Log request completion
    logger.request(req, res, responseTime);

    // Call original end method
    originalEnd.apply(this, args);
  };

  next();
};

module.exports = requestLogger;
