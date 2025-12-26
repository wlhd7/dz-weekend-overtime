from flask import render_template, request, redirect, url_for
from weekendOvertime.db import get_db


def _dept_id_from_cookie():
    cookie_val = request.cookies.get('department')
    if not cookie_val:
        return None
    try:
        return int(cookie_val)
    except (TypeError, ValueError):
        return None


def preset_add():
    """Handle listing and adding presets for the current department.

    Supports GET: render the preset editor showing content/time presets for
    the department.

    Supports POST: form fields should include `preset_type` ("content" or
    "time") and `preset_name` (the preset text). Inserts into the
    corresponding `presets_content` or `presets_time` table.
    """
    dept_id = _dept_id_from_cookie()
    if dept_id is None:
        return redirect(url_for('select_department'))

    db = get_db()

    if request.method == 'POST':
        ptype = request.form.get('preset_type')
        preset_name = request.form.get('preset_name')
        if not ptype or not preset_name:
            return redirect(url_for('preset_add'))

        table = 'presets_content' if ptype == 'content' else 'presets_time'
        try:
            db.execute(f'INSERT OR IGNORE INTO {table} (preset_name, department_id) VALUES (?, ?)', (preset_name, dept_id))
            db.commit()
        except Exception:
            db.rollback()
        return redirect(url_for('preset_add'))

    # GET: show existing presets for this department
    contents = db.execute('SELECT id, preset_name FROM presets_content WHERE department_id = ? ORDER BY id DESC', (dept_id,)).fetchall()
    times = db.execute('SELECT id, preset_name FROM presets_time WHERE department_id = ? ORDER BY id DESC', (dept_id,)).fetchall()
    return render_template('preset.html', contents=contents, times=times)


def preset_delete():
    """Delete a preset for the current department.

    Expects POST form with `preset_type` ("content" or "time") and
    `preset_id` (id of the preset to delete).
    """
    dept_id = _dept_id_from_cookie()
    if dept_id is None:
        return redirect(url_for('select_department'))

    preset_id = request.form.get('preset_id')
    ptype = request.form.get('preset_type')
    if not preset_id or not ptype:
        return redirect(url_for('preset_add'))

    table = 'presets_content' if ptype == 'content' else 'presets_time'
    db = get_db()
    try:
        db.execute(f'DELETE FROM {table} WHERE id = ? AND department_id = ?', (preset_id, dept_id))
        db.commit()
    except Exception:
        db.rollback()

    return redirect(url_for('preset_add'))