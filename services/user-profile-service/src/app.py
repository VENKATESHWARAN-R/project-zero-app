from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
import logging.config

from .config import get_settings
from .database import engine, Base
from .middleware import setup_middleware
from .middleware.error_handler import setup_exception_handlers
from .routers import health, profiles, addresses, preferences, activity, admin

# Initialize settings
settings = get_settings()

# Configure logging
logging.config.dictConfig(settings.get_log_config())
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="User Profile Service API",
    description="User profile management service for Project Zero App e-commerce platform",
    version=settings.version,
    debug=settings.debug,
    docs_url=None,  # Disable default docs URL for custom implementation
    redoc_url=None,  # Disable default redoc URL for custom implementation
    openapi_url="/openapi.json"
)

# Setup middleware
setup_middleware(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health.router)
app.include_router(profiles.router)
app.include_router(addresses.router)
app.include_router(preferences.router)
app.include_router(activity.router)

# Include admin router only if enabled
if settings.enable_admin_endpoints:
    app.include_router(admin.router)
    logger.info("Admin endpoints enabled")
else:
    logger.info("Admin endpoints disabled")


# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation."""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
    )


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add custom metadata
    openapi_schema["info"]["contact"] = {
        "name": "Project Zero Team",
        "email": "support@projectzero.example.com"
    }

    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }

    # Add servers
    openapi_schema["servers"] = [
        {
            "url": f"http://localhost:{settings.port}",
            "description": "Local development server"
        },
        {
            "url": "https://api.projectzero.example.com/profile",
            "description": "Production server"
        }
    ]

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.service_name} v{settings.version}")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(f"Database: {settings.get_database_url()}")
    logger.info(f"Auth Service: {settings.auth_service_url}")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

    logger.info(f"Application started successfully on {settings.host}:{settings.port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"Shutting down {settings.service_name}")

    # Perform cleanup if needed
    logger.info("Application shutdown complete")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.service_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health"
    }