## 1. Data Model & Migration

- [x] 1.1 Define unified overtime model with `mon`-`sun` status fields and update model exports
- [x] 1.2 Create migration/backfill logic to map existing `sat`/`sun` records into unified rows
- [x] 1.3 Keep legacy `sat`/`sun` tables during rollout and document rollback approach

## 2. Backend Service & API Updates

- [x] 2.1 Expand day validation to `mon`-`sun` and map weekday token to unified columns
- [x] 2.2 Update `/overtime/toggle` to write status tokens into unified records
- [x] 2.3 Update `/overtime/status` to return `mon`-`sun` status tokens per staff member
- [x] 2.4 Update statistics queries and any day-based logic to read from unified records

## 3. Frontend Rolling Selector

- [x] 3.1 Build 7-day rolling date option list starting from tomorrow
- [x] 3.2 Format option labels as date + weekday and ensure chronological ordering
- [x] 3.3 Update store and views to send weekday tokens for selection and handle `mon`-`sun` statuses

## 4. Validation & Cleanup

- [x] 4.1 Verify API responses and UI rendering for all seven days
- [x] 4.2 Remove or deprecate legacy `sat`/`sun` references after verification
