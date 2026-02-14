"""Department service for business logic."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging

from .base import BaseService
from ..models import Department
from ..utils.logging import logger

class DepartmentService(BaseService):
    """Service for department-related business logic."""
    
    def get_all_departments(self) -> List[Department]:
        """Get all departments."""
        try:
            departments = self.db.query(Department).all()
            logger.info(f"Retrieved {len(departments)} departments")
            return departments
        except Exception as e:
            self._log_error("get_all_departments", e)
            raise HTTPException(status_code=500, detail="Failed to retrieve departments")
    
    def get_department_by_id(self, department_id: int) -> Department:
        """Get department by ID."""
        try:
            department = self._get_by_id(Department, department_id, "Department")
            logger.info(f"Retrieved department: {department.name} (ID: {department_id})")
            return department
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("get_department_by_id", e, {"department_id": department_id})
            raise HTTPException(status_code=500, detail="Failed to retrieve department")
    
    def validate_department_exists(self, department_id: int) -> Department:
        """Validate that department exists and return it."""
        try:
            self._validate_id(department_id, "Department ID")
            department = self.db.query(Department).filter(Department.id == department_id).first()
            if not department:
                raise HTTPException(status_code=404, detail="Department not found")
            return department
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("validate_department_exists", e, {"department_id": department_id})
            raise HTTPException(status_code=500, detail="Failed to validate department")
    
    def extract_department_from_cookie(self, department_cookie: Optional[str]) -> int:
        """Extract and validate department ID from cookie."""
        if not department_cookie:
            raise HTTPException(status_code=400, detail="Department cookie not found")
        
        try:
            dept_id = int(department_cookie)
            if dept_id <= 0:
                raise ValueError()
            
            # Validate department exists
            self.validate_department_exists(dept_id)
            return dept_id
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid department cookie")
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("extract_department_from_cookie", e, {"cookie": department_cookie})
            raise HTTPException(status_code=500, detail="Failed to process department cookie")
