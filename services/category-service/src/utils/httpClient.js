const axios = require('axios');
const crypto = require('crypto');

class HttpClient {
  constructor(options = {}) {
    this.baseURL = options.baseURL;
    this.timeout = options.timeout || 10000;
    this.retries = options.retries || 3;
    this.retryDelay = options.retryDelay || 1000;
    this.defaultHeaders = options.headers || {};

    // Create axios instance
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: this.defaultHeaders
    });

    // Add request interceptor for correlation IDs and logging
    this.client.interceptors.request.use(
      (config) => {
        // Add correlation ID if not present
        if (!config.headers['X-Request-ID']) {
          config.headers['X-Request-ID'] = crypto.randomUUID();
        }

        // Add user agent
        config.headers['User-Agent'] = 'category-service/1.0.0';

        // Log outgoing request
        console.log(`HTTP Request: ${config.method?.toUpperCase()} ${config.url}`, {
          headers: this.sanitizeHeaders(config.headers),
          timeout: config.timeout,
          requestId: config.headers['X-Request-ID']
        });

        return config;
      },
      (error) => {
        console.error('HTTP Request Error:', error.message);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging and error handling
    this.client.interceptors.response.use(
      (response) => {
        // Log successful response
        console.log(`HTTP Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`, {
          status: response.status,
          statusText: response.statusText,
          responseTime: response.headers['x-response-time'],
          requestId: response.config.headers['X-Request-ID']
        });

        return response;
      },
      (error) => {
        // Log error response
        const response = error.response;
        if (response) {
          console.error(`HTTP Error: ${response.status} ${error.config.method?.toUpperCase()} ${error.config.url}`, {
            status: response.status,
            statusText: response.statusText,
            data: response.data,
            requestId: error.config.headers['X-Request-ID']
          });
        } else {
          console.error('HTTP Network Error:', {
            message: error.message,
            code: error.code,
            requestId: error.config?.headers['X-Request-ID']
          });
        }

        return Promise.reject(error);
      }
    );
  }

  // Sanitize headers for logging (remove sensitive information)
  sanitizeHeaders(headers) {
    const sanitized = { ...headers };
    const sensitiveKeys = ['authorization', 'cookie', 'x-api-key'];

    for (const key of sensitiveKeys) {
      if (sanitized[key]) {
        sanitized[key] = '[REDACTED]';
      }
    }

    return sanitized;
  }

  // Retry logic with exponential backoff
  async withRetry(requestFn, retries = this.retries, delay = this.retryDelay) {
    try {
      return await requestFn();
    } catch (error) {
      if (retries === 0 || !this.shouldRetry(error)) {
        throw error;
      }

      console.warn(`Request failed, retrying in ${delay}ms. Retries left: ${retries - 1}`);
      await this.sleep(delay);

      // Exponential backoff
      return this.withRetry(requestFn, retries - 1, delay * 2);
    }
  }

  // Determine if request should be retried
  shouldRetry(error) {
    if (!error.response) {
      // Network errors should be retried
      return true;
    }

    const status = error.response.status;

    // Retry on server errors (5xx) and some client errors
    return status >= 500 || status === 408 || status === 429;
  }

  // Sleep utility for retry delays
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // GET request with retry logic
  async get(url, config = {}) {
    return this.withRetry(() => this.client.get(url, config));
  }

  // POST request with retry logic
  async post(url, data, config = {}) {
    return this.withRetry(() => this.client.post(url, data, config));
  }

  // PUT request with retry logic
  async put(url, data, config = {}) {
    return this.withRetry(() => this.client.put(url, data, config));
  }

  // PATCH request with retry logic
  async patch(url, data, config = {}) {
    return this.withRetry(() => this.client.patch(url, data, config));
  }

  // DELETE request with retry logic
  async delete(url, config = {}) {
    return this.withRetry(() => this.client.delete(url, config));
  }

  // HEAD request with retry logic
  async head(url, config = {}) {
    return this.withRetry(() => this.client.head(url, config));
  }

  // Health check utility
  async healthCheck(endpoint = '/health') {
    try {
      const response = await this.get(endpoint, { timeout: 5000 });
      return {
        status: 'healthy',
        statusCode: response.status,
        responseTime: response.headers['x-response-time'] || 'unknown',
        data: response.data
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        statusCode: error.response?.status || null,
        error: error.message,
        code: error.code
      };
    }
  }

  // Circuit breaker state
  _circuitState = {
    failures: 0,
    lastFailure: null,
    state: 'closed' // closed, open, half-open
  };

  // Circuit breaker configuration
  _circuitConfig = {
    failureThreshold: 5,
    timeout: 60000, // 1 minute
    resetTimeout: 30000 // 30 seconds
  };

  // Circuit breaker wrapper
  async withCircuitBreaker(requestFn) {
    const now = Date.now();

    // Check if circuit is open
    if (this._circuitState.state === 'open') {
      if (now - this._circuitState.lastFailure < this._circuitConfig.timeout) {
        throw new Error('Circuit breaker is open - service unavailable');
      } else {
        // Transition to half-open
        this._circuitState.state = 'half-open';
      }
    }

    try {
      const result = await requestFn();

      // Success - reset circuit breaker
      if (this._circuitState.state === 'half-open') {
        this._circuitState.state = 'closed';
        this._circuitState.failures = 0;
        this._circuitState.lastFailure = null;
      }

      return result;
    } catch (error) {
      // Failure - update circuit breaker
      this._circuitState.failures++;
      this._circuitState.lastFailure = now;

      if (this._circuitState.failures >= this._circuitConfig.failureThreshold) {
        this._circuitState.state = 'open';
      }

      throw error;
    }
  }

  // Request with circuit breaker and retry
  async request(method, url, data = null, config = {}) {
    return this.withCircuitBreaker(() => {
      switch (method.toLowerCase()) {
        case 'get':
          return this.get(url, config);
        case 'post':
          return this.post(url, data, config);
        case 'put':
          return this.put(url, data, config);
        case 'patch':
          return this.patch(url, data, config);
        case 'delete':
          return this.delete(url, config);
        case 'head':
          return this.head(url, config);
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }
    });
  }

  // Batch requests with concurrency control
  async batchRequests(requests, concurrency = 5) {
    const results = [];
    const errors = [];

    // Process requests in batches
    for (let i = 0; i < requests.length; i += concurrency) {
      const batch = requests.slice(i, i + concurrency);

      const batchPromises = batch.map(async (request, index) => {
        try {
          const result = await this.request(
            request.method,
            request.url,
            request.data,
            request.config
          );
          return { index: i + index, result, error: null };
        } catch (error) {
          return { index: i + index, result: null, error };
        }
      });

      const batchResults = await Promise.all(batchPromises);

      for (const { index, result, error } of batchResults) {
        if (error) {
          errors.push({ index, error });
        } else {
          results.push({ index, result });
        }
      }
    }

    return { results, errors };
  }

  // Get circuit breaker status
  getCircuitStatus() {
    return {
      state: this._circuitState.state,
      failures: this._circuitState.failures,
      lastFailure: this._circuitState.lastFailure,
      isHealthy: this._circuitState.state === 'closed'
    };
  }

  // Reset circuit breaker
  resetCircuit() {
    this._circuitState.state = 'closed';
    this._circuitState.failures = 0;
    this._circuitState.lastFailure = null;
  }
}

// Factory function to create HTTP clients for different services
const createServiceClient = (serviceName, baseURL, options = {}) => {
  const defaultOptions = {
    baseURL,
    timeout: 10000,
    retries: 3,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    ...options
  };

  const client = new HttpClient(defaultOptions);

  // Add service-specific methods
  client.serviceName = serviceName;

  // Add health check with service-specific endpoint
  client.checkHealth = async () => {
    try {
      return await client.healthCheck();
    } catch (error) {
      return {
        status: 'unhealthy',
        service: serviceName,
        error: error.message
      };
    }
  };

  return client;
};

module.exports = {
  HttpClient,
  createServiceClient
};