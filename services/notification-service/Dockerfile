# Multi-stage build for Node.js notification service
FROM node:20-alpine AS base

# Install security updates and create non-root user
RUN apk update && apk upgrade && \
    addgroup -g 1001 -S notificationuser && \
    adduser -S notificationuser -u 1001 -G notificationuser

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy application source code
COPY . .

# Create logs directory and set permissions
RUN mkdir -p logs && \
    chown -R notificationuser:notificationuser /app

# Switch to non-root user
USER notificationuser

# Expose port
EXPOSE 8011

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:8011/health', (res) => { \
        process.exit(res.statusCode === 200 ? 0 : 1); \
    }).on('error', () => { process.exit(1); });"

# Start the application
CMD ["node", "src/server.js"]

# Development stage
FROM base AS development

# Switch to root user to install dev dependencies
USER root

# Install development dependencies
RUN npm install

# Switch back to non-root user
USER notificationuser

# Override command for development
CMD ["npm", "run", "dev"]