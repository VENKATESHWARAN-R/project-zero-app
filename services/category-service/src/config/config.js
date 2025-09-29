const path = require('path');

const config = {
  development: {
    dialect: 'sqlite',
    storage: path.join(__dirname, '../../category_service.db'),
    logging: console.log,
  },
  test: {
    dialect: 'sqlite',
    storage: ':memory:',
    logging: false,
  },
  production: {
    use_env_variable: 'DATABASE_URL',
    dialect: 'postgres',
    logging: false,
    pool: {
      max: 10,
      min: 0,
      idle: 30000,
      acquire: 60000,
    },
  },
};

module.exports = config;