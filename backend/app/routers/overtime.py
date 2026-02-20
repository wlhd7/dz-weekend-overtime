from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from ..database import get_db
from ..services import OvertimeService

router = APIRouter()

DAY_TOKENS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


# Pydantic models
class OvertimeToggleRequest(BaseModel):
    staff_id: int
    status: str  # "bg-1", "bg-2", "bg-3"
    day: str  # "mon" through "sun"


class OvertimeStatusResponse(BaseModel):
    staff_id: int
    mon: str
    tue: str
    wed: str
    thu: str
    fri: str
    sat: str
    sun: str

    class Config:
        from_attributes = True


@router.post("/toggle")
async def toggle_overtime_status(
    request: OvertimeToggleRequest, db: Session = Depends(get_db)
):
    """Toggle staff overtime status (bg-1: none, bg-2: internal, bg-3: business trip)"""

    # Validate inputs
    try:
        staff_id = int(request.staff_id)
        if staff_id <= 0:
            raise ValueError("Invalid staff_id")
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid staff_id")

    if request.day not in DAY_TOKENS:
        raise HTTPException(status_code=400, detail="Invalid day")

    if request.status not in ("bg-1", "bg-2", "bg-3"):
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        service = OvertimeService(db)
        success = service.toggle_staff_status(staff_id, request.status, request.day)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update status")
        return {"success": True, "message": "Status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=List[OvertimeStatusResponse])
async def get_overtime_status(
    dept_id: Optional[int] = None, db: Session = Depends(get_db)
):
    """Get current overtime status for staff in department"""
    if not dept_id:
        raise HTTPException(status_code=400, detail="Department ID required")

    staffs = db.execute(
        text("""
        SELECT
            s.id as staff_id,
            COALESCE(ow.mon, 'bg-1') as mon,
            COALESCE(ow.tue, 'bg-1') as tue,
            COALESCE(ow.wed, 'bg-1') as wed,
            COALESCE(ow.thu, 'bg-1') as thu,
            COALESCE(ow.fri, 'bg-1') as fri,
            COALESCE(ow.sat, 'bg-1') as sat,
            COALESCE(ow.sun, 'bg-1') as sun
        FROM staffs s
        LEFT JOIN overtime_weeks ow ON ow.staff_id = s.id
        WHERE s.department_id = :dept_id
        ORDER BY s.name
        """),
        {"dept_id": dept_id},
    ).fetchall()

    return [staff._mapping for staff in staffs]
