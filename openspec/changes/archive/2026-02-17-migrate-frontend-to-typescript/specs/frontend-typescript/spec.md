## ADDED Requirements

### Requirement: Frontend uses TypeScript configuration
The frontend SHALL include a TypeScript configuration that supports Vue SFCs
and incremental migration of existing JavaScript files.

#### Scenario: TypeScript configuration present
- **WHEN** the frontend project is checked for configuration
- **THEN** a TypeScript config exists and allows Vue SFC typing with incremental
  adoption settings

### Requirement: Type checking is available as a command
The frontend SHALL provide a type-check command that validates TypeScript
without emitting build artifacts.

#### Scenario: Developer runs type check
- **WHEN** the frontend type-check script is executed
- **THEN** the command reports type errors and exits non-zero on failures

### Requirement: Mixed JS and TS sources are supported
The frontend SHALL support a codebase that includes `.js`, `.ts`, `.tsx`, and
Vue SFCs during migration without breaking the dev server or build.

#### Scenario: Existing JavaScript file remains in use
- **WHEN** a JavaScript module is imported by a TypeScript file
- **THEN** the application builds and runs without module resolution errors

### Requirement: Build output remains compatible
The frontend SHALL preserve the current build output location and proxy
behavior while TypeScript is enabled.

#### Scenario: Build and dev server run after TypeScript is enabled
- **WHEN** the frontend dev server and production build are executed
- **THEN** the dev proxy continues to route API calls and the build output is
  written to the existing output directory
