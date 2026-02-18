## Context

The frontend is a Vue 3 + Vite application in `frontend/` and currently uses
JavaScript (`main.js`, Vue SFCs without `lang="ts"`). The proposal calls for
TypeScript adoption to improve safety and refactoring speed while keeping the
existing build and deployment flow (Vite build outputs into the backend static
directory).

## Goals / Non-Goals

**Goals:**
- Enable TypeScript in the frontend toolchain (type-checking and build).
- Support incremental migration of existing files from `.js` to `.ts/.tsx`
  and Vue SFCs to `script lang="ts"`.
- Keep the current Vite build output and dev server proxy behavior intact.

**Non-Goals:**
- Rewriting the entire frontend in one pass.
- Changing the frontend framework or replacing Vite.
- Refactoring application behavior beyond what is needed for typing.

## Decisions

- **Adopt incremental TypeScript migration.**
  Rationale: minimizes disruption by allowing a mix of JS and TS files while
  type coverage grows. Alternative: full rewrite to TS first, which is higher
  risk and slows delivery.

- **Use `typescript` + `vue-tsc` for type-checking with `noEmit`.**
  Rationale: `vue-tsc` understands Vue SFCs and provides reliable type checks
  without changing the Vite build path. Alternative: use `tsc` only, which
  misses Vue template and SFC typing.

- **Add a dedicated `tsconfig.json` for the frontend with permissive settings
  initially (e.g., `allowJs: true`, `checkJs: false`, `skipLibCheck: true`).**
  Rationale: enables TS adoption without blocking on legacy JS. Alternative:
  strict-only configuration from day one, which may stall migration due to
  large error surfaces.

- **Convert core entry points first (`main.js`, router, stores, utilities).
  Vue SFCs migrate as they are touched.**
  Rationale: provides early confidence in routing/state typing while avoiding
  a massive diff. Alternative: random file-by-file conversion, which increases
  churn and review complexity.

## Risks / Trade-offs

- **Mixed JS/TS codebase** -> Establish clear migration rules and update the
  contribution guide to prefer TS for new files.
- **Type-check noise during migration** -> Start with permissive tsconfig and
  tighten over time after the initial migration is stable.
- **Build/tooling regressions** -> Validate `vite build` and dev server proxy
  after introducing TS dependencies and configuration.

## Migration Plan

- Add TypeScript dependencies (`typescript`, `vue-tsc`) to `frontend/`.
- Create `frontend/tsconfig.json` and Vue shim declarations for SFC typing.
- Rename `main.js` to `main.ts` and update imports where necessary.
- Migrate router, store, and shared utilities to `.ts`.
- Convert Vue SFCs to `script lang="ts"` opportunistically and resolve typing
  issues as they appear.
- Add a `typecheck` script (e.g., `vue-tsc --noEmit`) to the frontend scripts.

## Open Questions

- Should we enforce stricter TypeScript settings after the initial migration
  (and if so, which ones)?
- Do we want to introduce path aliases (e.g., `@/`) as part of the migration
  or keep current relative imports for now?
