# Purpose

Define the expected frontend behavior for initiating overtime table export from
the homepage, including weekday selection defaults and browser download flow.

# Requirements

## ADDED Requirements

### Requirement: Homepage exposes a "制表" entrypoint
The homepage SHALL display a button labeled "制表" that is available without
additional protection.

#### Scenario: Button is visible
- **WHEN** a user visits the homepage
- **THEN** the "制表" button is visible and clickable

### Requirement: Clicking "制表" opens a weekday-selection modal
The UI SHALL open a modal dialog containing weekday checkboxes (周一..周日) and
actions to confirm or cancel.

#### Scenario: Modal opens with weekday options
- **WHEN** the user clicks the "制表" button
- **THEN** a modal appears with 7 weekday checkboxes and a confirm action

### Requirement: Default checkbox selection follows the specified rules
The modal MUST apply the following default selection based on the local day of
week at open time:

- If today is Friday: default select Saturday and Sunday
- Else if today is Saturday: default select Sunday
- Else: no default selections

#### Scenario: Friday defaults
- **WHEN** the modal is opened on a Friday
- **THEN** Saturday and Sunday checkboxes are preselected

#### Scenario: Saturday defaults
- **WHEN** the modal is opened on a Saturday
- **THEN** Sunday checkbox is preselected and Saturday is not preselected

### Requirement: Confirm triggers one download per selected weekday
On confirm, the UI SHALL request an export for each selected weekday and trigger
a browser download for each response.

The request MUST call `GET /api/exports/overtime-table?date=YYYY-MM-DD` with a
concrete calendar date.

#### Scenario: Multiple selected days download multiple files
- **WHEN** the user selects Saturday and Sunday and confirms
- **THEN** the browser initiates two downloads (one per selected day)

### Requirement: Weekday selection resolves to the next matching calendar date
For each selected weekday, the UI MUST compute the export date as the next
occurrence of that weekday on or after today (in local time), within the next 7
days.

#### Scenario: Friday selecting Saturday
- **WHEN** today is Friday and the user selects Saturday
- **THEN** the requested `date` is tomorrow's calendar date

### Requirement: Confirm with no selection is prevented
If no weekdays are selected, the UI MUST prevent confirming the export.

#### Scenario: No selection
- **WHEN** the user opens the modal, selects nothing, and attempts to confirm
- **THEN** no export requests are sent and the UI indicates a selection is
  required
