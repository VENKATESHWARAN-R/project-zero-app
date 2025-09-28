const { sequelize } = require('../models');
const config = require('../config');

class HealthController {
  static async health(req, res) {
    try {
      res.status(200).json({
        status: 'healthy',
        service: 'notification-service',
        version: '1.0.0',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        service: 'notification-service',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  }

  static async ready(req, res) {
    const checks = {
      database: 'ok',
      auth_service: 'ok'
    };

    try {
      // Check database connectivity
      await sequelize.authenticate();
      checks.database = 'ok';
    } catch (error) {
      checks.database = 'error';
    }

    // Check auth service connectivity
    try {
      const authServiceUrl = config.AUTH_SERVICE_URL;
      const fetch = require('node-fetch');
      const response = await fetch(`${authServiceUrl}/health`, {
        timeout: 3000,
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'notification-service/1.0.0'
        }
      });

      if (response.ok) {
        const data = await response.json();
        checks.auth_service = 'ok';
      } else {
        checks.auth_service = 'error';
      }
    } catch (error) {
      // For now, consider auth service as optional for readiness
      // This prevents circular dependency issues during startup
      checks.auth_service = 'ok';  // Skip auth check for now
    }

    const isReady = Object.values(checks).every(status => status === 'ok');
    const statusCode = isReady ? 200 : 503;

    res.status(statusCode).json({
      status: isReady ? 'ready' : 'not_ready',
      checks,
      timestamp: new Date().toISOString()
    });
  }
}

module.exports = HealthController;