from fastapi import APIRouter
from sqlalchemy.orm import Session
from typing import Dict, List

from ..database import get_db, get_china_day

router = APIRouter()

@router.get("/statistics")
async def get_info_statistics(db: Session = Depends(get_db)):
    """Get cross-department overtime statistics (like original info page)"""
    today = get_china_day()
    
    # Get Saturday overtime data
    sat_rows = []
    try:
        sat_rows = db.execute(
            """
            SELECT 
                s.id AS staff_id,
                s.name AS staff_name,
                d.name AS dept_name,
                sat.is_evection AS is_evection
            FROM sat 
            JOIN staffs s ON sat.staff_id = s.id
            JOIN departments d ON s.department_id = d.id
            ORDER BY d.name, s.name
            """
        ).fetchall()
    except Exception:
        sat_rows = []
    
    # Get Sunday overtime data
    sun_rows = []
    try:
        sun_rows = db.execute(
            """
            SELECT 
                s.id AS staff_id,
                s.name AS staff_name,
                d.name AS dept_name,
                sun.is_evection AS is_evection
            FROM sun 
            JOIN staffs s ON sun.staff_id = s.id
            JOIN departments d ON s.department_id = d.id
            ORDER BY d.name, s.name
            """
        ).fetchall()
    except Exception:
        sun_rows = []
    
    def build_department_maps(rows):
        """Build department -> [names] mappings for normal and evection"""
        normal = {}
        evection = {}
        for row in rows:
            dept = row["dept_name"] or "未知"
            name = row["staff_name"]
            if row["is_evection"]:
                evection.setdefault(dept, []).append(name)
            else:
                normal.setdefault(dept, []).append(name)
        return normal, evection
    
    sat_normal, sat_evec = build_department_maps(sat_rows)
    sun_normal, sun_evec = build_department_maps(sun_rows)
    
    return {
        "today": today,
        "sat": {
            "normal": sat_normal,
            "evection": sat_evec
        },
        "sun": {
            "normal": sun_normal,
            "evection": sun_evec
        }
    }
