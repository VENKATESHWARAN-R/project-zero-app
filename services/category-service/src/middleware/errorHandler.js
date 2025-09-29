const winston = require('winston');

// Configure logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
    }),
  ],
});

// Error handler middleware
const errorHandler = (err, req, res, next) => {
  // Log the error
  logger.error('Error occurred:', {
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    requestId: req.id,
  });

  // Default error response
  let statusCode = 500;
  let errorCode = 'INTERNAL_ERROR';
  let message = 'An internal server error occurred';
  let details = {};

  // Handle specific error types
  if (err.name === 'SequelizeValidationError') {
    statusCode = 400;
    errorCode = 'VALIDATION_ERROR';
    message = 'Database validation failed';
    details = {
      fields: err.errors.map(e => ({
        field: e.path,
        message: e.message,
        value: e.value,
      })),
    };
  } else if (err.name === 'SequelizeUniqueConstraintError') {
    statusCode = 409;
    errorCode = 'DUPLICATE_ENTRY';
    message = 'Duplicate entry violates unique constraint';
    details = {
      fields: err.errors.map(e => ({
        field: e.path,
        message: e.message,
      })),
    };
  } else if (err.name === 'SequelizeForeignKeyConstraintError') {
    statusCode = 400;
    errorCode = 'FOREIGN_KEY_CONSTRAINT';
    message = 'Foreign key constraint violation';
    details = {
      constraint: err.constraint,
      table: err.table,
    };
  } else if (err.message && err.message.includes('not found')) {
    statusCode = 404;
    errorCode = 'NOT_FOUND';
    message = err.message;
  } else if (err.message && err.message.includes('circular hierarchy')) {
    statusCode = 400;
    errorCode = 'CIRCULAR_HIERARCHY';
    message = err.message;
    details = {
      field: 'parent_id',
      reason: 'Category cannot be moved to become its own descendant',
    };
  } else if (err.message && err.message.includes('Maximum hierarchy depth')) {
    statusCode = 400;
    errorCode = 'MAX_DEPTH_EXCEEDED';
    message = err.message;
    details = {
      field: 'parent_id',
      max_depth: 5,
    };
  } else if (err.message && err.message.includes('active children')) {
    statusCode = 400;
    errorCode = 'HAS_CHILDREN';
    message = err.message;
    details = {
      reason: 'Category has active children and cannot be deleted',
    };
  } else if (err.statusCode || err.status) {
    statusCode = err.statusCode || err.status;
    message = err.message || message;
    errorCode = err.code || errorCode;
  }

  // Don't expose internal errors in production
  if (process.env.NODE_ENV === 'production' && statusCode === 500) {
    message = 'An internal server error occurred';
    details = {};
  }

  res.status(statusCode).json({
    error: {
      code: errorCode,
      message,
      details,
    },
    timestamp: new Date().toISOString(),
    request_id: req.id,
  });
};

// 404 handler
const notFoundHandler = (req, res, next) => {
  res.status(404).json({
    error: {
      code: 'ENDPOINT_NOT_FOUND',
      message: `Endpoint ${req.method} ${req.path} not found`,
    },
    timestamp: new Date().toISOString(),
    request_id: req.id,
  });
};

module.exports = {
  errorHandler,
  notFoundHandler,
  logger,
};