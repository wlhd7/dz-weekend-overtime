# 7-Day Overtime Date Selection and Storage Design

## Goal
Extend overtime tracking from weekend-only to a rolling 7-day window and update the UI date selector to list the next 7 days in chronological order.

## Scope
- Replace the weekend-only model with a unified date-based overtime table.
- Update API endpoints to accept a specific date instead of "sat/sun".
- Update the frontend date select to display tomorrow through the next 6 days in order.

## Data Model
Create a single table `overtime_days`:

- `id` (PK)
- `staff_id` (FK -> staffs.id, not null)
- `work_date` (DATE, not null)
- `status` (TEXT, not null, one of `bg-1`, `bg-2`, `bg-3`)
- `updated_at` (INTEGER)

Constraints and indexes:
- `UNIQUE(staff_id, work_date)` to avoid duplicates.
- Indexes on `staff_id` and `work_date` to speed lookups.

Rationale:
- Supports 7-day rolling selection without proliferating per-day tables.
- Keeps status tokens consistent with existing UI logic.

## API Changes
`POST /overtime/toggle`:
- Accepts `day` as ISO date string (`YYYY-MM-DD`).
- Upsert into `overtime_days` for the given `staff_id` + `work_date`.
- `bg-1` removes row (or stores `bg-1` if preferred).

`GET /overtime/status`:
- Accepts `date` (ISO) and `dept_id`.
- Returns overtime status for each staff for that date.

## Frontend Behavior
- Date select options = tomorrow through next 6 days.
- Labels: `M月D号-周X` (e.g., `2月21号-周六`).
- Values: ISO date strings.
- Sorted by date ascending.

## Error Handling
- Missing row for a staff/date is treated as `bg-1`.
- Invalid date input returns 400.

## Testing
- Backend: toggle creates/removes entries per date; status query returns correct mapping for a date.
- Frontend: date options generated and sorted correctly; selected date drives API calls.
