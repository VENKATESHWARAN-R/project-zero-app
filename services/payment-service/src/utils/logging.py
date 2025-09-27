"""
Structured Logging Configuration for Payment Processing Service.

This module provides comprehensive logging setup with JSON formatting,
correlation IDs, and structured logging for observability and debugging.
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from functools import wraps

import structlog
from structlog.stdlib import LoggerFactory


# Context variables for request correlation
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class PaymentServiceLogger:
    """
    Structured logger for the Payment Service.
    
    Provides consistent logging with correlation IDs, structured data,
    and configurable output formats for development and production.
    """
    
    def __init__(self):
        self.logger = structlog.get_logger()
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure structured logging based on environment."""
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_format = os.getenv("LOG_FORMAT", "json").lower()
        
        # Configure standard library logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level, logging.INFO),
        )
        
        # Configure structlog processors
        processors = [
            structlog.contextvars.merge_contextvars,
            self._add_correlation_context,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
        ]
        
        if log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.extend([
                structlog.dev.ConsoleRenderer(colors=True),
            ])
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    def _add_correlation_context(self, logger, method_name, event_dict):
        """Add correlation context to log entries."""
        correlation_id = correlation_id_var.get()
        user_id = user_id_var.get()
        request_id = request_id_var.get()
        
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        if user_id:
            event_dict["user_id"] = user_id
        if request_id:
            event_dict["request_id"] = request_id
        
        # Add service context
        event_dict["service"] = "payment-service"
        event_dict["version"] = os.getenv("SERVICE_VERSION", "1.0.0")
        
        return event_dict
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current context."""
        correlation_id_var.set(correlation_id)
    
    def set_user_id(self, user_id: str):
        """Set user ID for current context."""
        user_id_var.set(user_id)
    
    def set_request_id(self, request_id: str):
        """Set request ID for current context."""
        request_id_var.set(request_id)
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID."""
        return correlation_id_var.get()
    
    def generate_correlation_id(self) -> str:
        """Generate new correlation ID."""
        correlation_id = str(uuid.uuid4())
        self.set_correlation_id(correlation_id)
        return correlation_id
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with structured data."""
        self.logger.critical(message, **kwargs)
    
    def log_payment_event(
        self,
        event_type: str,
        payment_id: str,
        amount: int,
        currency: str,
        status: str,
        **kwargs
    ):
        """Log payment-specific events with structured data."""
        self.info(
            f"Payment {event_type}",
            event_type=event_type,
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            status=status,
            **kwargs
        )
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """Log API request with performance metrics."""
        self.info(
            "API request processed",
            http_method=method,
            http_path=path,
            http_status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """Log database operations with performance metrics."""
        log_data = {
            "db_operation": operation,
            "db_table": table,
            **kwargs
        }
        
        if duration_ms is not None:
            log_data["db_duration_ms"] = duration_ms
        
        self.debug("Database operation", **log_data)
    
    def log_external_service_call(
        self,
        service_name: str,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """Log external service calls with performance and error tracking."""
        log_data = {
            "external_service": service_name,
            "external_endpoint": endpoint,
            "external_method": method,
            **kwargs
        }
        
        if status_code is not None:
            log_data["external_status_code"] = status_code
        if duration_ms is not None:
            log_data["external_duration_ms"] = duration_ms
        if error:
            log_data["external_error"] = error
        
        level = "error" if error or (status_code and status_code >= 400) else "info"
        getattr(self, level)("External service call", **log_data)
    
    def log_webhook_delivery(
        self,
        webhook_id: str,
        endpoint_url: str,
        event_type: str,
        success: bool,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """Log webhook delivery attempts with detailed tracking."""
        log_data = {
            "webhook_id": webhook_id,
            "webhook_endpoint": endpoint_url,
            "webhook_event_type": event_type,
            "webhook_success": success,
            **kwargs
        }
        
        if status_code is not None:
            log_data["webhook_status_code"] = status_code
        if duration_ms is not None:
            log_data["webhook_duration_ms"] = duration_ms
        if error:
            log_data["webhook_error"] = error
        
        level = "error" if not success else "info"
        getattr(self, level)("Webhook delivery", **log_data)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        **kwargs
    ):
        """Log security-related events for monitoring and alerting."""
        self.warning(
            f"Security event: {event_type}",
            security_event_type=event_type,
            security_severity=severity,
            security_details=details,
            **kwargs
        )


def log_function_call(include_args: bool = False, include_result: bool = False):
    """
    Decorator to log function calls with optional arguments and results.
    
    Args:
        include_args: Whether to log function arguments
        include_result: Whether to log function result
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger()
            func_name = f"{func.__module__}.{func.__qualname__}"
            
            log_data = {"function": func_name}
            if include_args:
                # Sanitize sensitive data
                safe_args = _sanitize_log_data({"args": args, "kwargs": kwargs})
                log_data.update(safe_args)
            
            start_time = datetime.utcnow()
            logger.debug("Function call started", **log_data)
            
            try:
                result = await func(*args, **kwargs)
                
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                log_data["duration_ms"] = duration_ms
                
                if include_result:
                    safe_result = _sanitize_log_data({"result": result})
                    log_data.update(safe_result)
                
                logger.debug("Function call completed", **log_data)
                return result
            
            except Exception as e:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                log_data.update({
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                logger.error("Function call failed", **log_data)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger()
            func_name = f"{func.__module__}.{func.__qualname__}"
            
            log_data = {"function": func_name}
            if include_args:
                safe_args = _sanitize_log_data({"args": args, "kwargs": kwargs})
                log_data.update(safe_args)
            
            start_time = datetime.utcnow()
            logger.debug("Function call started", **log_data)
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                log_data["duration_ms"] = duration_ms
                
                if include_result:
                    safe_result = _sanitize_log_data({"result": result})
                    log_data.update(safe_result)
                
                logger.debug("Function call completed", **log_data)
                return result
            
            except Exception as e:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                log_data.update({
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                logger.error("Function call failed", **log_data)
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _sanitize_log_data(data: Any) -> Any:
    """
    Sanitize sensitive data from log entries.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data with sensitive fields masked
    """
    sensitive_fields = {
        'password', 'token', 'secret', 'key', 'authorization',
        'card_number', 'cvv', 'ssn', 'credit_card', 'debit_card'
    }
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            if any(sensitive in key_lower for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = _sanitize_log_data(value)
        return sanitized
    
    elif isinstance(data, (list, tuple)):
        return [_sanitize_log_data(item) for item in data]
    
    elif isinstance(data, str) and len(data) > 16:
        # Check if string looks like a card number or token
        if data.replace(' ', '').replace('-', '').isdigit() and len(data.replace(' ', '').replace('-', '')) >= 13:
            return "***REDACTED***"
    
    return data


# Global logger instance
_logger_instance: Optional[PaymentServiceLogger] = None


def get_logger() -> PaymentServiceLogger:
    """Get singleton logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = PaymentServiceLogger()
    return _logger_instance


def configure_logging():
    """Configure logging for the application."""
    logger = get_logger()
    logger.info("Logging configured", log_level=os.getenv("LOG_LEVEL", "INFO"))


# Convenience functions for common logging patterns
def log_payment_created(payment_id: str, amount: int, currency: str, user_id: str, order_id: str):
    """Log payment creation event."""
    logger = get_logger()
    logger.log_payment_event(
        event_type="created",
        payment_id=payment_id,
        amount=amount,
        currency=currency,
        status="PENDING",
        order_id=order_id,
        user_id=user_id
    )


def log_payment_processed(payment_id: str, status: str, gateway_transaction_id: Optional[str] = None, failure_reason: Optional[str] = None):
    """Log payment processing completion."""
    logger = get_logger()
    log_data = {
        "event_type": "processed",
        "payment_id": payment_id,
        "status": status
    }
    
    if gateway_transaction_id:
        log_data["gateway_transaction_id"] = gateway_transaction_id
    if failure_reason:
        log_data["failure_reason"] = failure_reason
    
    logger.log_payment_event(**log_data)


def log_auth_failure(reason: str, user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """Log authentication failure for security monitoring."""
    logger = get_logger()
    logger.log_security_event(
        event_type="auth_failure",
        severity="medium",
        details={
            "reason": reason,
            "user_id": user_id,
            "ip_address": ip_address
        }
    )


def log_rate_limit_exceeded(user_id: Optional[str] = None, ip_address: Optional[str] = None, endpoint: Optional[str] = None):
    """Log rate limit exceeded for security monitoring."""
    logger = get_logger()
    logger.log_security_event(
        event_type="rate_limit_exceeded",
        severity="medium",
        details={
            "user_id": user_id,
            "ip_address": ip_address,
            "endpoint": endpoint
        }
    )


def log_suspicious_activity(activity_type: str, details: Dict[str, Any], severity: str = "high"):
    """Log suspicious activity for security monitoring."""
    logger = get_logger()
    logger.log_security_event(
        event_type="suspicious_activity",
        severity=severity,
        details={
            "activity_type": activity_type,
            **details
        }
    )
