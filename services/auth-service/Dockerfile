# Multi-stage Docker build for Project Zero App Authentication Service
# Optimized for production deployment with security and performance in mind

# Build stage
FROM python:3.13-slim as builder

# Build arguments
ARG PYTHON_VERSION=3.13
ARG PORT=8001

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN uv pip install -r pyproject.toml

# Production stage
FROM python:3.13-slim as production

# Production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=${PORT:-8001} \
    HOST=0.0.0.0

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Default command
CMD ["sh", "-c", "uvicorn main:app --host $HOST --port $PORT --workers 1"]

# Labels for metadata
LABEL maintainer="Project Zero Team" \
      service="auth-service" \
      version="1.0.0" \
      description="JWT-based authentication microservice for Project Zero App" \
      org.opencontainers.image.title="Project Zero Auth Service" \
      org.opencontainers.image.description="Authentication microservice with JWT, bcrypt, and rate limiting" \
      org.opencontainers.image.source="https://github.com/project-zero/auth-service" \
      org.opencontainers.image.vendor="Project Zero Team"