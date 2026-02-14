"""Staff service for business logic."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
import logging

from .base import BaseService
from ..models import Staff, SubDepartment
from .department import DepartmentService

logger = logging.getLogger(__name__)

class StaffService(BaseService):
    """Service for staff-related business logic."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.department_service = DepartmentService(db)
    
    def get_staffs_by_department(self, department_id: int) -> List[Dict[str, Any]]:
        """Get staff by department with sub-department and overtime info."""
        try:
            # Validate department exists
            self.department_service.validate_department_exists(department_id)
            
            staffs = self.db.execute(
                text("""
                SELECT
                    s.id,
                    s.name,
                    s.department_id,
                    s.sub_department_id,
                    sd.name as sub_department_name,
                    sat.is_evection as sat_evection,
                    sun.is_evection as sun_evection
                FROM staffs s
                LEFT JOIN sub_departments sd ON s.sub_department_id = sd.id
                LEFT JOIN sat ON sat.staff_id = s.id
                LEFT JOIN sun ON sun.staff_id = s.id
                WHERE s.department_id = :dept_id
                ORDER BY s.name
                """),
                {"dept_id": department_id}
            ).fetchall()
            
            result = [staff._mapping for staff in staffs]
            logger.info(f"Retrieved {len(result)} staff for department {department_id}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("get_staffs_by_department", e, {"department_id": department_id})
            raise HTTPException(status_code=500, detail="Failed to retrieve staff")
    
    def get_sub_departments(self, department_id: int) -> List[SubDepartment]:
        """Get sub-departments for current department."""
        try:
            # Validate department exists
            self.department_service.validate_department_exists(department_id)
            
            sub_depts = self.db.query(SubDepartment).filter(
                SubDepartment.department_id == department_id
            ).all()
            
            logger.info(f"Retrieved {len(sub_depts)} sub-departments for department {department_id}")
            return sub_depts
            
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("get_sub_departments", e, {"department_id": department_id})
            raise HTTPException(status_code=500, detail="Failed to retrieve sub-departments")
    
    def add_staff(self, name: str, department_id: int, sub_department_id: Optional[int] = None) -> bool:
        """Add staff to department."""
        try:
            # Validate department exists
            self.department_service.validate_department_exists(department_id)
            
            # Validate sub-department if provided
            if sub_department_id:
                self._validate_sub_department_belongs_to_department(sub_department_id, department_id)
            
            # Check if staff already exists in the same department
            existing_staff = self.db.query(Staff).filter(
                Staff.name == name,
                Staff.department_id == department_id
            ).first()
            
            if existing_staff:
                self._log_error("add_staff_duplicate", ValueError("Duplicate staff"), {
                    "name": name,
                    "department_id": department_id
                })
                raise HTTPException(
                    status_code=409, 
                    detail=f"Staff '{name}' already exists in this department"
                )
            
            # Check if staff exists in other departments
            staff_in_other_dept = self.db.query(Staff).filter(Staff.name == name).first()
            
            if staff_in_other_dept:
                # Update existing staff's department and sub-department
                staff_in_other_dept.department_id = department_id
                staff_in_other_dept.sub_department_id = sub_department_id
                success = self._commit_or_rollback("staff_moved", {
                    "staff_name": name,
                    "old_department_id": staff_in_other_dept.department_id,
                    "new_department_id": department_id,
                    "sub_department_id": sub_department_id
                })
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to move staff")
            else:
                # Create new staff
                new_staff = Staff(
                    name=name,
                    department_id=department_id,
                    sub_department_id=sub_department_id
                )
                self.db.add(new_staff)
                success = self._commit_or_rollback("staff_added", {
                    "staff_name": name,
                    "department_id": department_id,
                    "sub_department_id": sub_department_id,
                    "staff_id": new_staff.id
                })
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to add staff")
            
            logger.info(f"Staff '{name}' added to department {department_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("add_staff", e, {
                "name": name,
                "department_id": department_id,
                "sub_department_id": sub_department_id
            })
            raise HTTPException(status_code=500, detail="Failed to add staff")
    
    def remove_staff(self, name: str, department_id: int) -> bool:
        """Remove staff from department."""
        try:
            # Validate department exists
            self.department_service.validate_department_exists(department_id)
            
            staff = self.db.query(Staff).filter(
                Staff.name == name,
                Staff.department_id == department_id
            ).first()
            
            if not staff:
                self._log_error("remove_staff_not_found", ValueError("Staff not found"), {
                    "name": name,
                    "department_id": department_id
                })
                raise HTTPException(status_code=404, detail="Staff not found in current department")
            
            # Log before deletion
            staff_id = staff.id
            sub_dept_id = staff.sub_department_id
            
            self.db.delete(staff)
            success = self._commit_or_rollback("staff_removed", {
                "staff_name": name,
                "staff_id": staff_id,
                "department_id": department_id,
                "sub_department_id": sub_dept_id
            })
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to remove staff")
            
            logger.info(f"Staff '{name}' removed from department {department_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self._log_error("remove_staff", e, {
                "name": name,
                "department_id": department_id
            })
            raise HTTPException(status_code=500, detail="Failed to remove staff")
    
    def _validate_sub_department_belongs_to_department(self, sub_dept_id: int, dept_id: int) -> None:
        """Validate that sub-department belongs to the specified department."""
        self._validate_id(sub_dept_id, "Sub-department ID")
        
        sub_dept = self.db.query(SubDepartment).filter(
            SubDepartment.id == sub_dept_id
        ).first()
        
        if not sub_dept or sub_dept.department_id != dept_id:
            raise HTTPException(
                status_code=400, 
                detail="Sub-department does not belong to the specified department"
            )
