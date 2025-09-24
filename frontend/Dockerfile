# Multi-stage Docker build for Project Zero Frontend
# Production-ready container image for the Next.js web application

# Stage 1: Install all dependencies (including dev) for builds
FROM node:22-alpine AS deps

# Install system libraries required by several npm dependencies
RUN apk add --no-cache libc6-compat

# Set working directory
WORKDIR /app

# Install dependencies based on lockfile for reproducible builds
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Build the Next.js application
FROM node:22-alpine AS builder

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

RUN apk add --no-cache libc6-compat

# Reuse fully resolved dependencies from the deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY . .

# Create the production build
RUN npm run build

# Stage 3: Install only production dependencies
FROM node:22-alpine AS production-deps

WORKDIR /app

RUN apk add --no-cache libc6-compat

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Stage 4: Final runtime image
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOST=0.0.0.0

RUN apk add --no-cache libc6-compat curl

# Create non-root user for runtime security
RUN addgroup -S nextjs && adduser -S -G nextjs nextjs

# Copy production node modules and build artifacts
COPY --from=production-deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.* ./

# Ensure proper permissions
RUN chown -R nextjs:nextjs /app

USER nextjs

# Expose application port
EXPOSE 3000

# Health check to verify Next.js responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Start the Next.js server
CMD ["npm", "run", "start"]

# Metadata labels
LABEL maintainer="Project Zero Team" \
      service="frontend" \
      version="1.0.0" \
      description="Next.js frontend for Project Zero App" \
      org.opencontainers.image.title="Project Zero Frontend" \
      org.opencontainers.image.description="Production-ready Next.js frontend" \
      org.opencontainers.image.vendor="Project Zero Team"
