# AGENTS.md

Guidance for agentic coding assistants working in this repo. Keep changes
consistent with the current FastAPI + Vue 3 architecture and the conventions
below. This file consolidates repo context plus Copilot instructions.

## 1. Build, Lint, and Test Commands

### 1.1 Development & Build

Backend (FastAPI):
- `cd backend && pip install -r requirements.txt`
- `cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Frontend (Vite + Vue 3):
- `npm --prefix frontend install`
- `npm --prefix frontend run dev`
- `npm --prefix frontend run build`
- `npm --prefix frontend run typecheck`

Full dev stack:
- `./start-dev.sh`

Docker build (production):
- `docker-compose up -d --build`

### 1.2 Lint / Format / Type Check

Backend:
- `black backend/`
- `flake8 backend/`
- `mypy backend/`

Frontend:
- `npm --prefix frontend run typecheck`

Legacy lint (still supported if needed):
- `python -m pyflakes .`
- `python -m pyflakes weekendOvertime`

### 1.3 Tests (pytest)

Run all tests:
- `cd backend && pytest`

Single test:
- `pytest tests/test_services.py::TestDepartmentService::test_get_all_departments_empty`

When tests need backend context:
- `python -m pytest`

## 2. Code Style Guidelines

### 2.1 Python (backend/app)

- Imports: standard library, third-party, local imports in that order.
- Prefer absolute imports within `backend/app`.
- Type hints required for public functions and service methods.
- Error handling: log exceptions and rollback DB transactions when needed.
- Follow PEP 8; 4-space indentation; keep line length reasonable (79-100).

Example error handling pattern:
```python
try:
    result = db.execute(query, params)
except Exception as exc:
    logger.exception("Database error")
    db.rollback()
    raise
```

### 2.2 TypeScript / Vue (frontend/src)

- Prefer `<script lang="ts">` or `<script setup lang="ts">` in Vue SFCs.
- Type props/emits using `defineProps<T>()` and `defineEmits<T>()`.
- Use explicit types for store state and API responses.
- Keep composition API logic in `setup()` tidy and return only used bindings.

### 2.3 Naming & Conventions

- Python: `snake_case` for variables/functions, `CamelCase` for classes.
- TypeScript: `camelCase` for variables/functions, `PascalCase` for types.
- Constants: `UPPER_SNAKE_CASE`.
- Routes: use clear, stable names; keep endpoints under `/api/*` for backend.

### 2.4 Imports & Formatting

- Avoid unused imports; keep import groups sorted.
- Prefer small, focused functions over large monoliths.
- Avoid inline CSS/JS in templates unless consistent with existing patterns.

## 3. Project Architecture (Current)

### 3.1 Backend (FastAPI)

- Entry: `backend/app/main.py`
- Routers: `backend/app/routers/`
- Services: `backend/app/services/` (business logic)
- Models: `backend/app/models/`
- DB: `backend/app/database.py` (SQLite, WAL enabled)

Use `get_db()` dependency for sessions. Routers should delegate to services.

### 3.2 Frontend (Vue 3 + Vite)

- Entry: `frontend/src/main.ts`
- Router: `frontend/src/router/index.ts` (lazy-loaded views)
- Stores: `frontend/src/stores/` (Pinia)
- API: `frontend/src/utils/api.ts`

## 4. Domain Rules & Data Notes

- Status tokens are persisted CSS class names: `bg-1`, `bg-2`, `bg-3`.
- Department isolation uses a cookie named `department`.
- Overtime data uses `sat` and `sun` tables with `UNIQUE(staff_id)`.

## 5. Legacy Notes (from Copilot instructions)

The old Flask app under `weekendOvertime/` is legacy and no longer active,
but the instructions are still helpful when reading history:

- Flask entrypoint: `weekendOvertime.create_app()`
- Dynamic per-date columns existed; now replaced by normalized `sat`/`sun`.
- Status tokens `bg-1/bg-2/bg-3` are still used consistently.
- Logging: `log_operation_file()` writes JSON lines to
  `instance/user-operation.log`.

Legacy JSON payload example:
```json
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

## 6. Testing Guidance

- Tests use pytest; fixtures in `tests/conftest.py`.
- Prefer service-level tests and database fixtures when adding coverage.

## 7. PRD / Requirements

- Use `PRD.md` for business context before altering workflows.
- Ensure status tokens and department isolation remain intact.

## 8. Additional Repo Rules

- No Cursor rules or `.cursorrules` found.
- Copilot instructions were reviewed and merged into this file.
