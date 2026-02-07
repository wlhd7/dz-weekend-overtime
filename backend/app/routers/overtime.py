from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from ..database import get_db
from ..models import Staff, Sat, Sun

router = APIRouter()

# Pydantic models
class OvertimeToggleRequest(BaseModel):
    staff_id: int
    status: str  # "bg-1", "bg-2", "bg-3"
    day: str = "sat"  # "sat" or "sun"

class OvertimeStatusResponse(BaseModel):
    staff_id: int
    sat_evection: Optional[bool] = None
    sun_evection: Optional[bool] = None
    
    class Config:
        from_attributes = True

def get_department_from_cookie(department: str = Depends(lambda: None)) -> int:
    """Extract and validate department from cookie (simplified for FastAPI)"""
    # In FastAPI, we'll handle this differently or use header
    # For now, assume department is passed in headers or we'll implement proper auth
    pass

@router.post("/toggle")
async def toggle_overtime_status(
    request: OvertimeToggleRequest,
    db: Session = Depends(get_db)
):
    """Toggle staff overtime status (bg-1: none, bg-2: internal, bg-3: business trip)"""
    
    # Validate inputs
    try:
        staff_id = int(request.staff_id)
        if staff_id <= 0:
            raise ValueError("Invalid staff_id")
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid staff_id")
    
    if request.day not in ("sat", "sun"):
        raise HTTPException(status_code=400, detail="Invalid day")
    
    if request.status not in ("bg-1", "bg-2", "bg-3"):
        raise HTTPException(status_code=400, detail="Invalid status")
    
    try:
        # Get staff to validate exists
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        
        # Handle status changes
        if request.status == "bg-1":
            # Remove overtime record
            if request.day == "sat":
                db.query(Sat).filter(Sat.staff_id == staff_id).delete()
            else:  # sun
                db.query(Sun).filter(Sun.staff_id == staff_id).delete()
        
        else:
            # Set overtime status
            is_evection = 1 if request.status == "bg-3" else 0
            
            # Remove existing record first (to prevent duplicates)
            if request.day == "sat":
                db.query(Sat).filter(Sat.staff_id == staff_id).delete()
                new_record = Sat(staff_id=staff_id, is_evection=is_evection)
            else:  # sun
                db.query(Sun).filter(Sun.staff_id == staff_id).delete()
                new_record = Sun(staff_id=staff_id, is_evection=is_evection)
            
            db.add(new_record)
        
        db.commit()
        return {"success": True, "message": "Status updated successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=List[OvertimeStatusResponse])
async def get_overtime_status(
    dept_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get current overtime status for staff in department"""
    if not dept_id:
        raise HTTPException(status_code=400, detail="Department ID required")
    
    staffs = db.execute(
        text("""
        SELECT
            s.id as staff_id,
            sat.is_evection as sat_evection,
            sun.is_evection as sun_evection
        FROM staffs s
        LEFT JOIN sat ON sat.staff_id = s.id
        LEFT JOIN sun ON sun.staff_id = s.id
        WHERE s.department_id = :dept_id
        ORDER BY s.name
        """),
        {"dept_id": dept_id}
    ).fetchall()
    
    return [staff._mapping for staff in staffs]
