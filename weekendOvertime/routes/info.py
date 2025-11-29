from flask import render_template
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

from ..db import get_db


def _china_day():
    try:
        if ZoneInfo:
            return datetime.now(ZoneInfo('Asia/Shanghai')).day
        else:
            return (datetime.utcnow() + timedelta(hours=8)).day
    except Exception:
        return datetime.utcnow().day


def info():
    db = get_db()
    today = _china_day()

    sat_rows = []
    sun_rows = []

    # defensive: column may not exist in older DBs
    try:
        sat_rows = db.execute(
            'SELECT s.id AS staff_id, s.name AS staff_name, d.name AS dept_name, sat.is_evection AS is_evection FROM sat JOIN staffs s ON sat.staff_id = s.id JOIN departments d ON s.department_id = d.id WHERE sat.updated_at = ? ORDER BY d.name, s.name',
            (today,)
        ).fetchall()
    except Exception:
        sat_rows = []

    try:
        sun_rows = db.execute(
            'SELECT s.id AS staff_id, s.name AS staff_name, d.name AS dept_name, sun.is_evection AS is_evection FROM sun JOIN staffs s ON sun.staff_id = s.id JOIN departments d ON s.department_id = d.id WHERE sun.updated_at = ? ORDER BY d.name, s.name',
            (today,)
        ).fetchall()
    except Exception:
        sun_rows = []

    # build department -> [names] mappings for normal and evection
    def build_maps(rows):
        normal = {}
        evection = {}
        for r in rows:
            dept = r['dept_name'] or '未知'
            name = r['staff_name']
            if r['is_evection']:
                evection.setdefault(dept, []).append(name)
            else:
                normal.setdefault(dept, []).append(name)
        return normal, evection

    sat_normal, sat_evec = build_maps(sat_rows)
    sun_normal, sun_evec = build_maps(sun_rows)

    return render_template('info.html', today=today, sat_normal=sat_normal, sat_evec=sat_evec, sun_normal=sun_normal, sun_evec=sun_evec)