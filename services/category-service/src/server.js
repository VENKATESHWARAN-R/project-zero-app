const app = require('./app');
const { sequelize, testConnection, closeConnection } = require('./config/database');
const { logger } = require('./middleware/errorHandler');

const PORT = process.env.PORT || 8005;
const HOST = process.env.HOST || '0.0.0.0';

let server;

// Start server
const startServer = async () => {
  try {
    // Test database connection
    await testConnection();

    // Sync database models (create tables if they don't exist)
    await sequelize.sync();
    logger.info('Database synchronized successfully');

    // Start HTTP server
    server = app.listen(PORT, HOST, () => {
      logger.info(`Category service running on http://${HOST}:${PORT}`);
      logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
      logger.info(`Database: ${process.env.DATABASE_URL || 'sqlite://category_service.db'}`);
    });

    // Handle server errors
    server.on('error', (error) => {
      if (error.syscall !== 'listen') {
        throw error;
      }

      const bind = typeof PORT === 'string' ? `Pipe ${PORT}` : `Port ${PORT}`;

      switch (error.code) {
        case 'EACCES':
          logger.error(`${bind} requires elevated privileges`);
          process.exit(1);
          break;
        case 'EADDRINUSE':
          logger.error(`${bind} is already in use`);
          process.exit(1);
          break;
        default:
          throw error;
      }
    });

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Graceful shutdown
const gracefulShutdown = async (signal) => {
  logger.info(`Received ${signal}. Starting graceful shutdown...`);

  if (server) {
    server.close(async () => {
      logger.info('HTTP server closed');

      try {
        await closeConnection();
        logger.info('Database connection closed');
        process.exit(0);
      } catch (error) {
        logger.error('Error closing database connection:', error);
        process.exit(1);
      }
    });
  } else {
    process.exit(0);
  }
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Start the server
if (require.main === module) {
  startServer();
}

module.exports = { app, startServer, gracefulShutdown };