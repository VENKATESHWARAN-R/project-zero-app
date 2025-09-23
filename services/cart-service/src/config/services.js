const config = require('./env');

// Service configuration and URL management
const services = {
  auth: {
    name: 'Auth Service',
    baseUrl: config.services.auth.url,
    timeout: config.services.auth.timeout,
    endpoints: {
      verify: '/auth/verify',
      health: '/health',
    },
    getUrl: (endpoint) =>
      `${services.auth.baseUrl}${services.auth.endpoints[endpoint]}`,
  },

  product: {
    name: 'Product Catalog Service',
    baseUrl: config.services.product.url,
    timeout: config.services.product.timeout,
    endpoints: {
      getProduct: (id) => `/products/${id}`,
      validateProducts: '/products/validate',
      health: '/health',
    },
    getUrl: (endpoint, ...args) => {
      const endpointTemplate = services.product.endpoints[endpoint];
      if (typeof endpointTemplate === 'function') {
        return `${services.product.baseUrl}${endpointTemplate(...args)}`;
      }
      return `${services.product.baseUrl}${endpointTemplate}`;
    },
  },
};

// Service discovery helpers
const getServiceConfig = (serviceName) => {
  const service = services[serviceName];
  if (!service) {
    throw new Error(`Unknown service: ${serviceName}`);
  }
  return service;
};

// Health check configuration for external services
const getHealthCheckConfig = () => {
  return {
    services: [
      {
        name: 'auth',
        url: services.auth.getUrl('health'),
        timeout: services.auth.timeout,
      },
      {
        name: 'product',
        url: services.product.getUrl('health'),
        timeout: services.product.timeout,
      },
    ],
    checkInterval: config.health.checkInterval,
  };
};

// Circuit breaker configuration (for future implementation)
const getCircuitBreakerConfig = () => {
  return {
    auth: {
      timeout: services.auth.timeout,
      errorThresholdPercentage: 50,
      resetTimeout: 60000, // 1 minute
    },
    product: {
      timeout: services.product.timeout,
      errorThresholdPercentage: 50,
      resetTimeout: 60000, // 1 minute
    },
  };
};

// Service endpoints mapping
const endpoints = {
  // Auth service endpoints
  authVerify: () => services.auth.getUrl('verify'),
  authHealth: () => services.auth.getUrl('health'),

  // Product service endpoints
  productGet: (productId) => services.product.getUrl('getProduct', productId),
  productValidate: () => services.product.getUrl('validateProducts'),
  productHealth: () => services.product.getUrl('health'),
};

module.exports = {
  services,
  getServiceConfig,
  getHealthCheckConfig,
  getCircuitBreakerConfig,
  endpoints,
};
