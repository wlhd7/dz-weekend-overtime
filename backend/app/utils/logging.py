"""Logging utilities for the weekend overtime application."""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps

# Configure logging
def setup_logging():
    """Setup application logging with both file and console handlers."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Create specific logger for user operations
    user_logger = logging.getLogger("user_operations")
    user_handler = logging.FileHandler(log_dir / "user_operations.log")
    user_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    user_logger.addHandler(user_handler)
    user_logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

logger = setup_logging()
user_logger = logging.getLogger("user_operations")

def log_operation(operation: str, data: Dict[str, Any], user_id: Optional[str] = None):
    """Log user operations in JSON format for audit trail."""
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "user_id": user_id,
        "data": data
    }
    
    user_logger.info(json.dumps(log_entry))

def log_error(operation: str, error: Exception, context: Dict[str, Any] = None):
    """Log errors with context information."""
    
    error_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error(f"Error in {operation}: {error}", extra={"error_data": error_data})

def handle_database_errors(operation: str):
    """Decorator to handle database errors consistently."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(operation, e, {"args": str(args), "kwargs": str(kwargs)})
                raise
        return wrapper
    return decorator

def validate_and_log(operation: str, validator_func=None):
    """Decorator to validate input and log operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validate input if validator provided
                if validator_func:
                    validator_func(*args, **kwargs)
                
                # Log the operation
                log_operation(operation, {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs": list(kwargs.keys())
                })
                
                return func(*args, **kwargs)
            except Exception as e:
                log_error(operation, e)
                raise
        return wrapper
    return decorator
