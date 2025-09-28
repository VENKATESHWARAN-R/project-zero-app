const path = require('path');

const config = {
  port: process.env.PORT || 8011,
  host: process.env.HOST || '0.0.0.0',
  nodeEnv: process.env.NODE_ENV || 'development',

  // JWT Configuration
  jwt: {
    secret: process.env.JWT_SECRET_KEY || 'dev-secret-key-change-in-production',
    algorithm: process.env.JWT_ALGORITHM || 'HS256',
    accessTokenExpire: process.env.ACCESS_TOKEN_EXPIRE_MINUTES || '15',
    refreshTokenExpire: process.env.REFRESH_TOKEN_EXPIRE_DAYS || '30',
  },

  // Database Configuration
  database: {
    url: process.env.DATABASE_URL || `sqlite:${path.join(__dirname, '../../notification_service.db')}`,
    dialect: process.env.DB_DIALECT || 'sqlite',
    storage: process.env.DB_STORAGE || path.join(__dirname, '../../notification_service.db'),
    logging: process.env.DB_LOGGING === 'true' ? console.log : false,
    pool: {
      max: parseInt(process.env.DB_POOL_MAX) || 5,
      min: parseInt(process.env.DB_POOL_MIN) || 0,
      acquire: parseInt(process.env.DB_POOL_ACQUIRE) || 30000,
      idle: parseInt(process.env.DB_POOL_IDLE) || 10000,
    },
  },

  // External Services
  services: {
    auth: {
      url: process.env.AUTH_SERVICE_URL || 'http://localhost:8001',
      verifyEndpoint: '/auth/verify',
    },
    userProfile: {
      url: process.env.USER_PROFILE_SERVICE_URL || 'http://localhost:8002',
    },
    order: {
      url: process.env.ORDER_SERVICE_URL || 'http://localhost:8008',
    },
    payment: {
      url: process.env.PAYMENT_SERVICE_URL || 'http://localhost:8009',
    },
  },

  // Rate Limiting
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX) || 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.',
    standardHeaders: true,
    legacyHeaders: false,
  },

  // CORS Configuration
  cors: {
    origin: process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : ['http://localhost:3000'],
    credentials: true,
    optionsSuccessStatus: 200,
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
    enableConsole: process.env.LOG_CONSOLE !== 'false',
    enableFile: process.env.LOG_FILE === 'true',
    filePath: process.env.LOG_FILE_PATH || path.join(__dirname, '../../logs/notification-service.log'),
  },

  // Mock Provider Configuration
  providers: {
    email: {
      enabled: process.env.EMAIL_PROVIDER_ENABLED !== 'false',
      mockDelay: parseInt(process.env.EMAIL_MOCK_DELAY) || 1000, // milliseconds
      failureRate: parseFloat(process.env.EMAIL_FAILURE_RATE) || 0.05, // 5% failure rate
    },
    sms: {
      enabled: process.env.SMS_PROVIDER_ENABLED !== 'false',
      mockDelay: parseInt(process.env.SMS_MOCK_DELAY) || 500, // milliseconds
      failureRate: parseFloat(process.env.SMS_FAILURE_RATE) || 0.03, // 3% failure rate
    },
    inApp: {
      enabled: process.env.IN_APP_PROVIDER_ENABLED !== 'false',
      mockDelay: parseInt(process.env.IN_APP_MOCK_DELAY) || 100, // milliseconds
    },
  },

  // Notification Configuration
  notifications: {
    maxRetries: parseInt(process.env.NOTIFICATION_MAX_RETRIES) || 3,
    retryDelay: parseInt(process.env.NOTIFICATION_RETRY_DELAY) || 300, // seconds
    batchSize: parseInt(process.env.NOTIFICATION_BATCH_SIZE) || 100,
    schedulerInterval: parseInt(process.env.SCHEDULER_INTERVAL) || 60, // seconds
  },

  // Security Configuration
  security: {
    trustProxy: process.env.TRUST_PROXY === 'true',
    helmet: {
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", 'data:', 'https:'],
        },
      },
    },
  },
};

module.exports = config;