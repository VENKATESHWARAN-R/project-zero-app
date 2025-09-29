const { Sequelize } = require('sequelize');
const config = require('./env');

const getDatabaseConfig = () => {
  const baseConfig = {
    logging: config.database.logging ? console.log : false,
    pool: {
      max: 5,
      min: 0,
      acquire: 30000,
      idle: 10000,
    },
    retry: {
      max: 3,
    },
  };

  if (config.database.dialect === 'sqlite') {
    const storagePath = config.database.url.replace('sqlite:', '');
    return {
      ...baseConfig,
      dialect: 'sqlite',
      storage: storagePath,
      // SQLite specific options
      dialectOptions: {
        // Enable foreign keys
        pragma: {
          foreign_keys: true,
        },
      },
    };
  }

  // PostgreSQL configuration
  return {
    ...baseConfig,
    dialect: 'postgres',
    dialectOptions: {
      // Disable SSL for development/test databases
      ssl: false,
    },
  };
};

const createSequelizeInstance = () => {
  const dbConfig = getDatabaseConfig();

  if (config.database.dialect === 'postgres') {
    return new Sequelize(config.database.url, dbConfig);
  }

  return new Sequelize(dbConfig);
};

// Health check function for database
const checkDatabaseHealth = async (sequelize) => {
  try {
    await sequelize.authenticate();
    return { healthy: true, message: 'Database connection successful' };
  } catch (error) {
    return {
      healthy: false,
      message: `Database connection failed: ${error.message}`,
    };
  }
};

module.exports = {
  createSequelizeInstance,
  getDatabaseConfig,
  checkDatabaseHealth,
  config: config.database,
};
