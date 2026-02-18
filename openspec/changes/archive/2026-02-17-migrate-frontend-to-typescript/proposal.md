## Why

The frontend codebase is still in JavaScript, which slows refactoring and
increases runtime bugs as the UI and data flows grow. Moving to TypeScript
now improves safety and developer velocity while the surface area is still
manageable.

## What Changes

- Adopt TypeScript for frontend source code and type-checking as part of the
  frontend workflow.
- Migrate existing frontend modules from `.js` to `.ts/.tsx` where applicable.
- Introduce or update tooling needed to compile and validate TypeScript.

## Capabilities

### New Capabilities
- `frontend-typescript`: Define TypeScript usage standards, build integration,
  and type-checking expectations for the frontend.

### Modified Capabilities
- None.

## Impact

- Frontend source files under `frontend/` and any bundling or build scripts.
- Developer workflows (lint/type-check commands) and CI configuration.
- Potential updates to documentation for frontend setup and contribution.
