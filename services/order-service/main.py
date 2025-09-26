from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from src.config import settings
from src.database import init_db, close_db
from src.logging_config import setup_logging, set_correlation_id, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Order Processing Service", extra={
        "version": "1.0.0",
        "environment": settings.environment,
        "port": settings.port
    })

    # Initialize database
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Order Processing Service")
    close_db()


# Create FastAPI application
app = FastAPI(
    title="Order Processing Service",
    description="Order lifecycle management service for Project Zero App e-commerce platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware in production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to all requests."""
    # Extract correlation ID from headers or generate new one
    correlation_id = request.headers.get("x-correlation-id")
    correlation_id = set_correlation_id(correlation_id)

    # Add to response headers
    response: Response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id

    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses."""
    logger.info("Request received", extra={
        "method": request.method,
        "url": str(request.url),
        "client_host": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    })

    response: Response = await call_next(request)

    logger.info("Request completed", extra={
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "response_time_ms": getattr(response, "process_time", 0) * 1000,
    })

    return response


# Health check endpoint (minimal implementation)
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "order-processing-service",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness check with dependency validation."""
    # TODO: Add database connectivity and external service checks
    return {
        "status": "ready",
        "service": "order-processing-service",
        "version": "1.0.0",
        "dependencies": {
            "database": "connected",
            "auth_service": "unknown",
            "cart_service": "unknown",
            "product_service": "unknown"
        }
    }


# Import and include API routers
from src.api import orders, admin, shipping

app.include_router(orders.router, tags=["orders"])
app.include_router(admin.router, tags=["admin"])
app.include_router(shipping.router, tags=["shipping"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )