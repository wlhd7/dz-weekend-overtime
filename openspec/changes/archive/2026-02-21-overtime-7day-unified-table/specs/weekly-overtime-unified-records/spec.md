## ADDED Requirements

### Requirement: Store unified weekly status per staff
The system SHALL store overtime status for each staff member in a single record with fields `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`.

#### Scenario: Default status
- **WHEN** a staff member has no overtime data recorded
- **THEN** each day value is `bg-1`

### Requirement: One weekly record per staff
The system SHALL maintain a single overtime record per staff member.

#### Scenario: Repeated updates
- **WHEN** the same staff member updates multiple days across the week
- **THEN** the updates modify the same record rather than creating additional records

### Requirement: Update a single day status
The system SHALL update the specified day field with the requested status token (`bg-1`, `bg-2`, `bg-3`) for the targeted staff member.

#### Scenario: Set overtime status
- **WHEN** a request sets `day` to `tue` with status `bg-2`
- **THEN** the staff record stores `tue = bg-2` and other day values are unchanged

### Requirement: Clear overtime status
The system SHALL clear overtime for a day by setting the day field to `bg-1` without deleting the staff record.

#### Scenario: Clear status
- **WHEN** a request sets `day` to `fri` with status `bg-1`
- **THEN** the staff record stores `fri = bg-1`

### Requirement: Return weekly status per staff
The system SHALL return overtime statuses for all seven days for each staff member in the status retrieval endpoint.

#### Scenario: Fetch weekly status
- **WHEN** the status endpoint is requested for a department
- **THEN** each staff entry includes `mon` through `sun` status tokens
