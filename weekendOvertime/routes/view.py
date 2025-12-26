from flask import render_template, request, redirect, url_for, jsonify
from weekendOvertime.db import get_db


def _dept_id_from_cookie():
    cookie_val = request.cookies.get('department')
    if not cookie_val:
        return None
    try:
        return int(cookie_val)
    except (TypeError, ValueError):
        return None


def _parse_time_presets(rows):
    # rows: iterable of row objects with 'preset_name' like '09:00-18:00'
    begins = []
    ends = []
    for r in rows:
        if not r['preset_name']:
            continue
        parts = r['preset_name'].split('-', 1)
        if len(parts) == 2:
            b, e = parts[0].strip(), parts[1].strip()
            begins.append(b)
            ends.append(e)
    # unique preserve order
    def uniq(seq):
        seen = set(); out = []
        for x in seq:
            if x and x not in seen:
                seen.add(x); out.append(x)
        return out

    return uniq(begins), uniq(ends)


def view():
    """GET: render list of staff with their sat/sun values and presets.

    POST (JSON): update `content`, `begin_time`, `end_time` for a given
    `staff_id` and `day` ('sat'|'sun'). Expects JSON:
      { staff_id: int, day: 'sat'|'sun', content: str, begin_time: str, end_time: str }
    Returns JSON {ok: true} on success.
    """
    dept_id = _dept_id_from_cookie()
    if dept_id is None:
        return redirect(url_for('select_department'))

    db = get_db()

    # Handle JSON updates from the client
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        staff_id = data.get('staff_id')
        day = data.get('day')
        content = data.get('content', '')
        begin_time = data.get('begin_time', '')
        end_time = data.get('end_time', '')

        if not staff_id or day not in ('sat', 'sun'):
            return jsonify(ok=False, error='invalid payload'), 400

        try:
            # preserve existing is_evection value when present
            existing = db.execute(f'SELECT is_evection FROM {day} WHERE staff_id = ?', (staff_id,)).fetchone()
            is_evection = existing['is_evection'] if existing else 0

            db.execute(f'DELETE FROM {day} WHERE staff_id = ?', (staff_id,))
            db.execute(
                f'INSERT INTO {day} (staff_id, is_evection, content, begin_time, end_time) VALUES (?, ?, ?, ?, ?)',
                (staff_id, is_evection, content or '', begin_time or '', end_time or '')
            )
            db.commit()
            return jsonify(ok=True)
        except Exception as e:
            db.rollback()
            return jsonify(ok=False, error=str(e)), 500

    # GET: load staffs that have sat/sun rows and the presets for this dept
    rows = db.execute(
        """
        SELECT s.id, s.name,
               sat.is_evection AS sat_evection, sat.content AS sat_content, sat.begin_time AS sat_begin_time, sat.end_time AS sat_end_time,
               sun.is_evection AS sun_evection, sun.content AS sun_content, sun.begin_time AS sun_begin_time, sun.end_time AS sun_end_time
        FROM staffs s
        LEFT JOIN sat ON sat.staff_id = s.id
        LEFT JOIN sun ON sun.staff_id = s.id
        WHERE s.department_id = ? AND (sat.staff_id IS NOT NULL OR sun.staff_id IS NOT NULL)
        ORDER BY s.name
        """,
        (dept_id,)
    ).fetchall()

    contents = db.execute('SELECT id, preset_name FROM presets_content WHERE department_id = ? ORDER BY id DESC', (dept_id,)).fetchall()
    times = db.execute('SELECT id, preset_name FROM presets_time WHERE department_id = ? ORDER BY id DESC', (dept_id,)).fetchall()
    begin_options, end_options = _parse_time_presets(times)

    return render_template('view.html', staffs=rows, contents=contents, begin_options=begin_options, end_options=end_options)
