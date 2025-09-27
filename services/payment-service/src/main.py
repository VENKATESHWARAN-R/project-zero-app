"""FastAPI application entry point for Payment Service."""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from .models.database import init_database, check_database_connection
from .services.webhook_simulator import start_webhook_simulator, stop_webhook_simulator
from .api.payments import router as payments_router
from .api.payment_methods import router as payment_methods_router
from .api.webhooks import router as webhooks_router


# Application startup time
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting Payment Processing Service...")
    
    # Initialize database
    try:
        await init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise
    
    # Start webhook simulator
    try:
        await start_webhook_simulator()
        print("Webhook simulator started")
    except Exception as e:
        print(f"Webhook simulator startup failed: {e}")
    
    print("Payment Processing Service started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down Payment Processing Service...")
    
    # Stop webhook simulator
    try:
        await stop_webhook_simulator()
        print("Webhook simulator stopped")
    except Exception as e:
        print(f"Webhook simulator shutdown error: {e}")
    
    print("Payment Processing Service shutdown complete")


# Create FastAPI application instance
app = FastAPI(
    title="Payment Processing Service",
    description="Mock payment processing service for Project Zero App e-commerce platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Payment Processing Service",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns basic service health status without dependencies.
    """
    uptime = time.time() - startup_time
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": round(uptime, 2)
    }


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    
    Checks if service is ready to handle requests by verifying
    dependencies like database and external services.
    """
    checks = {}
    overall_ready = True
    
    # Check database connection
    try:
        db_healthy = check_database_connection()
        checks["database"] = "ready" if db_healthy else "not_ready"
        if not db_healthy:
            overall_ready = False
    except Exception:
        checks["database"] = "not_ready"
        overall_ready = False
    
    # Check auth service connection
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{auth_service_url}/health")
            checks["auth_service"] = "ready" if response.status_code == 200 else "not_ready"
            if response.status_code != 200:
                overall_ready = False
    except Exception:
        checks["auth_service"] = "not_ready"
        overall_ready = False
    
    # Check order service connection
    order_service_url = os.getenv("ORDER_SERVICE_URL", "http://localhost:8008")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{order_service_url}/health")
            checks["order_service"] = "ready" if response.status_code == 200 else "not_ready"
            if response.status_code != 200:
                overall_ready = False
    except Exception:
        checks["order_service"] = "not_ready"
        overall_ready = False
    
    response_data = {
        "ready": overall_ready,
        "checks": checks
    }
    
    # Return 503 if not ready
    if not overall_ready:
        return JSONResponse(
            status_code=503,
            content=response_data
        )
    
    return response_data


@app.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint.
    
    Simple check to verify the service is alive and responding.
    Used by container orchestrators for restart decisions.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


# Include API routers
app.include_router(payments_router, prefix="/api/v1", tags=["payments"])
app.include_router(payment_methods_router, prefix="/api/v1", tags=["payment-methods"])
app.include_router(webhooks_router, prefix="/api/v1", tags=["webhooks"])


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "code": "not_found",
            "details": {"path": str(request.url.path)},
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "code": "internal_error",
            "details": {"message": "An unexpected error occurred"},
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8009"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )
