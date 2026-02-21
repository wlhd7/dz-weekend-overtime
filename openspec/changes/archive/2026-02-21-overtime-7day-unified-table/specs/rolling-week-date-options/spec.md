## ADDED Requirements

### Requirement: Provide rolling 7-day options
The system SHALL provide a list of seven date options starting from tomorrow (current local date + 1) and continuing for the next six days.

#### Scenario: Initial list generation
- **WHEN** the overtime day selector is opened
- **THEN** the option list contains exactly 7 dates starting with tomorrow and ordered by ascending date

### Requirement: Label includes date and weekday
The system SHALL render each option label with the calendar date and weekday name.

#### Scenario: Label formatting
- **WHEN** an option is displayed for a given date
- **THEN** the label includes the date and the weekday name for that date

### Requirement: Option value uses weekday token
The system SHALL use the weekday token (`mon` to `sun`) as the option value for API requests.

#### Scenario: Selecting a date
- **WHEN** a user selects a date option
- **THEN** the selected value equals the weekday token for that date
