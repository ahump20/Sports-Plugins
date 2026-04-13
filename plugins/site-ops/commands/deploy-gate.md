---
name: deploy-gate
description: Run the pre-deploy gate for a sports intelligence site. Checks typecheck, smoke tests, visual compliance, and clean git state before authorizing deploy.
---

# /deploy-gate

Pre-deploy gate. Must pass before `wrangler deploy` runs.

## Usage

```
/deploy-gate                      # full gate
/deploy-gate skip=smoke           # skip specific gate (not recommended)
/deploy-gate fast                 # typecheck + lint only (WIP pushes)
```

## Gates (in order)

1. **Git state** — `git status` must be clean. Uncommitted changes block the gate.
2. **Typecheck** — `npm run typecheck` must pass with zero errors.
3. **Lint** — `npm run lint` must pass.
4. **Test suite** — `npm run test:all` (Vitest). Playwright tests run separately.
5. **Smoke** — `npm run smoke:release` (homepage, layout, scores, mobile).
6. **CBB gate** — `npm run gate:cbb` (Playwright critical paths for college baseball).
7. **Visual compliance** — invoke `heritage-audit` against the top 3 landing URLs.
8. **Pre-deploy checks** — `npm run pre-deploy-check`.

## Output

Each gate reports ✅ / ❌ with the failing command and its output. On first failure, remaining gates do not run.

## Rules

- **Do not deploy from a dirty git state.** Commit first or explicitly justify the skip (requires `--force-dirty` flag).
- **Do not skip hooks** (`--no-verify`) without explicit authorization. Fix the hook failure instead.
- **Verification after deploy is still required.** The gate authorizes the deploy; it does not verify user-visible outcome. Run the post-deploy `health` check.

## Escalation

Gate failure → route the failure output to the appropriate agent:
- Typecheck / lint → `feature-dev:code-reviewer`
- Visual → `build-verify` for screenshot diff
- Smoke → `silent-failure-hunter` for the affected test
