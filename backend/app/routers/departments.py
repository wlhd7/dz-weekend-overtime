from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Department

router = APIRouter()

# Pydantic models
class DepartmentResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class DepartmentSelectRequest(BaseModel):
    department_id: int

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
