## Context

This repo is a FastAPI + Vue 3 (Vite) application used by department heads to fill weekend overtime data. Users need a frictionless way to export official overtime table documents directly from system data. The export output must match the provided paper template `format.jpg` and encode two overtime statuses:

- `bg-2`: internal overtime (name rendered normally)
- `bg-3`: business trip (name rendered with underline)

The export template contains fixed department rows. Some template department names have no DB department ID mapping; those rows must remain in the output and be left blank.

Constraints / conventions:

- Backend endpoints live under `/api/*` and use `get_db()` dependency.
- Status tokens are persisted as CSS-like class names (`bg-1/bg-2/bg-3`).
- There is a cookie-based department isolation (`department` cookie) used elsewhere; the export feature is explicitly "无需保护" and should not require auth.

## Goals / Non-Goals

**Goals:**

- Add a homepage entrypoint (button "制表") that opens a modal with weekday checkboxes (Mon-Sun) and the specified default selection logic.
- On confirm, download one export file per selected day (e.g., selecting Sat+Sun triggers two downloads).
- Generate export documents that visually match `format.jpg`:
  - Fill the title date (and any other date fields on the template, if present).
  - For each department row:
    - "部门加班人员": list staff names for that date; underline names for `bg-3`, normal text for `bg-2`.
    - "备注": internal overtime count for that department (count of `bg-2`).
- Map template department rows to DB department IDs where available:
  - 制造部=1, 品质部=2, 工艺部=3, 装配部=4, 电气部=5, 技术部=6, 机加技术部=7, 业务部=8
  - Rows without mapping remain blank.

**Non-Goals:**

- Re-designing the overtime data model.
- Adding authentication/authorization for export.
- Building a general-purpose report designer; this export is template-specific.

## Decisions

1) Export format: PDF built from the template image

- Use `format.jpg` as a background image and overlay text (names, counts, dates) to preserve the exact layout.
- Return a single PDF per selected date (print-friendly, stable across devices).

Alternatives considered:

- Export Excel/Word: easier cell layout but harder to match a JPG template exactly; increased client variability.
- Export JPG/PNG: simplest rendering, but printing/scaling quality and multi-page handling are less predictable.

2) Backend API: one file per request

- Add an unprotected endpoint such as:
  - `GET /api/exports/overtime-table?date=YYYY-MM-DD`
- Response:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="YYYY-MM-DD_上班人员统计表.pdf"`

Frontend will call this endpoint once per selected date and trigger downloads.

Alternatives considered:

- A single endpoint that returns a ZIP when multiple dates are selected. This reduces requests but complicates UX (requirement implies separate tables).

3) Date selection semantics: weekday UI, explicit date on the wire

- UI presents weekday checkboxes (周一..周日) and applies the default logic based on "today".
- On confirm, the frontend computes the concrete calendar date for each selected weekday (next occurrence starting from today) and passes `date=YYYY-MM-DD` to the backend.

Rationale:

- The template requires a concrete date string.
- Passing explicit dates avoids server/client timezone mismatches and keeps the export endpoint deterministic.

Open consideration:

- If the app data model only supports Sat/Sun tables without historical dates, the backend may need to map `date` to the current "active weekend". This should be validated while implementing specs.

4) Data assembly: group staff by department and status

- Query overtime entries for the requested date.
- For each mapped department ID, collect staff with status `bg-2` and `bg-3`.
- Render staff names in the "部门加班人员" box in a stable order (e.g., by staff name or staff_id; pick one and keep consistent).
- Compute remark count per department as `len(bg-2 staff)`.

5) Template layout: fixed bounding boxes + text wrapping

- Define a small layout map in code (constants) for:
  - Title date position
  - Per-department "部门加班人员" rectangle (x/y/width/height)
  - Per-department "备注" rectangle
- Implement text wrapping by measuring text width with the chosen font and inserting line breaks to fit within each rectangle.
- Underline rendering for `bg-3`:
  - PDF: draw a line under each `bg-3` name segment.
  - If using raster first (Pillow): draw a short underline under the glyph run for that name.

6) Fonts: ship a known Chinese-capable font

- Bundle a CJK-capable font (e.g., Noto Sans CJK) with the backend image, or install it in the container.
- Ensure the renderer uses this font to avoid missing glyphs on servers.

## Risks / Trade-offs

- [Text overflow for large departments] Too many names may not fit the template cell. → Implement wrapping + fallback (reduce font size within a range, or clip with ellipsis) and log when overflow occurs.
- [Underline accuracy] Underlining in a raster/PDF overlay can look misaligned depending on font metrics. → Use font ascent/descent metrics and test on sample outputs; keep a small per-font tweak constant.
- [Timezone/date mismatch] "Today" differs between client and server, affecting default selections and computed dates. → Compute default selections in the client only; pass explicit `date` values to the server.
- [Department isolation interference] Existing endpoints may filter by `department` cookie. → Make export endpoint explicitly ignore department isolation and always build a full-table export.
- [Font availability in prod] Missing CJK fonts causes tofu (square boxes). → Bundle font with app assets and load explicitly; add container validation in CI.
