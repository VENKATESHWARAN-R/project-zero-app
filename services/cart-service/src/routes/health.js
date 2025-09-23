const express = require('express');
const { sequelize } = require('../models');
const authService = require('../services/authService');
const productService = require('../services/productService');
const logger = require('../services/logger');

const router = express.Router();

// GET /health - Health check endpoint
router.get('/', async (req, res) => {
  try {
    // Test database connection
    await sequelize.authenticate();

    const healthResponse = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: 'connected',
    };

    res.json(healthResponse);
  } catch (error) {
    logger.error('Health check failed', error, {
      correlationId: req.correlationId,
    });

    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      database: 'disconnected',
      error: 'Database connection failed',
    });
  }
});

// GET /health/ready - Readiness check endpoint
router.get('/ready', async (req, res) => {
  const checks = {
    database: false,
    auth_service: false,
    product_service: false,
  };

  try {
    // Check database
    await sequelize.authenticate();
    checks.database = true;
  } catch (error) {
    logger.warn('Database check failed', { correlationId: req.correlationId });
  }

  try {
    // Check auth service
    checks.auth_service = await authService.checkHealth();
  } catch (error) {
    logger.warn('Auth service check failed', {
      correlationId: req.correlationId,
    });
  }

  try {
    // Check product service
    checks.product_service = await productService.checkHealth();
  } catch (error) {
    logger.warn('Product service check failed', {
      correlationId: req.correlationId,
    });
  }

  const allHealthy = Object.values(checks).every((check) => check === true);
  const status = allHealthy ? 'ready' : 'not ready';
  const statusCode = allHealthy ? 200 : 503;

  res.status(statusCode).json({
    status,
    checks,
  });
});

module.exports = router;
