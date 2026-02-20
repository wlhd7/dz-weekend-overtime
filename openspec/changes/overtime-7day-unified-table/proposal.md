## Why

Overtime entry currently does not present a consistent rolling week of options and stores data in a split model, which makes scheduling confusing and harder to maintain. A unified weekly view with a 7-day rolling selector will align the UI with how users plan work and simplify backend storage.

## What Changes

- Extend the overtime date select options to show a rolling 7-day window starting from tomorrow.
- Display option labels as date + weekday (for example, "Feb 21 (Sat)") and sort strictly in chronological order.
- Store overtime data in a unified weekly table with columns for mon, tue, wed, thu, fri, sat, sun.

## Capabilities

### New Capabilities
- `rolling-week-date-options`: Provide a 7-day rolling set of date options with ordered, user-friendly labels.
- `weekly-overtime-unified-records`: Persist and access weekly overtime data using a unified mon-sun schema.

### Modified Capabilities
-

## Impact

- Frontend date selection component(s) and formatting logic.
- Backend model at `backend/app/models/overtime.py` and any related migrations/queries.
- API payloads or services that read/write weekly overtime data.
