from flask import request, jsonify
from ..db import get_db


def toggle_sat():
    """AJAX endpoint to toggle a staff's sat/sun status.

    Expects JSON body: { "staff_id": <int>, "status": "bg-1"|"bg-2"|"bg-3", "day": "sat"|"sun" }

    Behavior:
    - "bg-1": remove staff from the given day table (DELETE)
    - "bg-2": ensure a row exists with is_evection=0
    - "bg-3": ensure a row exists with is_evection=1

    Returns JSON {ok: true} on success, or {ok: false, error: "..."} on failure.
    """
    if not request.is_json:
        return jsonify(ok=False, error='expected JSON'), 400

    data = request.get_json()
    staff_id = data.get('staff_id')
    status = data.get('status')
    day = data.get('day', 'sat')
    if day not in ('sat', 'sun'):
        return jsonify(ok=False, error='invalid day'), 400

    if not staff_id or status not in ('bg-1', 'bg-2', 'bg-3'):
        return jsonify(ok=False, error='invalid payload'), 400

    db = get_db()
    try:
        # Removal case: bg-1 -> delete any existing row
        if status == 'bg-1':
            db.execute(f'DELETE FROM {day} WHERE staff_id = ?', (staff_id,))
            db.commit()
            return jsonify(ok=True)

        is_evection = 1 if status == 'bg-3' else 0

        # Ensure there is only one row per staff_id in the day table.
        # Some older DBs may lack a UNIQUE(staff_id) constraint; deleting any
        # existing row first prevents inserting duplicates and avoids JOIN
        # duplication in the main query.
        db.execute(f'DELETE FROM {day} WHERE staff_id = ?', (staff_id,))
        db.execute(
            f"INSERT INTO {day} (staff_id, is_evection) VALUES (?, ?)",
            (staff_id, is_evection)
        )
        db.commit()
        return jsonify(ok=True)
    except Exception as e:
        db.rollback()
        return jsonify(ok=False, error=str(e)), 500
