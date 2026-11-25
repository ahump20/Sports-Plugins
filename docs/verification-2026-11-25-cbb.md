# College baseball accuracy repair — November 25, 2026

## Scope

Sports-Plugins base: `78be4791a4bd769989850e8f0f7416270b7c156f`.
Dedicated branch: `fix/cbb-verified-data-20261125`.
Package version: `cbb-sabermetrics` **0.4.0**.

The package now has a working standalone official-page HTML source workflow,
season-aware research instructions and meaningful MCP data-contract checks.
The BSI remote worker is a separately owned/deployed component. Package source
changes, a merged PR and a successful local helper do not prove an account
installation or a production server release.

## Executed checks

Environment: Node **24.22.3**, Python **3.12.14**. Node dependencies installed
with `npm ci` from the existing lockfile.

| Check | Observed result |
|---|---|
| `npm run check` | Passed: typecheck, lint, 146 Node tests, 42 Vitest tests, Python suites and nine-package validation |
| New source-helper tests | 32 passed; source-backed snippets plus explicitly synthetic adverse cases |
| New MCP diagnostic tests | 20 passed, including a real local HTTP session with initialization, session/version headers and paginated discovery |
| Python suites in full check | 261 discovered; nine pre-existing opt-in live cases skipped; all executed tests passed |
| Claude marketplace validation | Passed with the available current Claude CLI; this is validation, not installation or invocation |
| Skill frontmatter validation | New college-baseball-data skill passed |
| Standalone ZIP | Extracted outside checkout; JSON/Markdown fixture commands, help and rejected wrong-season input behaved as documented |
| Official live HTML | Texas 2025 stats, roster and schedule returned HTTP 200 with matching visible season evidence |
| Deployed MCP before repair | Connectivity passed; seasonal data contract failed because v4.0.0 exposes no season inputs |

The full check's nine skipped live-source cases are not counted as successful
provider checks. The package's changed source paths were exercised independently
against the real official pages below.

## Real source observations

See [official-source-smoke.json](verification/2026-11-25/official-source-smoke.json)
for URLs, retrieval timestamps, content hashes, season evidence and table counts.

- Texas 2025 stats: five HTML tables; 16 individual batting rows plus two
  footer totals. Ethan Mendoza: 225 AB, 75 H, 107 TB. Raw published strings are
  preserved; OPS .913 is kept distinct from derived raw-count OPS .9121227.
- Texas 2025 roster: 41 player rows, two separately marked advertisement rows,
  five coaches and five support staff. No inference of eligibility is made.
- Texas 2025 schedule: 59 listed cards, including non-completed entries;
  published record 44–14 overall and 22–8 conference. Absent tie counts are null.

The helper does not authenticate a supplied HTML file, independently verify a
publisher, or promote requested team/division labels into verified identity.
Source statistical cutoff and completeness remain unknown unless established
separately. Texas's retrieved HTML exposes batting; it does not expose the full
pitching tab. Official cumulative PDFs and page/browser inspection remain useful.

The Texas 2025 summary widget conflicts with the detailed tables/PDF on opponent
AB and double plays. The helper preserves separate source sections and the
workflow requires reconciliation; it does not silently flatten the conflict.

## Live MCP defect reproduction

[live-contract-before.json](verification/2026-11-25/live-contract-before.json)
records the actual v4.0.0 catalog. Its four season-sensitive tools lack season
inputs. The old test only required nonempty response text, so even
`{"rankings":[]}` passed. The replacement separately checks connectivity,
catalog/schema, season/source/coverage metadata, usable rows and availability.

Direct pre-repair observations also showed incompatible Texas game totals
between standings and schedule, incomplete player counts with zero-filled
missing fields, and freshly stamped fetch metadata on older published polls.
Those observations motivate separate BSI worker/data-path fixes; this repository
does not claim that its package release deploys them.

## Review and release boundaries

Independent review tested the workflow with a mixed historical-stat/current-
roster request and reproduced diagnostic/parser edge cases. Findings were fixed
and retained as regression tests. Static Plugin Eval reports are included with
their limitations in [the evaluation note](evaluation/2026-11-25/README.md).

The source package can be reviewed and merged after required repository checks.
No production deployment, tagged publication, account-plugin replacement or
host installation is claimed by this verification record. The strict live-data
gate remains failing on the old deployed server until a verified backend release
can satisfy it; no test was weakened to hide that result.
