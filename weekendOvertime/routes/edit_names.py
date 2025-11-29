from flask import request, redirect, url_for
from ..db import get_db


def edit_names():
    """Handle add/remove staff name requests.

    Expects form fields: `name` and `action` ('add' or 'remove'). The current
    department is taken from the `department` cookie (stored as department id).
    """
    cookie_val = request.cookies.get('department')
    if not cookie_val:
        return redirect(url_for('select_department'))

    try:
        dept_id = int(cookie_val)
    except (TypeError, ValueError):
        return redirect(url_for('select_department'))

    name = request.form.get('name')
    action = request.form.get('action')
    if not name or not action:
        return redirect(url_for('index'))

    db = get_db()

    # standardized schema: use `sub_department_id` column
    if action == 'add':
        sub_val = request.form.get('sub_department')
        sub_id = None
        if sub_val:
            try:
                sub_id = int(sub_val)
            except (TypeError, ValueError):
                sub_id = None

        try:
            if sub_id is not None:
                cur = db.execute(
                    'INSERT OR IGNORE INTO staffs (name, department_id, sub_department_id) VALUES (?, ?, ?)',
                    (name, dept_id, sub_id)
                )
            else:
                cur = db.execute(
                    'INSERT OR IGNORE INTO staffs (name, department_id) VALUES (?, ?)',
                    (name, dept_id)
                )
            db.commit()

            # If insert was ignored (existing name), update department and sub-department when needed
            if cur.rowcount == 0:
                existing = db.execute('SELECT department_id, sub_department_id FROM staffs WHERE name = ?', (name,)).fetchone()
                needs_update = False
                update_fields = []
                update_params = []
                if existing:
                    if existing['department_id'] != dept_id:
                        needs_update = True
                        update_fields.append('department_id = ?')
                        update_params.append(dept_id)
                    if sub_id is not None and existing['sub_department_id'] != sub_id:
                        needs_update = True
                        update_fields.append('sub_department_id = ?')
                        update_params.append(sub_id)

                if needs_update:
                    try:
                        update_params.append(name)
                        db.execute(f"UPDATE staffs SET {', '.join(update_fields)} WHERE name = ?", tuple(update_params))
                        db.commit()
                    except Exception as e:
                        print(f"Error updating staff {name}: {e}")
                        db.rollback()
        except Exception as e:
            print(f"Error adding staff: {e}")
            db.rollback()

    elif action == 'remove':
        try:
            db.execute('DELETE FROM staffs WHERE name = ? AND department_id = ?', (name, dept_id))
            db.commit()
        except Exception as e:
            print(f"Error deleting staff: {e}")
            db.rollback()

    return redirect(url_for('index'))