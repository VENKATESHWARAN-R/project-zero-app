# Build stage
FROM golang:1.20-alpine AS builder

# Install git for dependency management
RUN apk add --no-cache git ca-certificates

# Create app user for security
RUN adduser -D -g '' appuser

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download
RUN go mod verify

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' \
    -a -installsuffix cgo \
    -o gateway ./cmd/gateway

# Final stage
FROM alpine:3.19

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates

# Create app user
RUN adduser -D -g '' appuser

# Create directories
RUN mkdir -p /app/config

# Copy the binary and configuration from builder stage
COPY --from=builder /app/gateway /app/gateway
COPY --from=builder /app/config /app/config

# Copy ca-certificates
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD /app/gateway --health-check || exit 1

# Run the gateway
CMD ["./gateway"]