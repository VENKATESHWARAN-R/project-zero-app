# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile --production=false

# Copy source code
COPY . .

# Run linting and tests (optional - comment out if you want faster builds)
# RUN yarn lint
# RUN yarn test

# Install only production dependencies
RUN yarn install --frozen-lockfile --production=true

# Production stage
FROM node:18-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S category-service -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Copy node_modules from builder stage
COPY --from=builder /app/node_modules ./node_modules

# Copy source code
COPY --chown=category-service:nodejs . .

# Create data directory for SQLite
RUN mkdir -p data && chown category-service:nodejs data

# Switch to non-root user
USER category-service

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8005/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the application
CMD ["yarn", "start"]