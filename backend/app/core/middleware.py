import time
import uuid
import contextvars
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .logging import get_logger

logger = get_logger("middleware")

# ContextVar to store request ID for the current async task
request_id_var = contextvars.ContextVar("request_id", default=None)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and propagate a unique request/correlation ID."""
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID or use one from headers
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Set it in the context variable
        token = request_id_var.set(request_id)
        
        try:
            response: Response = await call_next(request)
            # Add it to the response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Reset the context variable
            request_id_var.reset(token)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request details and latency."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Capture request ID from context
        request_id = request_id_var.get()
        
        try:
            response = await call_next(request)
            
            process_time = (time.perf_counter() - start_time) * 1000
            
            # Log the request details
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} "
                f"({process_time:.2f}ms)",
                extra={"request_id": request_id}
            )
            
            return response
            
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            # Log unhandled exceptions with request ID
            logger.error(
                f"Unhandled Exception: {request.method} {request.url.path} - "
                f"FAILED ({process_time:.2f}ms) - Error: {str(e)}",
                exc_info=True,
                extra={"request_id": request_id}
            )
            raise
