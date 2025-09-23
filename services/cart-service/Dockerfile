# Use official Node.js runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S cartservice && \
    adduser -S cartservice -u 1001

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile --production && \
    yarn cache clean

# Copy application code
COPY src/ src/
COPY scripts/ scripts/

# Create logs directory
RUN mkdir -p logs && \
    chown -R cartservice:cartservice /app

# Switch to non-root user
USER cartservice

# Expose service port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8007/health || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8007

# Start the service
CMD ["node", "src/server.js"]