const joi = require('joi');

/**
 * Environment variable validation schema for the notification service
 * Validates all required and optional environment variables with appropriate types and constraints
 */
const envSchema = joi.object({
  // Server Configuration
  PORT: joi.number().port().default(8011),
  HOST: joi.string().hostname().default('0.0.0.0'),
  NODE_ENV: joi.string().valid('development', 'test', 'production', 'staging').default('development'),

  // JWT Configuration (should match auth service settings)
  JWT_SECRET_KEY: joi.string().min(32).when('NODE_ENV', {
    is: 'production',
    then: joi.required(),
    otherwise: joi.optional()
  }).description('JWT secret key - REQUIRED in production'),
  JWT_ALGORITHM: joi.string().valid('HS256', 'HS384', 'HS512').default('HS256'),
  ACCESS_TOKEN_EXPIRE_MINUTES: joi.number().positive().default(15),
  REFRESH_TOKEN_EXPIRE_DAYS: joi.number().positive().default(30),

  // Database Configuration
  DATABASE_URL: joi.string().uri().optional().description('Full database URL'),
  DB_DIALECT: joi.string().valid('sqlite', 'postgres', 'mysql', 'mariadb').default('sqlite'),
  DB_STORAGE: joi.string().optional().description('SQLite database file path'),
  DB_LOGGING: joi.boolean().default(false),
  DB_POOL_MAX: joi.number().positive().max(50).default(5),
  DB_POOL_MIN: joi.number().min(0).default(0),
  DB_POOL_ACQUIRE: joi.number().positive().default(30000),
  DB_POOL_IDLE: joi.number().positive().default(10000),

  // External Service URLs
  AUTH_SERVICE_URL: joi.string().uri().required().description('Auth service URL for JWT verification'),
  USER_PROFILE_SERVICE_URL: joi.string().uri().optional(),
  ORDER_SERVICE_URL: joi.string().uri().optional(),
  PAYMENT_SERVICE_URL: joi.string().uri().optional(),

  // Rate Limiting Configuration
  RATE_LIMIT_WINDOW_MS: joi.number().positive().default(900000), // 15 minutes
  RATE_LIMIT_MAX: joi.number().positive().default(100),

  // CORS Configuration
  CORS_ORIGIN: joi.string().optional().description('Comma-separated list of allowed origins'),

  // Logging Configuration
  LOG_LEVEL: joi.string().valid('error', 'warn', 'info', 'http', 'verbose', 'debug', 'silly').default('info'),
  LOG_FORMAT: joi.string().valid('json', 'simple', 'combined').default('json'),
  LOG_CONSOLE: joi.boolean().default(true),
  LOG_FILE: joi.boolean().default(false),
  LOG_FILE_PATH: joi.string().optional(),

  // Mock Provider Configuration
  EMAIL_PROVIDER_ENABLED: joi.boolean().default(true),
  EMAIL_MOCK_DELAY: joi.number().min(0).max(10000).default(1000),
  EMAIL_FAILURE_RATE: joi.number().min(0).max(1).default(0.05),

  SMS_PROVIDER_ENABLED: joi.boolean().default(true),
  SMS_MOCK_DELAY: joi.number().min(0).max(10000).default(500),
  SMS_FAILURE_RATE: joi.number().min(0).max(1).default(0.03),

  IN_APP_PROVIDER_ENABLED: joi.boolean().default(true),
  IN_APP_MOCK_DELAY: joi.number().min(0).max(5000).default(100),

  // Notification Configuration
  NOTIFICATION_MAX_RETRIES: joi.number().min(0).max(10).default(3),
  NOTIFICATION_RETRY_DELAY: joi.number().positive().default(300),
  NOTIFICATION_BATCH_SIZE: joi.number().positive().max(1000).default(100),
  SCHEDULER_INTERVAL: joi.number().positive().default(60),

  // Security Configuration
  TRUST_PROXY: joi.boolean().default(false),
}).unknown(true); // Allow other environment variables not defined here

