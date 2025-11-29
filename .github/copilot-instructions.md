# Copilot / AI agent instructions — weekendOvertime

This file contains concise, actionable guidance for AI coding agents working in this repository so they can be immediately productive.

Overview
- **Purpose**: A small Flask app for recording/displaying weekend overtime per department.
- **Entrypoint**: `weekendOvertime.create_app()` in `weekendOvertime/__init__.py`.

Key components and data flow
- `weekendOvertime/__init__.py`: app factory, config (`SECRET_KEY`, `DATABASE`), creates `instance/`, registers endpoints.
- `weekendOvertime/routes/`: primary route modules and handlers. See `index.py` (main UI), `edit_names.py` (add/remove staff), `toggle_sat.py` (AJAX toggles), and `info.py`.
- `weekendOvertime/db.py`: `get_db()`, `close_db()`, and the `flask` CLI `init-db` command. DB file: `instance/weekend-overtime.sqlite`. Schema: `weekendOvertime/schema.sql`.
- Templates: `weekendOvertime/templates/` — `weekend-overtime.html` contains client JS that POSTs JSON (`action: add-date`) and builds the UI.

Project-specific conventions
- Dynamic date columns: per-day columns are created at runtime with names `YYYY_MM_DD` (e.g. `2025_11_28`). Code runs `ALTER TABLE staffs ADD COLUMN "{date_column}" TEXT DEFAULT "bg-1"` to ensure columns exist. This is a schema-mutation pattern; be careful when changing schema layout.
- Status tokens: CSS class names are used as stored tokens: `bg-1` (default), `bg-2` (company overtime), `bg-3` (business trip). Templates and JS expect these exact strings.
- Departments & sub-departments: department is stored in a cookie named `department`. `manu` (manufacturing) uses `sub_department` values to place staff into subgroup containers.

Legacy note
- Previous code included a `work.py` module (an earlier OOP refactor). That module is no longer present — routing and request logic are now implemented under `weekendOvertime/routes/`. Before changing routing, check `weekendOvertime/__init__.py` to confirm how routes are registered.

JSON payload example (client -> server)
```
{
  "action": "add-date",
  "date": "2025-11-28",
  "staffs": [
    {"name": "Alice", "department": "manu", "status": "bg-2"},
    {"name": "Bob", "department": "manu", "status": "bg-3"}
  ],
  "use_fallback": false
}
```

Run / init commands
- Set FLASK app and run dev server:
  - `export FLASK_APP=weekendOvertime:create_app`
  - `flask run --reload` (or `flask --app weekendOvertime:create_app --debug run`)
- Initialize DB (after setting `FLASK_APP`):
  - `flask init-db` (runs `schema.sql` and creates `instance/weekend-overtime.sqlite`)

Recent changes
- Normalized day tables: the app uses `sat` and `sun` tables (rows per staff/day) instead of per-date columns.
- Day selector + JS: `index.html` renders both `sat` and `sun` values as data attributes and adds a day selector so clicks apply to the selected day.
- Toggle endpoint: `weekendOvertime/routes/toggle_sat.py` accepts POST JSON `{ staff_id, status, day }` and updates the corresponding day table.
- File-based operation logging: the app now writes JSON lines to `instance/user-operation.log` via `log_operation_file()` in `weekendOvertime/db.py` for add/remove/toggle operations.
- Migration helper: `scripts/migrate_enforce_unique_sat_sun.py` can be used to add `UNIQUE(staff_id)` to `sat`/`sun` and deduplicate existing rows before relying on upserts.

Testing and smoke checks
- Quick syntax/lint: run `python -m pyflakes .` or `python -m pyflakes weekendOvertime` if available.
- Start the dev server and open `/` to verify UI and that column creation + JSON saving work.
- Example quick smoke test (manual):
  1. `export FLASK_APP=weekendOvertime:create_app`
  2. `flask init-db`
  3. Start server `flask run --reload`
  4. Open the site, add a staff, click the colored item and press `确定` to POST JSON. Observe server logs and DB changes in `instance/weekend-overtime.sqlite`.

Files to inspect for common tasks
- Routes & business logic: `weekendOvertime/routes/` (look at `index.py`, `edit_names.py`, `toggle_sat.py`)
- DB access & CLI: `weekendOvertime/db.py`, `weekendOvertime/schema.sql`
- Templates & client behavior: `weekendOvertime/templates/index.html`

Known quirks & gotchas
- Dynamic column creation: migrating to a normalized model (staff-date rows) will require updating both server logic (GET/POST) and the frontend JS payloads.
- `db.py` registers a `timestamp` converter with `datetime.fromisoformat` but does not import `datetime` in the file. This will raise a `NameError` on import. Fix by adding `from datetime import datetime` at the top of `db.py` if you use the converter.
- The code frequently logs exceptions and calls `db.rollback()`; preserve that pattern when editing SQL to avoid partial commits.

Recommended next steps for contributors
- If adding features that touch dates, follow the existing pattern for column creation or propose a migration to a normalized table.
- For tests, use Flask's `app.test_client()` and construct JSON POSTs matching the example above. Focus tests on `_handle_json_post` and `_choose_display_column`.

Search hints for agents
- Search for `add-date` to follow the JSON flow.
- Inspect `schema.sql` and `db.py` for DB-related changes.

Questions to ask the maintainer before large changes
- Keep dynamic per-date columns or migrate to normalized rows? (this impacts templates and DB access heavily)
- Is there a retention policy for old date-columns?

If anything here is unclear or you want more examples (unit test skeleton, migration plan, or a sample DB export), tell me and I'll expand the document.
