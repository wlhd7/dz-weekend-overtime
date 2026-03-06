from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict
from datetime import date, timedelta

from ..database import get_db, get_china_day
from ..models import DepartmentOperation

router = APIRouter()

DAY_TOKENS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@router.get("/statistics")
async def get_info_statistics(db: Session = Depends(get_db)):
    """Get cross-department overtime statistics (like original info page)"""
    today_num = get_china_day()
    today_date = date.today()

    # 获取所有日期的操作记录 (为了简单，我们取最近 7 天的)
    # 或者我们只支持“今天”的过滤，因为滚动周的其他日期可能已经由于“今天”的操作而被确认。
    # 根据需求，“若某部门当天未进行任何操作”，这暗示是特定日期的。
    
    # 查找最近 7 天有操作记录的 (部门, 日期)
    active_ops = db.query(DepartmentOperation.department_name, DepartmentOperation.date).all()
    # 转换为集合提高查询效率: {(dept_name, date), ...}
    active_set = {(op.department_name, op.date) for op in active_ops}

    # 计算 mon, tue 等对应的具体日期
    # 注意：这里的逻辑要严谨。由于是“滚动周”，我们需要知道每个 token 对应的 date。
    # 假设当前日期为 today_date, 对应的 weekday 为 today_date.weekday() (0-6)
    current_weekday = today_date.weekday()
    day_token_to_date = {}
    tokens = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    for i, token in enumerate(tokens):
        # 偏移量 = 目标星期几 - 当前星期几
        # 这里假设 token 对应的是“当前这周”的日期。
        diff = i - current_weekday
        day_token_to_date[token] = today_date + timedelta(days=diff)

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
        days = {day: {"normal": {}, "evection": {}} for day in tokens}
        for row in rows:
            row_dict = row._mapping
            dept = row_dict["dept_name"] or "未知"
            name = row_dict["staff_name"]
            for day in tokens:
                target_date = day_token_to_date[day]
                # 过滤逻辑：如果该部门在 target_date 没有操作记录，则跳过
                if (dept, target_date) not in active_set:
                    continue
                
                status = row_dict[day]
                if status == "bg-2":
                    days[day]["normal"].setdefault(dept, []).append(name)
                elif status == "bg-3":
                    days[day]["evection"].setdefault(dept, []).append(name)
        return days

    return {"today": today_num, "days": build_day_maps(rows)}
