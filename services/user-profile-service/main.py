#!/usr/bin/env python3
"""
User Profile Service - Main Application Entry Point

This is the main entry point for the User Profile Service.
It can be run directly with Python or via uvicorn.
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config import get_settings
from src.app import app

# Initialize settings
settings = get_settings()

# Configure logging for main module
logger = logging.getLogger(__name__)


def main():
    """Main entry point for running the application."""
    logger.info(f"Starting {settings.service_name} v{settings.version}")

    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
        access_log=True,
        server_header=False,  # Don't expose server header for security
        date_header=False     # Don't expose date header for security
    )


if __name__ == "__main__":
    main()