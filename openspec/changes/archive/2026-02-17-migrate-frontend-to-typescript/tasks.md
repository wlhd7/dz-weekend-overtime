## 1. Tooling setup

- [x] 1.1 Add TypeScript and `vue-tsc` dev dependencies in `frontend/package.json`
- [x] 1.2 Create `frontend/tsconfig.json` with incremental migration settings
- [x] 1.3 Add Vue SFC shim declarations for TypeScript
- [x] 1.4 Add a `typecheck` script to run `vue-tsc --noEmit`

## 2. Entry point migration

- [x] 2.1 Rename `frontend/src/main.js` to `frontend/src/main.ts`
- [x] 2.2 Update imports and bootstrap code to satisfy TypeScript

## 3. Core module migration

- [x] 3.1 Convert router modules under `frontend/src/router` to `.ts`
- [x] 3.2 Convert Pinia stores under `frontend/src/stores` to `.ts`
- [x] 3.3 Convert shared utilities under `frontend/src/utils` to `.ts`

## 4. Vue SFC migration

- [x] 4.1 Update key Vue SFCs to `script lang="ts"` as touched
- [x] 4.2 Resolve SFC typing issues for props/emits where needed

## 5. Validation

- [x] 5.1 Run `npm --prefix frontend run typecheck`
- [x] 5.2 Run `npm --prefix frontend run build` to verify output and proxy
