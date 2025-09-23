const logger = require('../services/logger');

const errorHandler = (error, req, res, next) => {
  // Set default error properties
  let statusCode = 500;
  let errorMessage = 'Internal server error';
  let errorDetails = null;

  // Handle specific error types
  if (error.message) {
    if (error.message.includes('Product not found')) {
      statusCode = 404;
      errorMessage = 'Product not found';
    } else if (error.message.includes('not available')) {
      statusCode = 422;
      errorMessage = 'Product is not available for purchase';
    } else if (
      error.message.includes('exceed') ||
      error.message.includes('limit')
    ) {
      statusCode = 422;
      errorMessage = error.message;
    } else if (error.message.includes('not found in cart')) {
      statusCode = 404;
      errorMessage = 'Item not found in cart';
    } else if (error.message.includes('Quantity must be')) {
      statusCode = 400;
      errorMessage = error.message;
    } else if (error.message.includes('service unavailable')) {
      statusCode = 503;
      errorMessage = 'External service unavailable';
    } else if (error.name === 'SequelizeValidationError') {
      statusCode = 400;
      errorMessage = 'Data validation failed';
      errorDetails = error.errors?.map((err) => ({
        field: err.path,
        message: err.message,
      }));
    } else if (error.name === 'SequelizeUniqueConstraintError') {
      statusCode = 409;
      errorMessage = 'Resource already exists';
    } else if (error.name === 'SequelizeForeignKeyConstraintError') {
      statusCode = 400;
      errorMessage = 'Invalid reference';
    }
  }

  // Log the error
  logger.error('Request error', error, {
    correlationId: req.correlationId,
    userId: req.user?.id,
    method: req.method,
    url: req.url,
    statusCode,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
  });

  // Prepare error response
  const errorResponse = {
    error: errorMessage,
    timestamp: new Date().toISOString(),
    correlation_id: req.correlationId,
  };

  if (errorDetails) {
    errorResponse.details = errorDetails;
  }

  // Don't expose internal errors in production
  if (process.env.NODE_ENV === 'production' && statusCode === 500) {
    errorResponse.error = 'Internal server error';
  }

  res.status(statusCode).json(errorResponse);
};

module.exports = errorHandler;
