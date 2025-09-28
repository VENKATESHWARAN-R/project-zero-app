const cors = require('cors');
const helmet = require('helmet');

const securityMiddleware = {
  // CORS configuration
  cors: cors({
    origin: function (origin, callback) {
      // Allow requests with no origin (like mobile apps or curl)
      if (!origin) return callback(null, true);

      // List of allowed origins
      const allowedOrigins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:8000',
        'https://project-zero-app.com'
      ];

      if (allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Correlation-ID']
  }),

  // Security headers using helmet
  helmet: helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'"],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"]
      }
    },
    crossOriginEmbedderPolicy: false,
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    }
  }),

  // Rate limiting (basic implementation)
  rateLimit: () => {
    const requests = new Map();
    const WINDOW_MS = 15 * 60 * 1000; // 15 minutes
    const MAX_REQUESTS = 100; // per window

    return (req, res, next) => {
      const clientId = req.ip || req.connection.remoteAddress;
      const now = Date.now();
      const windowStart = now - WINDOW_MS;

      // Clean old entries
      for (const [key, data] of requests.entries()) {
        if (data.timestamp < windowStart) {
          requests.delete(key);
        }
      }

      // Get current request count for this client
      const clientRequests = requests.get(clientId) || { count: 0, timestamp: now };

      if (clientRequests.timestamp < windowStart) {
        // Reset counter for new window
        clientRequests.count = 1;
        clientRequests.timestamp = now;
      } else {
        clientRequests.count++;
      }

      requests.set(clientId, clientRequests);

      if (clientRequests.count > MAX_REQUESTS) {
        return res.status(429).json({
          error: 'rate_limit_exceeded',
          message: 'Too many requests. Please try again later.',
          retryAfter: Math.ceil((WINDOW_MS - (now - clientRequests.timestamp)) / 1000),
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      // Add rate limit headers
      res.set({
        'X-RateLimit-Limit': MAX_REQUESTS,
        'X-RateLimit-Remaining': Math.max(0, MAX_REQUESTS - clientRequests.count),
        'X-RateLimit-Reset': new Date(clientRequests.timestamp + WINDOW_MS).toISOString()
      });

      next();
    };
  },

  // Request size limiting
  requestSizeLimit: () => {
    return (req, res, next) => {
      const maxSize = 1024 * 1024; // 1MB

      if (req.headers['content-length'] && parseInt(req.headers['content-length']) > maxSize) {
        return res.status(413).json({
          error: 'payload_too_large',
          message: 'Request body too large',
          maxSize: '1MB',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      next();
    };
  },

  // Security headers for JSON responses
  jsonResponseHeaders: (req, res, next) => {
    res.set({
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    });
    next();
  }
};

module.exports = securityMiddleware;