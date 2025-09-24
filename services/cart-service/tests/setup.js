const { sequelize } = require('../src/models');

// Mock services for testing
jest.mock('../src/services/authService', () => require('./mocks/authService'));
jest.mock('../src/services/productService', () => require('./mocks/productService'));

beforeAll(async () => {
  process.env.NODE_ENV = 'test';
  process.env.DATABASE_URL = 'sqlite::memory:';
  process.env.LOG_LEVEL = 'error';
  process.env.AUTH_SERVICE_URL = 'http://mock-auth-service:8001';
  process.env.PRODUCT_SERVICE_URL = 'http://mock-product-service:8004';

  try {
    await sequelize.authenticate();
    await sequelize.sync({ force: true });
  } catch (error) {
    console.warn('Database setup failed:', error.message);
  }
});

afterAll(async () => {
  try {
    await sequelize.close();
  } catch (error) {
    console.warn('Database cleanup failed:', error.message);
  }
});

beforeEach(async () => {
  try {
    await sequelize.sync({ force: true });
  } catch (error) {
    console.warn('Database reset failed:', error.message);
  }
});

global.testTimeout = 10000;