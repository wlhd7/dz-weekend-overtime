"""Base service class for common functionality."""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..utils import log_operation, log_error

logger = logging.getLogger(__name__)

class BaseService:
    """Base service class with common database operations and error handling."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _commit_or_rollback(self, operation: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Handle database commit with error handling and logging."""
        try:
            self.db.commit()
            if context:
                log_operation(operation, context)
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            log_error(f"{operation}_db_error", e, context or {})
            logger.error(f"Database error in {operation}: {str(e)}")
            return False
    
    def _log_error(self, operation: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        log_error(operation, error, context or {})
        logger.error(f"Error in {operation}: {str(error)}")
    
    def _validate_id(self, id_value: int, field_name: str = "ID") -> None:
        """Validate ID is positive integer."""
        if not isinstance(id_value, int) or id_value <= 0:
            raise ValueError(f"Invalid {field_name}: must be positive integer")
    
    def _get_by_id(self, model_class: Any, id_value: int, context: Optional[str] = None):
        """Generic method to get entity by ID."""
        self._validate_id(id_value, f"{context or model_class.__name__} ID")
        entity = self.db.query(model_class).filter(model_class.id == id_value).first()
        if not entity:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, 
                detail=f"{context or model_class.__name__} not found"
            )
        return entity