/**
 * Validates environment variables against the schema
 * @returns {Object} Validated and transformed environment variables
 * @throws {Error} If validation fails
 */
function validateEnv() {
  const { error, value } = envSchema.validate(process.env, {
    abortEarly: false,
    stripUnknown: false,
    convert: true,
  });

  if (error) {
    const errorMessage = error.details
      .map(detail => `${detail.path.join('.')}: ${detail.message}`)
      .join(', ');

    throw new Error(`Environment validation failed: ${errorMessage}`);
  }

  return value;
}

/**
 * Gets validation warnings for non-critical configuration issues
 * @returns {Array} Array of warning messages
 */
function getValidationWarnings() {
  const warnings = [];

  // Check for production-specific warnings
  if (process.env.NODE_ENV === 'production') {
    if (!process.env.JWT_SECRET_KEY || process.env.JWT_SECRET_KEY.length < 32) {
      warnings.push('JWT_SECRET_KEY should be at least 32 characters in production');
    }

    if (process.env.JWT_SECRET_KEY === 'dev-secret-key-change-in-production') {
      warnings.push('JWT_SECRET_KEY is using default development value in production');
    }

    if (!process.env.AUTH_SERVICE_URL || process.env.AUTH_SERVICE_URL.includes('localhost')) {
      warnings.push('AUTH_SERVICE_URL should not use localhost in production');
    }

    if (process.env.LOG_LEVEL === 'debug' || process.env.LOG_LEVEL === 'silly') {
      warnings.push('LOG_LEVEL is set to verbose level in production - consider using info or warn');
    }
  }

  // Check for development warnings
  if (process.env.NODE_ENV === 'development') {
    if (!process.env.DATABASE_URL && process.env.DB_DIALECT !== 'sqlite') {
      warnings.push('Using non-SQLite database in development without DATABASE_URL');
    }
  }

  // Check for potentially problematic configurations
  if (process.env.EMAIL_FAILURE_RATE && parseFloat(process.env.EMAIL_FAILURE_RATE) > 0.1) {
    warnings.push('EMAIL_FAILURE_RATE is set above 10% - this may cause excessive failures');
  }

  if (process.env.SMS_FAILURE_RATE && parseFloat(process.env.SMS_FAILURE_RATE) > 0.1) {
    warnings.push('SMS_FAILURE_RATE is set above 10% - this may cause excessive failures');
  }

  if (process.env.RATE_LIMIT_MAX && parseInt(process.env.RATE_LIMIT_MAX) < 10) {
    warnings.push('RATE_LIMIT_MAX is set very low - this may cause legitimate requests to be blocked');
  }

  return warnings;
}

/**
 * Validates required service dependencies are configured
 * @returns {Object} Validation result with success flag and messages
 */
function validateServiceDependencies() {
  const result = {
    success: true,
    errors: [],
    warnings: []
  };

  // Check required services
  if (!process.env.AUTH_SERVICE_URL) {
    result.success = false;
    result.errors.push('AUTH_SERVICE_URL is required for JWT token verification');
  }

  // Check optional but recommended services
  if (!process.env.USER_PROFILE_SERVICE_URL) {
    result.warnings.push('USER_PROFILE_SERVICE_URL not configured - user preference lookups will be limited');
  }

  return result;
}

/**
 * Performs comprehensive environment validation including dependencies
 * @returns {Object} Complete validation result
 */
function performFullValidation() {
  try {
    // Validate basic environment variables
    const validatedEnv = validateEnv();

    // Get configuration warnings
    const warnings = getValidationWarnings();

    // Validate service dependencies
    const serviceValidation = validateServiceDependencies();

    return {
      success: serviceValidation.success,
      validatedEnv,
      errors: serviceValidation.errors,
      warnings: [...warnings, ...serviceValidation.warnings]
    };
  } catch (error) {
    return {
      success: false,
      validatedEnv: null,
      errors: [error.message],
      warnings: []
    };
  }
}

module.exports = {
  validateEnv,
  getValidationWarnings,
  validateServiceDependencies,
  performFullValidation,
  envSchema
};