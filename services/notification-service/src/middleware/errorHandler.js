const errorHandler = (err, req, res, next) => {
  console.error('Error caught by error handler:', err);

  // Default error response
  let error = {
    error: 'internal_error',
    message: 'An unexpected error occurred',
    timestamp: new Date().toISOString(),
    path: req.path
  };

  // Handle Sequelize validation errors
  if (err.name === 'SequelizeValidationError') {
    error = {
      error: 'validation_error',
      message: 'Database validation failed',
      errors: err.errors.map(e => ({
        field: e.path,
        message: e.message,
        value: e.value
      })),
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(422).json(error);
  }

  // Handle Sequelize unique constraint errors
  if (err.name === 'SequelizeUniqueConstraintError') {
    error = {
      error: 'validation_error',
      message: 'Duplicate value for unique field',
      errors: err.errors.map(e => ({
        field: e.path,
        message: `${e.path} must be unique`,
        value: e.value
      })),
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(422).json(error);
  }

  // Handle Sequelize foreign key constraint errors
  if (err.name === 'SequelizeForeignKeyConstraintError') {
    error = {
      error: 'validation_error',
      message: 'Invalid reference to related resource',
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(400).json(error);
  }

  // Handle Sequelize database connection errors
  if (err.name === 'SequelizeConnectionError' || err.name === 'SequelizeConnectionRefusedError') {
    error = {
      error: 'service_unavailable',
      message: 'Database connection failed',
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(503).json(error);
  }

  // Handle JWT errors
  if (err.name === 'JsonWebTokenError') {
    error = {
      error: 'unauthorized',
      message: 'Invalid token',
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(401).json(error);
  }

  if (err.name === 'TokenExpiredError') {
    error = {
      error: 'unauthorized',
      message: 'Token expired',
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(401).json(error);
  }

  // Handle syntax errors (malformed JSON)
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    error = {
      error: 'bad_request',
      message: 'Invalid JSON in request body',
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(400).json(error);
  }

  // Handle custom errors with status codes
  if (err.statusCode) {
    error = {
      error: err.code || 'custom_error',
      message: err.message || 'Custom error occurred',
      timestamp: new Date().toISOString(),
      path: req.path
    };
    return res.status(err.statusCode).json(error);
  }

  // For all other errors, return 500
  res.status(500).json(error);
};

// 404 handler for unmatched routes
const notFoundHandler = (req, res) => {
  res.status(404).json({
    error: 'not_found',
    message: `Route ${req.method} ${req.path} not found`,
    timestamp: new Date().toISOString(),
    path: req.path
  });
};

module.exports = {
  errorHandler,
  notFoundHandler
};