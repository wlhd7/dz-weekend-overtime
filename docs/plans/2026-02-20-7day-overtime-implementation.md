# 7-Day Overtime Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace weekend-only overtime with a date-based model and show the next 7 dates in the UI selector.

**Architecture:** Store overtime per staff per date in a unified `overtime_days` table. Backend APIs accept an ISO date, and the frontend stores the selected date (tomorrow + 6 days) to drive status reads and toggles.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Vue 3, Pinia, Element Plus.

---

### Task 1: Update overtime service tests for date-based behavior

**Files:**
- Modify: `tests/test_services.py`

**Step 1: Write the failing test**

```python
def test_get_staff_status_no_record_date_based(self, db_session, sample_staff):
    service = OvertimeService(db_session)
    status = service.get_staff_status(sample_staff.id, "2026-02-21")
    assert status == "bg-1"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::TestOvertimeService::test_get_staff_status_no_record_date_based -v`
Expected: FAIL with validation error for day/date

**Step 3: Write minimal implementation**

Update remaining overtime service tests in `TestOvertimeService` to pass ISO dates instead of `sat/sun` and to assert status toggles on a date.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::TestOvertimeService -v`
Expected: PASS (or only remaining failures relate to missing model/service changes)

**Step 5: Commit**

```bash
git add tests/test_services.py
git commit -m "test: switch overtime service tests to date based"
```

### Task 2: Add unified overtime model and remove weekend-only tables

**Files:**
- Modify: `backend/app/models/overtime.py`
- Modify: `backend/app/models/staff.py`
- Modify: `backend/app/models/__init__.py`

**Step 1: Write the failing test**

Add a test to ensure the unified model can store two different dates for the same staff and enforces uniqueness per date:

```python
def test_overtime_day_unique_per_date(self, db_session, sample_staff):
    from app.models import OvertimeDay
    db_session.add(OvertimeDay(staff_id=sample_staff.id, work_date="2026-02-21", status="bg-2"))
    db_session.add(OvertimeDay(staff_id=sample_staff.id, work_date="2026-02-22", status="bg-3"))
    db_session.commit()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::TestOvertimeService::test_overtime_day_unique_per_date -v`
Expected: FAIL with import error (OvertimeDay missing)

**Step 3: Write minimal implementation**

- Replace `Sat`/`Sun` models with a single `OvertimeDay` model containing:
  - `staff_id` (FK)
  - `work_date` (DATE or String)
  - `status` (TEXT)
  - `updated_at` (INTEGER)
- Update `Staff` relationship to `overtime_days`.
- Update `__all__` exports.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::TestOvertimeService::test_overtime_day_unique_per_date -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/overtime.py backend/app/models/staff.py backend/app/models/__init__.py tests/test_services.py
git commit -m "feat: add unified overtime day model"
```

### Task 3: Update OvertimeService to use date-based table

**Files:**
- Modify: `backend/app/services/overtime.py`

**Step 1: Write the failing test**

Add a test to verify `toggle_staff_status` updates the same date record:

```python
def test_toggle_staff_status_updates_date_record(self, db_session, sample_staff):
    service = OvertimeService(db_session)
    service.toggle_staff_status(sample_staff.id, "bg-2", "2026-02-21")
    service.toggle_staff_status(sample_staff.id, "bg-3", "2026-02-21")
    assert service.get_staff_status(sample_staff.id, "2026-02-21") == "bg-3"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::TestOvertimeService::test_toggle_staff_status_updates_date_record -v`
Expected: FAIL due to old table logic

**Step 3: Write minimal implementation**

- Replace day validation with ISO date parsing.
- Query `OvertimeDay` by `staff_id` + `work_date`.
- `bg-1` removes the record; `bg-2/bg-3` upsert the record and set `status`.
- Update `apply_to_all` and `get_department_statistics` to use date + unified table.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::TestOvertimeService -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/overtime.py tests/test_services.py
git commit -m "feat: switch overtime service to date based records"
```

### Task 4: Update staff service and router to accept date

**Files:**
- Modify: `backend/app/services/staff.py`
- Modify: `backend/app/routers/staffs.py`

**Step 1: Write the failing test**

Add a test for `get_staffs_by_department` with date input returning `status` per staff:

```python
def test_get_staffs_by_department_with_date_status(self, db_session, sample_department, sample_staff):
    service = StaffService(db_session)
    service.overtime_service.toggle_staff_status(sample_staff.id, "bg-2", "2026-02-21")
    result = service.get_staffs_by_department(sample_department.id, "2026-02-21")
    assert result[0]["status"] == "bg-2"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::TestStaffService::test_get_staffs_by_department_with_date_status -v`
Expected: FAIL due to missing date param and field

**Step 3: Write minimal implementation**

- Add `date` parameter to staff service query and join `overtime_days` on `work_date`.
- Update router to accept `date` query param and include `status` in response model.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::TestStaffService::test_get_staffs_by_department_with_date_status -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/staff.py backend/app/routers/staffs.py tests/test_services.py
git commit -m "feat: return date based overtime status with staff list"
```

### Task 5: Update overtime router to accept ISO date

**Files:**
- Modify: `backend/app/routers/overtime.py`

**Step 1: Write the failing test**

Add a router test to ensure invalid date yields 400 and valid date toggles status. If no router tests exist, add service-level test validating date parsing in OvertimeService.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::TestOvertimeService::test_invalid_date_rejected -v`
Expected: FAIL

**Step 3: Write minimal implementation**

- Update Pydantic model to use `date` (ISO string) and validate it.
- Use `OvertimeService` to toggle status.
- Update status response to return date-scoped status if needed.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::TestOvertimeService::test_invalid_date_rejected -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/routers/overtime.py tests/test_services.py
git commit -m "feat: accept ISO date in overtime endpoints"
```

### Task 6: Update frontend store for ISO date selection

**Files:**
- Modify: `frontend/src/stores/staff.ts`

**Step 1: Write the failing test**

If no frontend test setup exists, skip test and proceed to implementation.

**Step 2: Write minimal implementation**

- Change `selectedDay` type from `sat/sun` to `string` (ISO date).
- Update `toggleStaffStatus` to send date string to `/overtime/toggle`.
- Update staff status fields to read `status` instead of `sat_evection/sun_evection`.

**Step 3: Commit**

```bash
git add frontend/src/stores/staff.ts
git commit -m "feat: store selected date and use date based status"
```

### Task 7: Update Home.vue date selector for next 7 days

**Files:**
- Modify: `frontend/src/views/Home.vue`

**Step 1: Write minimal implementation**

- Generate options for tomorrow + next 6 days in order.
- Label format `M月D号-周X`, value ISO date.
- Bind options to `selectedDay`.

**Step 2: Commit**

```bash
git add frontend/src/views/Home.vue
git commit -m "feat: show 7 day date options in selector"
```

### Task 8: Update any backend response models/types

**Files:**
- Modify: `backend/app/routers/staffs.py`
- Modify: `backend/app/routers/overtime.py`

**Step 1: Ensure response models reflect new `status` and remove `sat/sun` fields.**

**Step 2: Run full tests**

Run: `cd backend && pytest`
Expected: PASS

**Step 3: Commit**

```bash
git add backend/app/routers/staffs.py backend/app/routers/overtime.py
git commit -m "refactor: align response models with date based overtime"
```

---

Plan complete and saved to `docs/plans/2026-02-20-7day-overtime-implementation.md`. Two execution options:

1. Subagent-Driven (this session) - I dispatch fresh subagent per task, review between tasks, fast iteration
2. Parallel Session (separate) - Open new session with executing-plans, batch execution with checkpoints

Which approach?
