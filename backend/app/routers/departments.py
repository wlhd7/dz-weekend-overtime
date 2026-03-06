from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import Department, DepartmentOperation
from ..services.department import upsert_department_operation, delete_department_operation, ensure_department_operation
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
    # 1. 记录当天的操作（更新 last_updated，锁定今天的按钮）
    upsert_department_operation(db, dept.name, date.today())

    # 2. 确保本周六和周日的操作记录存在，确保报表能正确导出
    # 使用 ensure 而不是 upsert，这样不会更新 last_updated，第二天按钮会自动重置
    for token in ["sat", "sun"]:
        target_date = get_date_by_token(token)
        ensure_department_operation(db, dept.name, target_date)

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
        
        # 核心逻辑修改：只有当记录存在，且最后更新时间也是今天时，才算作“已确认”
        # 这样即便昨天操作时提前生成了今天的记录，今天进来由于 last_updated 是昨天，按钮也会重置。
        is_confirmed = False
        if op and op.last_updated:
            is_confirmed = op.last_updated.date() == date.today()
        
        return {"is_confirmed": is_confirmed}
    except (TypeError, ValueError):
        return {"is_confirmed": False}
