from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict

from ..database import get_db, get_china_day

router = APIRouter()

DAY_TOKENS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@router.get("/statistics")
async def get_info_statistics(db: Session = Depends(get_db)):
    """Get cross-department overtime statistics (like original info page)"""
    today = get_china_day()

    rows = db.execute(
        text("""
        SELECT
            s.id AS staff_id,
            s.name AS staff_name,
            d.name AS dept_name,
            COALESCE(ow.mon, 'bg-1') AS mon,
            COALESCE(ow.tue, 'bg-1') AS tue,
            COALESCE(ow.wed, 'bg-1') AS wed,
            COALESCE(ow.thu, 'bg-1') AS thu,
            COALESCE(ow.fri, 'bg-1') AS fri,
            COALESCE(ow.sat, 'bg-1') AS sat,
            COALESCE(ow.sun, 'bg-1') AS sun
        FROM staffs s
        JOIN departments d ON s.department_id = d.id
        LEFT JOIN overtime_weeks ow ON ow.staff_id = s.id
        ORDER BY d.name, s.name
        """)
    ).fetchall()

    def build_day_maps(rows) -> Dict[str, Dict[str, Dict[str, list]]]:
        days = {day: {"normal": {}, "evection": {}} for day in DAY_TOKENS}
        for row in rows:
            row_dict = row._mapping
            dept = row_dict["dept_name"] or "未知"
            name = row_dict["staff_name"]
            for day in DAY_TOKENS:
                status = row_dict[day]
                if status == "bg-2":
                    days[day]["normal"].setdefault(dept, []).append(name)
                elif status == "bg-3":
                    days[day]["evection"].setdefault(dept, []).append(name)
        return days

    return {"today": today, "days": build_day_maps(rows)}
