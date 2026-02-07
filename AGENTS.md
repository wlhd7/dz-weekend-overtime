# AGENTS.md

This file provides detailed instructions for agentic coding agents working in this repository. Follow these guidelines to ensure consistent and productive collaboration.

---

## 1. Build, Lint, and Test Commands

### 1.1 Build and Development
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

### 1.2 Lint Commands
- Syntax/Lint Check:
  ```bash
  python -m pyflakes .
  ```
  or
  ```bash
  python -m pyflakes weekendOvertime
  ```

### 1.3 Testing
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

### 2.1 General Guidelines
- **PEP 8:** Follow PEP 8 for formatting and code style.
- **Imports:**
  - Standard library imports first, third-party libraries second, local imports last.
  - Use absolute imports whenever possible.
  ```python
  from flask import Flask, render_template
  from ..db import get_db
  ```

### 2.2 Naming Conventions
- **Variables and Functions:** Use `snake_case`.
- **Classes:** Use `CamelCase`.
- **Constants:** Use `UPPER_CASE_WITH_UNDERSCORES`.
- **Modules and Packages:** Use lowercase and avoid underscores unless necessary.

### 2.3 Type Annotations
- Always include type hints.
```python
from typing import List, Dict

def fetch_staffs(dept_id: int) -> List[Dict]:
    ...
```

### 2.4 Formatting
- Use spaces, not tabs (4 spaces per indentation level).
- Maximum line length: 79 characters.
- Always ensure one blank line before function definitions and two blank lines before class definitions.

### 2.5 Error Handling
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

### 3.1 Routing and Endpoints
- Include clear, expressive endpoint names in `url_for()`.
```python
return redirect(url_for('select_department'))
```
- Dynamic route handlers should validate input thoroughly.
```python
cookie_val = request.cookies.get('department')
if not cookie_val:
    return redirect(url_for('select_department'))

# Example: Enhanced input validation
try:
    staff_id = int(staff_id)
    if staff_id <= 0:
        return jsonify(ok=False, error="invalid staff_id"), 400
except (TypeError, ValueError):
    return jsonify(ok=False, error="invalid staff_id"), 400
```

### 3.2 Templates
- Use `{% extends 'base.html' %}` to derive templates from the shared layout.
- Avoid inline CSS or JS; use `static/` files.

### 3.3 Database Schema
- Follow existing patterns for table design and naming (see `schema.sql`).
- Use normalized rows when possible.
- Tokens such as `bg-1` (default), `bg-2` (overtime), and `bg-3` (business trip) must be consistent with CSS classes.
- **Security Note**: Always use parameterized queries instead of f-string SQL construction to prevent injection.

### 3.4 JSON Standards
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

### 3.5 Logging
- Log all operations (e.g., add/remove actions and status changes) to `instance/user-operation.log` using `log_operation_file()` defined in `weekendOvertime/db.py`.

---

## 4. New Features and Legacy Notes

### 4.1 Recent Changes
- Normalized `sat` and `sun` tables now replace per-date columns for overtime tracking.
- Added `log_operation_file()` for logging JSON lines during modifications.
- **Security Enhancements**: 
  - Enhanced input validation in `toggle_sat.py` with proper integer validation
  - Replaced f-string SQL construction with parameterized queries to prevent SQL injection
  - Improved JavaScript error handling with null checks for `prevClass`
- **Removed Features**: Preset management functionality has been removed from main interface

### 4.2 Legacy Quirks
- Dynamic runtime-altered columns exist but should eventually migrate to normalized rows.
- **Fixed**: `datetime` import issue in `db.py` has been resolved - `datetime.fromisoformat` is properly imported.

For any structural changes to routes or database tables, consult `weekendOvertime/__init__.py` for route registration patterns, and ensure that updates sync with frontend templates and client-side JavaScript logic.

---

## 5. Business Context Reference

### 5.1 When to Consult PRD.md
Before implementing new features or modifying existing functionality, consult `PRD.md` for complete business context:

#### 5.2 Feature Development
- **Section 3.1-3.5**: Detailed functional requirements for each module
- **Section 4**: Business workflows and user interaction patterns
- **Section 5**: Data model constraints and entity relationships

#### 5.3 Route and Endpoint Changes
- Cross-reference with PRD section 3.3 for status token meanings (`bg-1`, `bg-2`, `bg-3`)
- Ensure API responses align with JSON standards in PRD section 3.3.2
- Validate user workflows against PRD section 4 business flows

#### 5.4 Database Modifications
- Reference PRD section 5 for complete entity relationship diagrams
- Maintain compatibility with existing data structures described in PRD
- Ensure schema changes support business requirements in PRD section 3

#### 5.5 UI/Template Updates
- Align with user workflows described in PRD section 4
- Maintain consistency with business rules in PRD section 3
- Support department isolation requirements from PRD section 2.1

### 5.6 Validation Checklist
Before committing changes, verify:
- [ ] Implementation matches PRD functional requirements
- [ ] User workflow aligns with PRD business flows
- [ ] Data model maintains PRD-defined relationships
- [ ] Status tokens follow PRD section 3.3.1 definitions
- [ ] Department isolation is preserved per PRD section 2.1