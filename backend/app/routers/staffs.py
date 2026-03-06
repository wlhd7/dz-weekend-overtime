from fastapi import APIRouter, HTTPException, Depends, Cookie
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Any

from ..database import get_db
from ..models import Staff, SubDepartment, OvertimeWeek, Department
from ..services.department import upsert_department_operation
from datetime import date

router = APIRouter()


# Pydantic models
class StaffResponse(BaseModel):
    id: int
    name: str
    department_id: int
    sub_department_id: Optional[int] = None
    sub_department_name: Optional[str] = None
    mon: str
    tue: str
    wed: str
    thu: str
    fri: str
    sat: str
    sun: str

    class Config:
        from_attributes = True


class SubDepartmentResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StaffAddRequest(BaseModel):
    name: str
    sub_department_id: Optional[int] = None


class StaffRemoveRequest(BaseModel):
    name: str


def ensure_overtime_week(db: Session, staff_id: Any) -> None:
    existing = db.query(OvertimeWeek).filter(OvertimeWeek.staff_id == staff_id).first()
    if not existing:
        db.add(OvertimeWeek(staff_id=staff_id))


def get_department_from_cookie(department: Optional[str] = Cookie(None)) -> int:
    """Extract and validate department from cookie"""
    if not department:
        raise HTTPException(status_code=400, detail="Department cookie not found")

    try:
        dept_id = int(department)
        if dept_id <= 0:
            raise ValueError()
        return dept_id
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid department cookie")


@router.get("/", response_model=List[StaffResponse])
@router.get("", response_model=List[StaffResponse])
async def get_staffs(
    dept_id: int = Depends(get_department_from_cookie), db: Session = Depends(get_db)
):
    """Get staff by department with sub-department and overtime info"""
    staffs = db.execute(
        text("""
        SELECT
            s.id,
            s.name,
            s.department_id,
            s.sub_department_id,
            sd.name as sub_department_name,
            COALESCE(ow.mon, 'bg-1') as mon,
            COALESCE(ow.tue, 'bg-1') as tue,
            COALESCE(ow.wed, 'bg-1') as wed,
            COALESCE(ow.thu, 'bg-1') as thu,
            COALESCE(ow.fri, 'bg-1') as fri,
            COALESCE(ow.sat, 'bg-1') as sat,
            COALESCE(ow.sun, 'bg-1') as sun
        FROM staffs s
        LEFT JOIN sub_departments sd ON s.sub_department_id = sd.id
        LEFT JOIN overtime_weeks ow ON ow.staff_id = s.id
        WHERE s.department_id = :dept_id
        ORDER BY s.name
        """),
        {"dept_id": dept_id},
    ).fetchall()

    return [staff._mapping for staff in staffs]


@router.get("/sub-departments", response_model=List[SubDepartmentResponse])
async def get_sub_departments(
    dept_id: int = Depends(get_department_from_cookie), db: Session = Depends(get_db)
):
    """Get sub-departments for current department"""
    sub_depts = (
        db.query(SubDepartment).filter(SubDepartment.department_id == dept_id).all()
    )
    return sub_depts


@router.post("/add")
async def add_staff(
    request: StaffAddRequest,
    dept_id: int = Depends(get_department_from_cookie),
    db: Session = Depends(get_db),
):
    """Add staff to current department"""
    try:
        # Check if staff already exists
        existing_staff = db.query(Staff).filter(Staff.name == request.name).first()

        if existing_staff:
            # Update existing staff's department and sub-department
            setattr(existing_staff, "department_id", dept_id)
            setattr(existing_staff, "sub_department_id", request.sub_department_id)
            ensure_overtime_week(db, existing_staff.id)
            db.commit()
        else:
            # Create new staff
            new_staff = Staff(
                name=request.name,
                department_id=dept_id,
                sub_department_id=request.sub_department_id,
            )
            db.add(new_staff)
            db.flush()
            ensure_overtime_week(db, new_staff.id)
            db.commit()

        # Update operation record
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if dept:
            upsert_department_operation(db, dept.name, date.today())

        return {"success": True, "message": "Staff added successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove")
async def remove_staff(
    request: StaffRemoveRequest,
    dept_id: int = Depends(get_department_from_cookie),
    db: Session = Depends(get_db),
):
    """Remove staff from current department"""
    try:
        staff = (
            db.query(Staff)
            .filter(Staff.name == request.name, Staff.department_id == dept_id)
            .first()
        )

        if not staff:
            raise HTTPException(
                status_code=404, detail="Staff not found in current department"
            )

        db.delete(staff)
        db.commit()

        # Update operation record
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if dept:
            upsert_department_operation(db, dept.name, date.today())

        return {"success": True, "message": "Staff removed successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
