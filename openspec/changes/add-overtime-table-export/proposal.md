## Why

Department heads fill weekend overtime on Fridays, and we need a fast way to generate the official, printable overtime table(s) directly from the system data. A one-click export from the homepage reduces manual copy/paste, keeps department totals consistent, and produces documents that match the existing paper template.

## What Changes

- Add a homepage button labeled "制表" that opens a modal.
- In the modal, users select day(s) of week (Mon-Sun) via checkboxes.
- Default checkbox behavior:
  - If today is Friday: preselect Saturday + Sunday
  - If today is Saturday: preselect Sunday
  - Else: no default selections
- On confirm, the browser downloads overtime table file(s): one file per selected day (e.g., selecting Sat+Sun downloads two tables).
- Exported tables follow the provided template `format.jpg`, including the department rows in the same order and the date shown in the title.
- Department data is filled based on the template department names mapped to DB department IDs:
  - 制造部=1, 品质部=2, 工艺部=3, 装配部=4, 电气部=5, 技术部=6, 机加技术部=7, 业务部=8
  - Rows without a DB mapping (仓库/采购部/管理部, etc.) remain present in the template and are left blank.
- In the template column "部门加班人员", fill staff names for the selected date. Name formatting encodes status:
  - No underline: internal overtime (`bg-2`)
  - Underline: business trip (`bg-3`)
- In the template column "备注", fill the per-department count of internal overtime staff (count of `bg-2`).
- "制表" export is not protected (no auth gate beyond existing app behavior).

## Capabilities

### New Capabilities

- `overtime-table-export`: Generate downloadable overtime table documents per selected weekday using `format.jpg`, including department mapping, name styling (`bg-2` normal, `bg-3` underlined), and per-department remark counts (`bg-2` only).
- `overtime-table-export-ui`: Homepage "制表" entrypoint (modal + weekday checkboxes + default selection logic) that triggers browser downloads for each selected day.


### Modified Capabilities

## Impact

- Frontend: homepage UI change (new button + modal), default-selection date logic, download handling for multiple files.
- Backend: new unprotected `/api/*` endpoint(s) for generating the export; service logic to assemble per-department staff lists and render the output in the template format.
- Dependencies: may require adding a document/image generation library and ensuring Chinese font rendering to match the template.
