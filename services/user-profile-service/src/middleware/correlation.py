from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import logging

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs for distributed tracing."""

    def __init__(self, app, header_name: str = "X-Correlation-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next):
        # Get correlation ID from headers or generate new one
        correlation_id = (
            request.headers.get(self.header_name.lower()) or
            request.headers.get("x-request-id") or
            request.headers.get("x-trace-id") or
            str(uuid.uuid4())
        )

        # Store correlation ID in request state
        request.state.correlation_id = correlation_id

        # Add to logging context
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.correlation_id = correlation_id
            return record

        logging.setLogRecordFactory(record_factory)

        try:
            # Process the request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers[self.header_name] = correlation_id

            return response

        finally:
            # Restore original log record factory
            logging.setLogRecordFactory(old_factory)


def get_correlation_id(request: Request) -> str:
    """Get correlation ID from request state."""
    return getattr(request.state, 'correlation_id', str(uuid.uuid4()))