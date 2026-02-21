# Purpose

Define the expected behavior for generating downloadable overtime table document(s)
from system overtime data, matching the provided template `format.jpg`.

# Requirements

## ADDED Requirements

### Requirement: Export endpoint returns a downloadable document for a date
The system SHALL provide an unprotected HTTP endpoint that generates an overtime
table document for a requested calendar date.

#### Scenario: Successful export request
- **WHEN** the client requests `GET /api/exports/overtime-table?date=2026-02-22`
- **THEN** the server responds with a binary document and `Content-Disposition:
  attachment`

### Requirement: Export output uses the provided template layout
The exported document SHALL visually match the layout of `format.jpg`.

#### Scenario: Template layout is preserved
- **WHEN** an export is generated for any valid date
- **THEN** the document contains the same department rows and columns as the
  template, with unspecified fields left blank

### Requirement: Template department rows are filled using the defined mapping
The system SHALL fill department rows using the template-name to DB-department-id
mapping:

- 制造部=1, 品质部=2, 工艺部=3, 装配部=4, 电气部=5, 技术部=6, 机加技术部=7, 业务部=8

Rows without a DB mapping (e.g., 仓库/采购部/管理部) SHALL remain present and
blank.

#### Scenario: Unmapped department rows remain blank
- **WHEN** an export is generated
- **THEN** the output includes the unmapped department rows and does not attempt
  to populate names or counts for them

### Requirement: Staff names are rendered with status-specific styling
For each mapped department, the "部门加班人员" area SHALL list the staff names for
the requested date.

- Names with status `bg-2` (internal overtime) SHALL be rendered normally (no
  underline)
- Names with status `bg-3` (business trip) SHALL be rendered with underline

#### Scenario: Status is reflected in name styling
- **WHEN** a department has one `bg-2` staff and one `bg-3` staff for the export
  date
- **THEN** the `bg-2` name is not underlined and the `bg-3` name is underlined

### Requirement: Remark count equals the number of internal overtime staff
For each mapped department, the "备注" field SHALL equal the count of staff with
status `bg-2` for the requested date.

#### Scenario: Remark count is computed from bg-2 only
- **WHEN** a department has 3 staff with `bg-2` and 2 staff with `bg-3` for the
  export date
- **THEN** the "备注" field for that department is `3`

### Requirement: Department isolation does not affect export
The export endpoint SHALL generate a full-table export and MUST NOT be filtered
by any department isolation cookie.

#### Scenario: Export ignores department cookie
- **WHEN** the client requests an export while sending a `department` cookie
- **THEN** the returned document still includes all template departments (mapped
  and unmapped)

### Requirement: Invalid date requests are rejected
The endpoint MUST validate the `date` query parameter.

#### Scenario: Missing or invalid date
- **WHEN** the client requests `/api/exports/overtime-table` without `date` or
  with an invalid date string
- **THEN** the server responds with HTTP 400 and a JSON error message
