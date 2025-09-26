import json
import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional
from uuid import uuid4

from .config import settings

# Context variable for correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelatedJSONFormatter(logging.Formatter):
    """JSON formatter that includes correlation IDs and structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with correlation ID."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        correlation_id = correlation_id_ctx.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add extra fields from the log record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure structured logging for the service."""
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create formatter
    formatter = CorrelatedJSONFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger.addHandler(console_handler)

    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.environment == "development" else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for the current context."""
    if correlation_id is None:
        correlation_id = str(uuid4())

    correlation_id_ctx.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id_ctx.get()


def log_with_extra(logger: logging.Logger, level: int, message: str, **extra: Any) -> None:
    """Log message with extra fields."""
    logger.log(level, message, extra={"extra_fields": extra})