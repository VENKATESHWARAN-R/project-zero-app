const { Sequelize } = require('sequelize');
const path = require('path');

const env = process.env.NODE_ENV || 'development';
const databaseUrl = process.env.DATABASE_URL;

let sequelize;

if (databaseUrl) {
  if (databaseUrl.startsWith('sqlite:')) {
    // Handle SQLite URLs with relative paths
    const dbPath = databaseUrl.replace('sqlite://', '').replace('sqlite:', '');
    const fullPath = path.isAbsolute(dbPath)
      ? dbPath
      : path.join(process.cwd(), dbPath);

    sequelize = new Sequelize({
      dialect: 'sqlite',
      storage: fullPath,
      logging: env === 'development' ? console.log : false,
      pool: {
        max: 1, // SQLite doesn't support multiple connections
        idle: 30000,
        acquire: 60000,
      },
    });
  } else {
    // Handle PostgreSQL and other database URLs
    sequelize = new Sequelize(databaseUrl, {
      logging: env === 'development' ? console.log : false,
      pool: {
        max: 10,
        min: 0,
        idle: 30000,
        acquire: 60000,
      },
    });
  }
} else {
  // Default SQLite configuration
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: path.join(process.cwd(), 'category_service.db'),
    logging: env === 'development' ? console.log : false,
    pool: {
      max: 1,
      idle: 30000,
      acquire: 60000,
    },
  });
}

module.exports = {
  sequelize,
  Sequelize,
};

// Test database connection with retry logic
const testConnection = async (maxRetries = 5, retryDelay = 3000) => {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await sequelize.authenticate();
      console.log('Database connection established successfully.');
      return true;
    } catch (error) {
      lastError = error;
      console.error(`Database connection attempt ${attempt}/${maxRetries} failed:`, error.message);

      if (attempt < maxRetries) {
        console.log(`Retrying in ${retryDelay}ms...`);
        await new Promise(resolve => setTimeout(resolve, retryDelay));
        // Exponential backoff
        retryDelay = Math.min(retryDelay * 1.5, 30000);
      }
    }
  }

  console.error('Failed to connect to database after all retry attempts');
  throw lastError;
};

// Initialize database with automatic retries and migration
const initializeDatabase = async () => {
  try {
    console.log('Initializing database connection...');

    // Test connection with retries
    await testConnection();

    // Sync database (create tables if they don't exist)
    if (process.env.NODE_ENV !== 'test') {
      await sequelize.sync({ alter: env === 'development' });
      console.log('Database synchronized successfully.');
    }

    return true;
  } catch (error) {
    console.error('Database initialization failed:', error);
    throw error;
  }
};

// Health check for database
const checkDatabaseHealth = async () => {
  try {
    const start = Date.now();
    await sequelize.authenticate();
    const responseTime = Date.now() - start;

    return {
      status: 'connected',
      response_time: responseTime,
      dialect: sequelize.getDialect(),
      database: sequelize.getDatabaseName()
    };
  } catch (error) {
    return {
      status: 'disconnected',
      error: error.message,
      dialect: sequelize.getDialect()
    };
  }
};

// Graceful shutdown with connection cleanup
const closeConnection = async () => {
  try {
    console.log('Closing database connections...');

    // Close all connections in the pool
    await sequelize.close();

    console.log('Database connection closed successfully.');
    return true;
  } catch (error) {
    console.error('Error closing database connection:', error);
    throw error;
  }
};

// Monitor database connection status
const monitorConnection = (intervalMs = 30000) => {
  const monitor = setInterval(async () => {
    try {
      await sequelize.authenticate();
    } catch (error) {
      console.error('Database connection lost:', error.message);
      // Could implement reconnection logic here
    }
  }, intervalMs);

  return () => clearInterval(monitor);
};

// Get database connection info
const getConnectionInfo = () => {
  return {
    dialect: sequelize.getDialect(),
    database: sequelize.getDatabaseName(),
    host: sequelize.config.host,
    port: sequelize.config.port,
    pool: {
      max: sequelize.connectionManager.pool.options.max,
      min: sequelize.connectionManager.pool.options.min,
      idle: sequelize.connectionManager.pool.options.idle,
      acquire: sequelize.connectionManager.pool.options.acquire
    },
    options: {
      logging: !!sequelize.options.logging,
      timezone: sequelize.options.timezone
    }
  };
};

module.exports.testConnection = testConnection;
module.exports.closeConnection = closeConnection;
module.exports.initializeDatabase = initializeDatabase;
module.exports.checkDatabaseHealth = checkDatabaseHealth;
module.exports.monitorConnection = monitorConnection;
module.exports.getConnectionInfo = getConnectionInfo;