## Context

Overtime is currently stored in separate `sat` and `sun` tables with a per-staff record and an `is_evection` flag. The backend services and router only accept `day` values of `sat` or `sun`, and the frontend exposes a weekend-only selector. The change expands the UI to a rolling 7-day selector with date + weekday labels and requires a unified backend table that records `mon` through `sun` in a single row.

## Goals / Non-Goals

**Goals:**
- Provide a 7-day rolling day selector starting from tomorrow with chronological ordering and date + weekday labels.
- Store per-day overtime status in a unified `mon`-through-`sun` schema under `backend/app/models/overtime.py`.
- Update API/service logic to read and write statuses for any weekday (mon-sun).

**Non-Goals:**
- Historical, multi-week overtime tracking or reporting.
- New UI for per-day content, time ranges, or detailed overtime notes.
- Changing the meaning of the status tokens (`bg-1`, `bg-2`, `bg-3`).

## Decisions

- **Unified model:** Replace the `Sat`/`Sun` tables with a single `OvertimeWeek` table (name TBD) keyed by `staff_id`, containing columns `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`. Each column stores the status token (`bg-1`, `bg-2`, `bg-3`), defaulting to `bg-1`.
- **Day mapping:** The API continues to accept a `day` token, but expands validation to `mon`-`sun`. The frontend selector displays a date label yet sends the weekday token as the value, ensuring one entry per day in the 7-day window.
- **Service/API updates:** Replace `Sat`/`Sun` branching with a weekday-to-column mapping. Update `/overtime/toggle`, `/overtime/status`, and statistics queries to read/write the unified table. Responses return per-day status tokens instead of booleans.
- **Selector behavior:** Build the 7-day list by starting at "tomorrow" and iterating 7 days forward. Sort by date ascending, label as localized date + weekday (match existing UI locale), and value as weekday token.

## Risks / Trade-offs

- **Rolling window ambiguity:** Without storing exact dates, data represents the next occurrence of each weekday; crossing week boundaries may be confusing. Mitigation: document the behavior and consider a future reset when the 7-day window rolls.
- **Data migration:** Backfilling from `sat`/`sun` into a unified row could drop unused fields. Mitigation: migrate only status, and keep the legacy tables for rollback during the first release.
- **Timezone mismatch:** "Today" is computed on the client, which may differ from server time. Mitigation: treat the schedule as client-centric and keep logic consistent with existing UI behavior.

## Migration Plan

- Add the unified overtime model and create the new table in SQLite.
- Backfill: for each staff, set `sat`/`sun` columns based on existing records (`bg-2` for internal overtime, `bg-3` for business trip), and default all other days to `bg-1`.
- Update backend services/routers and frontend store/views to use weekday tokens and unified storage.
- Keep `sat`/`sun` tables temporarily for rollback; remove them after verification.

## Rollback Approach

- Keep legacy `sat`/`sun` tables untouched during rollout.
- To rollback, point API/services back to `sat`/`sun` and ignore `overtime_weeks` while preserving existing data.

## Open Questions

- Should we preserve per-day `content`, `begin_time`, `end_time`, and `updated_at` fields in the unified table, or explicitly drop them?
- Should `/overtime/status` return status tokens for each day or a condensed structure (for example, an array of day/status pairs)?
- Is the date label format fixed (for example, Chinese date + weekday) or should it follow the browser locale?
