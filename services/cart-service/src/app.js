const express = require('express');
const cors = require('cors');
const requestLogger = require('./middleware/requestLogger');
const errorHandler = require('./middleware/errorHandler');
const healthRoutes = require('./routes/health');
const cartRoutes = require('./routes/cart');

const app = express();

// Trust proxy for accurate IP addresses
app.set('trust proxy', true);

// CORS configuration
const corsOptions = {
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
  optionsSuccessStatus: 200,
};

// Middleware
app.use(cors(corsOptions));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging and correlation ID
app.use(requestLogger);

// Health check routes (no auth required)
app.use('/health', healthRoutes);

// Cart routes (auth required)
app.use('/cart', cartRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'Cart Service',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString(),
  });
});

// 404 handler for unknown routes
app.use((req, res) => {
  res.status(404).json({
    error: 'Route not found',
    timestamp: new Date().toISOString(),
    correlation_id: req.correlationId,
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

module.exports = app;
