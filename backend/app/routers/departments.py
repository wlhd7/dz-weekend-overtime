from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import Department, DepartmentOperation
from ..services.department import upsert_department_operation, delete_department_operation
from ..services.overtime import get_date_by_token

router = APIRouter()

# Pydantic models
class DepartmentResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class DepartmentSelectRequest(BaseModel):
    department_id: int

class ConfirmStatusResponse(BaseModel):
    is_confirmed: bool

@router.get("/", response_model=List[DepartmentResponse])
@router.get("", response_model=List[DepartmentResponse])
async def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(Department).all()
    return departments

@router.get("/current", response_model=DepartmentResponse)
async def get_current_department(
    department: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Get current department from cookie"""
    if not department:
        raise HTTPException(status_code=400, detail="Department cookie not found")
    
    try:
        dept_id = int(department)
        if dept_id <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid department cookie")
    
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return dept

@router.post("/select")
async def select_department(
    request: DepartmentSelectRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Set department cookie (1-year expiry)"""
    # Validate department exists
    department = db.query(Department).filter(Department.id == request.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Set cookie with 1-year expiry
    response.set_cookie(
        key="department",
        value=str(request.department_id),
        max_age=365 * 24 * 3600,  # 1 year
        httponly=True,
        samesite="lax"
    )
    
    return {"success": True, "message": "Department selected"}

@router.post("/confirm")
async def confirm_department_data(
    department: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Confirm department data for today and upcoming weekend"""
    if not department:
        raise HTTPException(status_code=400, detail="Department cookie not found")
    
    dept = db.query(Department).filter(Department.id == int(department)).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # 1. 记录当天的操作
    upsert_department_operation(db, dept.name, date.today())
    
    # 2. 同时记录本周六和周日的操作，确保报表能正确导出
    # 规范要求确认操作针对整个加班周期
    for token in ["sat", "sun"]:
        target_date = get_date_by_token(token)
        upsert_department_operation(db, dept.name, target_date)
    
    return {"success": True, "message": "Data confirmed"}

@router.post("/unconfirm")
async def unconfirm_department_data(
    department: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Unconfirm department data for today and upcoming weekend"""
    if not department:
        raise HTTPException(status_code=400, detail="Department cookie not found")
    
    dept = db.query(Department).filter(Department.id == int(department)).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # 1. 删除当天的操作记录
    delete_department_operation(db, dept.name, date.today())
    
    # 2. 同时删除本周六和周日的操作记录
    for token in ["sat", "sun"]:
        target_date = get_date_by_token(token)
        delete_department_operation(db, dept.name, target_date)
    
    return {"success": True, "message": "Confirmation revoked"}

@router.get("/confirm-status", response_model=ConfirmStatusResponse)
async def get_confirm_status(
    department: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Check if department has confirmed data for today"""
    if not department:
        return {"is_confirmed": False}
    
    try:
        dept_id = int(department)
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if not dept:
            return {"is_confirmed": False}
        
        # Check for operation record today
        op = db.query(DepartmentOperation).filter(
            DepartmentOperation.department_name == dept.name,
            DepartmentOperation.date == date.today()
        ).first()
        
        return {"is_confirmed": op is not None}
    except (TypeError, ValueError):
        return {"is_confirmed": False}
