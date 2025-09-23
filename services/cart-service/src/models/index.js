const { Sequelize } = require('sequelize');
const path = require('path');

// Database configuration
const getDatabaseConfig = () => {
  const databaseUrl = process.env.DATABASE_URL || 'sqlite:./cart.db';

  if (databaseUrl.includes('sqlite')) {
    return {
      dialect: 'sqlite',
      storage: databaseUrl.replace('sqlite:', ''),
      logging: process.env.NODE_ENV === 'development' ? console.log : false,
    };
  }

  // PostgreSQL configuration
  return {
    url: databaseUrl,
    dialect: 'postgres',
    logging: process.env.NODE_ENV === 'development' ? console.log : false,
    pool: {
      max: 5,
      min: 0,
      acquire: 30000,
      idle: 10000,
    },
  };
};

// Initialize Sequelize
const sequelize = process.env.DATABASE_URL
  ? new Sequelize(process.env.DATABASE_URL, getDatabaseConfig())
  : new Sequelize(getDatabaseConfig());

// Import models
const Cart = require('./Cart')(sequelize);
const CartItem = require('./CartItem')(sequelize);

// Store models in an object
const models = {
  Cart,
  CartItem,
  sequelize,
  Sequelize,
};

// Set up associations
Object.keys(models).forEach((modelName) => {
  if (models[modelName].associate) {
    models[modelName].associate(models);
  }
});

module.exports = models;
