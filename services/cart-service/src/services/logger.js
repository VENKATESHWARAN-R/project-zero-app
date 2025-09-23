const winston = require('winston');

// Define log levels
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
};

// Create custom format
const logFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(
    ({ timestamp, level, message, correlationId, userId, ...meta }) => {
      return JSON.stringify({
        timestamp,
        level,
        message,
        correlationId: correlationId || 'unknown',
        userId: userId || 'anonymous',
        ...meta,
      });
    }
  )
);

// Create logger instance
const logger = winston.createLogger({
  levels: logLevels,
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(
          ({ timestamp, level, message, correlationId, userId, ...meta }) => {
            const metaStr = Object.keys(meta).length
              ? JSON.stringify(meta)
              : '';
            return `${timestamp} [${level}] ${message} [${correlationId}] [${userId}] ${metaStr}`;
          }
        )
      ),
    }),
  ],
});

// Add file transport for production
if (process.env.NODE_ENV === 'production') {
  logger.add(
    new winston.transports.File({
      filename: 'logs/cart-service-error.log',
      level: 'error',
      format: logFormat,
    })
  );

  logger.add(
    new winston.transports.File({
      filename: 'logs/cart-service.log',
      format: logFormat,
    })
  );
}

// Helper methods for structured logging
class Logger {
  static info(message, meta = {}) {
    logger.info(message, meta);
  }

  static error(message, error = null, meta = {}) {
    const errorMeta = error
      ? {
          error: error.message,
          stack: error.stack,
          ...meta,
        }
      : meta;

    logger.error(message, errorMeta);
  }

  static warn(message, meta = {}) {
    logger.warn(message, meta);
  }

  static debug(message, meta = {}) {
    logger.debug(message, meta);
  }

  static request(req, res, responseTime) {
    const meta = {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      responseTime: `${responseTime}ms`,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      correlationId: req.correlationId,
      userId: req.user?.id,
    };

    if (res.statusCode >= 400) {
      this.warn('HTTP request failed', meta);
    } else {
      this.info('HTTP request completed', meta);
    }
  }

  static cartOperation(operation, userId, cartId, meta = {}) {
    this.info(`Cart operation: ${operation}`, {
      operation,
      userId,
      cartId,
      ...meta,
    });
  }

  static serviceCall(service, operation, success, responseTime, meta = {}) {
    const logLevel = success ? 'info' : 'warn';
    const message = `${service} service call: ${operation} ${success ? 'succeeded' : 'failed'}`;

    logger[logLevel](message, {
      service,
      operation,
      success,
      responseTime: `${responseTime}ms`,
      ...meta,
    });
  }

  static authEvent(event, userId, success, meta = {}) {
    const logLevel = success ? 'info' : 'warn';
    const message = `Auth event: ${event} ${success ? 'succeeded' : 'failed'}`;

    logger[logLevel](message, {
      event,
      userId,
      success,
      ...meta,
    });
  }
}

module.exports = Logger;
