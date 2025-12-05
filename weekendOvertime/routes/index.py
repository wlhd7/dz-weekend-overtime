from flask import render_template, request, redirect, url_for, make_response
from ..db import get_db


def index():
    cookie_val = request.cookies.get('department')
    if not cookie_val:
        return redirect(url_for('select_department'))

    # cookie now stores department id (as string). Validate and lookup.
    try:
        dept_id = int(cookie_val)
    except (TypeError, ValueError):
        return redirect(url_for('select_department'))

    db = get_db()
    dept_row = db.execute('SELECT id, name FROM departments WHERE id = ?', (dept_id,)).fetchone()
    if not dept_row:
        return redirect(url_for('select_department'))

    dept_name = dept_row['name']

    # fetch staffs by department_id FK, include sub-department name when available
    staffs = db.execute(
        'SELECT staffs.*, sub_departments.name as sub_department_name, '
        'sat.is_evection as sat_evection, sun.is_evection as sun_evection '
        'FROM staffs '
        'LEFT JOIN sub_departments ON staffs.sub_department_id = sub_departments.id '
        'LEFT JOIN sat ON sat.staff_id = staffs.id '
        'LEFT JOIN sun ON sun.staff_id = staffs.id '
        'WHERE staffs.department_id = ?'
        ' ORDER BY staffs.name',
        (dept_id,)
    ).fetchall()

    # fetch sub-departments for this department (to populate form select)
    sub_departments = db.execute('SELECT id, name FROM sub_departments WHERE department_id = ? ORDER BY id', (dept_id,)).fetchall()

    return render_template('index.html', department=dept_name, staffs=staffs, sub_departments=sub_departments)


def select_department():
    """Render department chooser and handle selection.

    On GET: render `select-department.html`.
    On POST: read `department` from form, set cookie and redirect to index.
    """
    if request.method == 'POST':
        department = request.form.get('department')
        if not department:
            return render_template('select-department.html', error='请选择部门')

        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('department', department, max_age=365*24*3600)
        return resp

    return render_template('select-department.html')