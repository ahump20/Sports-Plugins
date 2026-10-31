# Sports Plugins: verified upgrade, October 31, 2026

## Scope

Expanded the working catalog from five to seven plugins and twelve to fourteen skills. Added executable game-day packets and editorial evidence ledgers rather than restoring the older prompt-only expansion. Existing baseball, football and basketball numerical implementations are retained. College/Texas instructions now distinguish observed statistics, defensible interpretation and unavailable models.

Package versions: root tools 1.1.0; marketplace 2.1.0; baseball/football/basketball 1.0.1; cbb-sabermetrics and texas-longhorns-intel 0.3.0; gameday-ops and editorial-desk 1.0.0. Package identity is preserved.

## Verified checks

| Check | Result |
|---|---|
| Node deterministic suites | 60 passed |
| Vitest numerical suites | 42 passed |
| Python skill suites | 152 passed; 9 existing network-dependent cases skipped |
| Total deterministic results | 254 passed; 9 skipped |
| TypeScript typecheck, ESLint and build | Passed |
| Custom package/catalog validator | Seven packages passed |
| Actual Skill Creator quick_validate.py | Fourteen skills passed |
| Actual Claude Code 2.1.316 plugin validator | Marketplace and all seven package manifests passed; advisory directory warnings remain |
| Standalone archive tests | Three passed, including byte-for-byte repeatability and unsafe-name rejection |
| Actual live MCP checks | Discovery plus live rankings, standings and schedule reads exercised |

The two new Python helpers each have ten tests, including actual CLI invocations. Fixtures are explicitly synthetic. Regression tests for missing executables, package contracts, instruction boundaries and archive construction were run failing before implementation. Existing math tests still use their repository's cited examples.

Skill Creator's installed initializer created both new skills. Its installed validator initially could not import PyYAML; the missing dependency was installed in an isolated validation environment, not in the product or global Python environment. Fourteen validations then passed. No product runtime dependency was added.

## Executable workflows

Game-day packets preserve null scores, distinguish scheduled/live/final/disrupted games, compute final outcomes only from complete final scores, retain provenance and flag retrieval freshness. They do not infer turning points, injuries or a complete season from an empty scoreboard.

Editorial ledgers check source IDs, exact quote/excerpt matches, supported arithmetic, timestamps and current-versus-historical scope. A complete ledger means documented, not independently true or approved to publish. Missing citations and division by zero cannot silently pass strict mode.

## Packaging and distribution

Portable root manifests coexist with Claude and Codex compatibility files. Native Codex and Claude catalogs list the same seven packages. Validation checks identities, versions, declared component files, skill discovery, MCP connection agreement and package-boundary path safety.

`python3 scripts/package-plugins.py` produces one plugin per ZIP with hidden manifests and a license notice, excluding caches and marketplace wrappers. Identical input produces identical bytes. GitHub CI is configured to save these packages and checksums as an artifact with seven-day retention. Configured CI upload is not a claim that a particular remote run completed; inspect the PR checks.

## Evaluation and limits

[Full before/after Plugin Eval reports](evaluation/2026-10-31/README.md) retain the heuristic failures and the documented evaluator compatibility correction. Static evaluation is **not fully green**. No observed token benchmark, independent model reviewer or fresh-chat skill invocation benchmark was run.

Host installation and public-directory publication were not performed. Missing public-listing metadata and advisory icon requirements remain outside this local-package delivery. No production deployment, paid API purchase, credential change or account-plugin publication occurred. The legacy four-plugin PR was left untouched.

The HTTP companion's [packaged live smoke result](verification/live-smoke-2026-10-31.json) preserves tool/provider timestamps. It is a finite observation, not continuous monitoring. Only catalog discovery and the named read paths were live-tested; all seven possible tool calls were not exercised.

## Reproduce

```bash
npm ci
npm run check
npm run build
claude plugin validate .
SPORTS_LIVE=1 node --test tests/blaze-mcp.test.mjs
python3 scripts/package-plugins.py --output ./dist/plugin-packages
```

Use the installed Skill Creator `quick_validate.py` against each `plugins/*/skills/*` directory in an environment with PyYAML. For each Python helper, run its own tests from its skill directory. See the evaluation report for the static evaluator reproduction note.
