const path = require('path');

// Load environment variables from .env file in development
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config({ path: path.join(__dirname, '../../.env') });
}

const config = {
  // Server configuration
  port: parseInt(process.env.PORT || '8007'),
  host: process.env.HOST || '0.0.0.0',
  nodeEnv: process.env.NODE_ENV || 'development',

  // Database configuration
  database: {
    url: process.env.DATABASE_URL || 'sqlite:./cart.db',
    dialect: process.env.DATABASE_URL?.includes('postgres')
      ? 'postgres'
      : 'sqlite',
    logging: process.env.NODE_ENV === 'development',
  },

  // External services
  services: {
    auth: {
      url: process.env.AUTH_SERVICE_URL || 'http://localhost:8001',
      timeout: parseInt(process.env.REQUEST_TIMEOUT || '5000'),
    },
    product: {
      url: process.env.PRODUCT_SERVICE_URL || 'http://localhost:8004',
      timeout: parseInt(process.env.REQUEST_TIMEOUT || '5000'),
    },
  },

  // Cart business rules
  cart: {
    ttlHours: parseInt(process.env.CART_TTL_HOURS || '24'),
    maxQuantityPerItem: parseInt(process.env.MAX_QUANTITY_PER_ITEM || '10'),
    maxTotalItems: parseInt(process.env.MAX_TOTAL_ITEMS || '50'),
  },

  // Security and authentication
  auth: {
    jwtSecret: process.env.JWT_SECRET || null, // Optional for local validation
  },

  // CORS configuration
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true,
  },

  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    enableFileLogging: process.env.NODE_ENV === 'production',
    logDirectory: process.env.LOG_DIRECTORY || 'logs',
  },

  // Health check configuration
  health: {
    checkInterval: parseInt(process.env.HEALTH_CHECK_INTERVAL || '30000'), // 30 seconds
  },
};

// Validate required configuration
const validateConfig = () => {
  const errors = [];

  if (!config.port || config.port < 1 || config.port > 65535) {
    errors.push('Invalid PORT: must be between 1 and 65535');
  }

  if (!config.services.auth.url) {
    errors.push('AUTH_SERVICE_URL is required');
  }

  if (!config.services.product.url) {
    errors.push('PRODUCT_SERVICE_URL is required');
  }

  if (
    config.cart.maxQuantityPerItem < 1 ||
    config.cart.maxQuantityPerItem > 100
  ) {
    errors.push('MAX_QUANTITY_PER_ITEM must be between 1 and 100');
  }

  if (config.cart.ttlHours < 1 || config.cart.ttlHours > 8760) {
    // 1 year max
    errors.push('CART_TTL_HOURS must be between 1 and 8760');
  }

  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
};

// Validate configuration on module load
validateConfig();

module.exports = config;
