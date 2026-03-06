"""Department service for business logic."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging

from .base import BaseService
from ..models import Department
from ..utils.logging import logger

from datetime import date, datetime
from ..models import Department, DepartmentOperation

def upsert_department_operation(db: Session, department_name: str, op_date: date):
    """
    更新或插入部门在特定日期的操作记录。
    会更新 last_updated 时间戳。
    """
    try:
        # 尝试查找已存在的记录
        db_op = db.query(DepartmentOperation).filter(
            DepartmentOperation.department_name == department_name,
            DepartmentOperation.date == op_date
        ).first()
        
        if db_op:
            # 更新最后操作时间
            db_op.last_updated = datetime.now()
        else:
            # 创建新记录
            db_op = DepartmentOperation(
                department_name=department_name,
                date=op_date,
                last_updated=datetime.now()
            )
            db.add(db_op)
        
        db.commit()
        db.refresh(db_op)
        return db_op
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to upsert department operation for {department_name} on {op_date}: {e}")
        raise e

def ensure_department_operation(db: Session, department_name: str, op_date: date):
    """
    确保部门在特定日期的操作记录存在。
    如果记录已存在，则不进行任何操作（不更新 last_updated）。
    """
    try:
        db_op = db.query(DepartmentOperation).filter(
            DepartmentOperation.department_name == department_name,
            DepartmentOperation.date == op_date
        ).first()
        
        if not db_op:
            db_op = DepartmentOperation(
                department_name=department_name,
                date=op_date,
                last_updated=datetime.now()
            )
            db.add(db_op)
            db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to ensure department operation for {department_name} on {op_date}: {e}")
        raise e

def delete_department_operation(db: Session, department_name: str, op_date: date):
    """
    删除部门在特定日期的操作记录。
    """
    try:
        db.query(DepartmentOperation).filter(
            DepartmentOperation.department_name == department_name,
            DepartmentOperation.date == op_date
        ).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete department operation for {department_name} on {op_date}: {e}")
        raise e

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
