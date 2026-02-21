## 1. Backend API + Data Assembly

- [ ] 1.1 Add unprotected FastAPI route `GET /api/exports/overtime-table` with `date=YYYY-MM-DD` validation and HTTP 400 JSON errors
- [ ] 1.2 Implement data lookup for the requested calendar date (decide how `date` maps to existing overtime storage such as sat/sun tables)
- [ ] 1.3 Build per-department export model: mapped departments (1-8) plus unmapped rows preserved but blank
- [ ] 1.4 Compute per-department staff lists grouped by status (`bg-2`, `bg-3`) and remark count = `bg-2` count
- [ ] 1.5 Ensure export ignores any department isolation cookie and always generates a full-table export

## 2. PDF Rendering (Template `format.jpg`)

- [ ] 2.1 Add/confirm backend dependencies for rendering a PDF with a background image and text overlay (and image loading)
- [ ] 2.2 Define layout constants for title date position and each department row's "部门加班人员" + "备注" bounding boxes
- [ ] 2.3 Render the title date in the required Chinese format (e.g., `YYYY年M月D日`) and leave unspecified template fields blank
- [ ] 2.4 Implement name rendering with wrapping inside the bounding box and stable ordering of names
- [ ] 2.5 Implement underline rendering for `bg-3` names and normal rendering for `bg-2` names
- [ ] 2.6 Add overflow handling (font-size fallback / ellipsis) and log when a department overflows the template box
- [ ] 2.7 Return PDF bytes with correct `Content-Type` and `Content-Disposition` attachment filename

## 3. Frontend "制表" Modal

- [ ] 3.1 Add a homepage button labeled "制表"
- [ ] 3.2 Implement modal dialog with weekday checkboxes (周一..周日) and confirm/cancel actions
- [ ] 3.3 Implement default selection logic: Friday -> Sat+Sun, Saturday -> Sun, else -> none
- [ ] 3.4 Prevent confirm when no weekdays are selected (disable button and/or show validation message)

## 4. Frontend Date Resolution + Downloads

- [ ] 4.1 Implement helper to resolve selected weekdays to concrete dates: next occurrence on/after today (local time), within 7 days
- [ ] 4.2 On confirm, request `GET /api/exports/overtime-table?date=YYYY-MM-DD` once per resolved date
- [ ] 4.3 Trigger one browser download per response (handle multiple downloads reliably, preferably sequential)
- [ ] 4.4 Handle loading + errors (e.g., one date fails while others succeed) with user-visible feedback

## 5. Tests + Verification

- [ ] 5.1 Backend tests: missing/invalid `date` -> HTTP 400
- [ ] 5.2 Backend tests: remark count uses `bg-2` only; `bg-2` vs `bg-3` styling decision is respected in renderer inputs
- [ ] 5.3 Backend smoke test: export endpoint returns `application/pdf` and non-empty body
- [ ] 5.4 Manual QA: on Friday default selects Sat+Sun and downloads two files; verify underline for `bg-3`, remark counts, and unmapped rows stay blank
- [ ] 5.5 Verify build commands: `cd backend && pytest`, `npm --prefix frontend run typecheck`, `npm --prefix frontend run build`
