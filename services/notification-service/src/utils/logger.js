const winston = require('winston');
const config = require('../config');

const logger = winston.createLogger({
  level: config.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'notification-service',
    version: '1.0.0'
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// Create logs directory if it doesn't exist
const fs = require('fs');
const path = require('path');
const logsDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Add request logging helper
logger.logRequest = (req, res, responseTime) => {
  const logData = {
    method: req.method,
    url: req.url,
    statusCode: res.statusCode,
    responseTime: `${responseTime}ms`,
    userAgent: req.headers['user-agent'],
    ip: req.ip || req.connection.remoteAddress,
    correlationId: req.correlationId
  };

  if (req.user) {
    logData.userId = req.user.userId;
  }

  logger.info('HTTP Request', logData);
};

// Add error logging helper
logger.logError = (error, req = null, context = {}) => {
  const logData = {
    error: {
      message: error.message,
      stack: error.stack,
      name: error.name
    },
    context
  };

  if (req) {
    logData.request = {
      method: req.method,
      url: req.url,
      correlationId: req.correlationId,
      userId: req.user?.userId
    };
  }

  logger.error('Application Error', logData);
};

// Add notification logging helper
logger.logNotification = (action, notificationId, userId, details = {}) => {
  logger.info('Notification Event', {
    action,
    notificationId,
    userId,
    ...details
  });
};

module.exports = logger;