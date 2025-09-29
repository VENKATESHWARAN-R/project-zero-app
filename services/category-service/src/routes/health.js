const express = require('express');
const axios = require('axios');
const { sequelize } = require('../models');

const router = express.Router();

/**
 * @swagger
 * /health:
 *   get:
 *     summary: Health check endpoint
 *     description: Returns service health status
 *     tags:
 *       - Health
 *     responses:
 *       '200':
 *         description: Service is healthy
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: "healthy"
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 *                 version:
 *                   type: string
 *                   example: "1.0.0"
 *                 uptime:
 *                   type: number
 *                   example: 3600
 */
router.get('/health', async (req, res) => {
  try {
    const uptime = process.uptime();
    const timestamp = new Date().toISOString();
    const version = process.env.npm_package_version || '1.0.0';

    res.json({
      status: 'healthy',
      timestamp,
      version,
      uptime,
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
    });
  }
});

// Readiness check with dependencies
router.get('/health/ready', async (req, res) => {
  try {
    const timestamp = new Date().toISOString();
    const dependencies = {};

    // Check database connection
    try {
      const start = Date.now();
      await sequelize.authenticate();
      const responseTime = Date.now() - start;

      dependencies.database = {
        status: 'connected',
        response_time: responseTime,
      };
    } catch (dbError) {
      dependencies.database = {
        status: 'disconnected',
        error: dbError.message,
      };
    }

    // Check auth service
    try {
      const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:8001';
      const start = Date.now();
      await axios.get(`${authServiceUrl}/health`, { timeout: 5000 });
      const responseTime = Date.now() - start;

      dependencies.auth_service = {
        status: 'available',
        response_time: responseTime,
      };
    } catch (authError) {
      dependencies.auth_service = {
        status: 'unavailable',
        error: authError.message,
      };
    }

    // Determine overall status
    const allHealthy = Object.values(dependencies).every(
      dep => dep.status === 'connected' || dep.status === 'available'
    );

    if (allHealthy) {
      res.json({
        status: 'ready',
        timestamp,
        dependencies,
      });
    } else {
      res.status(503).json({
        status: 'not_ready',
        timestamp,
        dependencies,
      });
    }
  } catch (error) {
    res.status(503).json({
      status: 'not_ready',
      timestamp: new Date().toISOString(),
      error: error.message,
    });
  }
});

module.exports = router;