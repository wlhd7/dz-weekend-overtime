# AGENTS.md

This file provides detailed instructions for agentic coding agents working in this repository. Follow these guidelines to ensure consistent and productive collaboration.

---

## 1. Build, Lint, and Test Commands

### Build and Development
- **Set Flask App and Run Development Server:**
  ```bash
  export FLASK_APP=weekendOvertime:create_app
  flask run --reload
  ```
- **Database Initialization:**
  ```bash
  export FLASK_APP=weekendOvertime:create_app
  flask init-db
  ```

### Lint Commands
- Syntax/Lint Check:
  ```bash
  python -m pyflakes .
  ```
  or
  ```bash
  python -m pyflakes weekendOvertime
  ```

### Testing
- Testing Framework: Flask's `app.test_client()`
- Example Single Test Workflow:
  ```python
  def test_example():
      client = app.test_client()
      response = client.post('/some-endpoint', json={"key": "value"})
      assert response.status_code == 200
  ```
- To manually verify the app's behavior:
  ```bash
  export FLASK_APP=weekendOvertime:create_app
  flask run --reload
  ```
  Open the site in a browser, perform actions, and validate database changes in `instance/weekend-overtime.sqlite`.

---

## 2. Code Style Guidelines

### General Guidelines
- **PEP 8:** Follow PEP 8 for formatting and code style.
- **Imports:**
  - Standard library imports first, third-party libraries second, local imports last.
  - Use absolute imports whenever possible.
  ```python
  from flask import Flask, render_template
  from ..db import get_db
  ```

### Naming Conventions
- **Variables and Functions:** Use `snake_case`.
- **Classes:** Use `CamelCase`.
- **Constants:** Use `UPPER_CASE_WITH_UNDERSCORES`.
- **Modules and Packages:** Use lowercase and avoid underscores unless necessary.

### Type Annotations
- Always include type hints.
```python
from typing import List, Dict

def fetch_staffs(dept_id: int) -> List[Dict]:
    ...
```

### Formatting
- Use spaces, not tabs (4 spaces per indentation level).
- Maximum line length: 79 characters.
- Always ensure one blank line before function definitions and two blank lines before class definitions.

### Error Handling
- Always log exceptions and use `db.rollback()` for database-related errors.
```python
try:
    result = db.execute('SQL QUERY')
except Exception as e:
    app.logger.error(f"Database error: {e}")
    db.rollback()
    raise
```

---

## 3. Project-Specific Conventions

### Routing and Endpoints
- Include clear, expressive endpoint names in `url_for()`.
```python
return redirect(url_for('select_department'))
```
- Dynamic route handlers should validate input.
```python
cookie_val = request.cookies.get('department')
if not cookie_val:
    return redirect(url_for('select_department'))
```

### Templates
- Use `{% extends 'base.html' %}` to derive templates from the shared layout.
- Avoid inline CSS or JS; use `static/` files.

### Database Schema
- Follow existing patterns for table design and naming (see `schema.sql`).
- Use normalized rows when possible.
- Tokens such as `bg-1` (default), `bg-2` (overtime), and `bg-3` (business trip) must be consistent with CSS classes.

### JSON Standards
- Payloads should follow this structure when sent or received via Ajax/Fetch:
```json
{
  "action": "add-date",
  "date": "2025-11-28",
  "staffs": [
    {"name": "Alice", "department": "manu", "status": "bg-2"},
    {"name": "Bob", "department": "sales", "status": "bg-3"}
  ]
}
```

### Logging
- Log all operations (e.g., add/remove actions and status changes) to `instance/user-operation.log` using `log_operation_file()` defined in `weekendOvertime/db.py`.

---

## 4. New Features and Legacy Notes

### Recent Changes
- Normalized `sat` and `sun` tables now replace per-date columns for overtime tracking.
- Added `log_operation_file()` for logging JSON lines during modifications.

### Legacy Quirks
- Dynamic runtime-altered columns exist but should eventually migrate to normalized rows.
- Fix known issue in `db.py`: `datetime` import missing when using `datetime.fromisoformat`.

For any structural changes to routes or database tables, consult `weekendOvertime/__init__.py` for route registration patterns, and ensure that updates sync with frontend templates and client-side JavaScript logic.