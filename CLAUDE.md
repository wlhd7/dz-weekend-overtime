# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Weekend Overtime Management System** for tracking and managing weekend overtime schedules across multiple departments.

**Architecture**: Modern FastAPI backend + Vue.js frontend (migrated from Flask; legacy code in `weekendOvertime/` directory is no longer active).

## Common Commands

### Development

```bash
# Start both backend and frontend together
./start-dev.sh

# Backend only
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
cd frontend
npm install
npm run dev

# Production builds
cd frontend && npm run build
docker-compose up -d --build
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Run specific test
pytest tests/test_services.py::TestDepartmentService::test_get_all_departments_empty

# For tests requiring backend context
python -m pytest
```

### Code Quality

```bash
# Pre-commit checks
pre-commit run --all-files

# Individual tools
black backend/           # Format Python code
flake8 backend/          # Lint Python code
mypy backend/            # Type checking
```

## Architecture

### Backend (FastAPI) - `backend/app/`

**Layered Architecture:**
- `main.py` - Application entry, CORS config, route registration
- `models/` - SQLAlchemy ORM models (Department, Staff, Overtime, SubDepartment)
- `routers/` - FastAPI route handlers (departments, staffs, overtime, info)
- `services/` - Business logic layer (encapsulates database operations)
- `middleware/` - Cross-cutting concerns (auth, validation)
- `utils/` - Helper functions
- `database.py` - SQLAlchemy engine with WAL mode, session factory

**Database:**
- SQLite at `database/weekend-overtime.sqlite`
- Uses WAL mode for better concurrency
- Tables: `departments`, `sub_departments`, `staffs`, `sat`, `sun`

**Route Patterns:**
- `/api/departments/*` - Department management and selection
- `/api/staffs/*` - Staff CRUD operations
- `/api/overtime/*` - Overtime status management
- `/api/info/*` - Cross-department statistics

### Frontend (Vue.js) - `frontend/src/`

**Structure:**
- `main.js` - Vue app initialization
- `router/` - Vue Router configuration
- `stores/` - Pinia state management (department.js, staff.js)
- `views/` - Page components (Home, DepartmentSelect, Info)
- `components/` - Reusable components
- `utils/api.js` - Axios HTTP client with CORS and auth interceptors

**State Management:**
- Department state stored in cookies for persistence
- Pinia stores manage client-side state with API sync

## Key Concepts

### Status Tokens
CSS class names used as database values for overtime status:
- `bg-1` (default) - No overtime
- `bg-2` - Normal overtime (company location)
- `bg-3` - Business trip (off-site)

### Department Isolation
- Department selection stored in cookie named `department`
- All staff operations scoped to current department
- Auth middleware validates department cookie

### Day Management
- Separate `sat` and `sun` tables for Saturday and Sunday overtime
- Each staff can have one status per day
- Records use `UNIQUE(staff_id)` constraint

## Important Patterns

### Backend Services Pattern
Business logic lives in `backend/app/services/`. Routers should delegate to services rather than direct DB access:

```python
# In router
@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    service = DepartmentService(db)
    return service.get_all_departments()
```

### Database Session Dependency
Always use `get_db()` dependency for sessions to ensure cleanup:

```python
from .database import get_db
def my_endpoint(db: Session = Depends(get_db)):
    ...
```

### Frontend API Client
Use the configured `api` instance from `utils/api.js` for all API calls - handles cookies and CORS.

## Legacy Note

The `weekendOvertime/` directory contains the old Flask application. This is no longer active. When making changes, work in `backend/app/` and `frontend/src/`.

## Testing Fixtures

Common test fixtures in `tests/conftest.py`:
- `temp_db` - Temporary database file
- `db_session` - Fresh database session
- `sample_department` - Pre-populated department
- `sample_staff` - Pre-populated staff member
