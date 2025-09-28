const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');

const routes = require('./routes');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');
const correlationIdMiddleware = require('./middleware/correlationId');
const securityMiddleware = require('./middleware/security');
const logger = require('./utils/logger');
const config = require('./config');

const app = express();

// Trust proxy for rate limiting and IP detection
app.set('trust proxy', 1);

// Security middleware
app.use(securityMiddleware.helmet);
app.use(securityMiddleware.cors);
app.use(correlationIdMiddleware);

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'rate_limit_exceeded',
    message: 'Too many requests from this IP, please try again later.',
    timestamp: new Date().toISOString()
  },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.logRequest(req, res, duration);
  });

  next();
});

// Swagger documentation
try {
  const swaggerPath = path.join(__dirname, '../swagger.json');
  if (fs.existsSync(swaggerPath)) {
    const swaggerDocument = JSON.parse(fs.readFileSync(swaggerPath, 'utf8'));
    app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
    logger.info('Swagger documentation available at /docs');
  }
} catch (error) {
  logger.logError(error, null, { component: 'swagger-setup' });
}

// API routes
app.use('/', routes);

// Health check endpoint (redundant but helpful at root)
app.get('/', (req, res) => {
  res.json({
    service: 'notification-service',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString(),
    docs: '/docs',
    health: '/health'
  });
});

// 404 handler for unmatched routes
app.use(notFoundHandler);

// Global error handler
app.use(errorHandler);

// Graceful shutdown handling
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.logError(new Error('Unhandled Promise Rejection'), null, { reason, promise });
  process.exit(1);
});

// Uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.logError(error, null, { type: 'uncaughtException' });
  process.exit(1);
});

module.exports = app;