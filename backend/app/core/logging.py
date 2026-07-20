import logging
import sys
import json
import time
from typing import Any, Dict
from .config import settings

def setup_logging():
    """Configure centralized logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Add correlation ID filter
    from .middleware import request_id_var
    
    class CorrelationIdFilter(logging.Filter):
        def filter(self, record):
            record.request_id = request_id_var.get()
            return True
            
    handler.addFilter(CorrelationIdFilter())
    
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        # Standard text format: 2024-02-28 14:00:00 [INFO] [req-id] module.function:L123 - message
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s.%(funcName)s:L%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Suppress noisy logs from third-party libraries
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]
    
    logging.info(f"Logging initialized (Level: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT})")

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add correlation ID if present in the record (from middleware)
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
            
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def get_logger(name: str):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
