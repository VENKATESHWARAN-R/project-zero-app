const { v4: uuidv4 } = require('uuid');

const correlationIdMiddleware = (req, res, next) => {
  // Get correlation ID from header or generate new one
  const correlationId = req.headers['x-correlation-id'] || uuidv4();

  // Add correlation ID to request object
  req.correlationId = correlationId;

  // Add correlation ID to response headers
  res.set('X-Correlation-ID', correlationId);

  // Add correlation ID to logs context (if using structured logging)
  req.logContext = {
    correlationId,
    method: req.method,
    path: req.path,
    userAgent: req.headers['user-agent'],
    ip: req.ip || req.connection.remoteAddress
  };

  next();
};

module.exports = correlationIdMiddleware;