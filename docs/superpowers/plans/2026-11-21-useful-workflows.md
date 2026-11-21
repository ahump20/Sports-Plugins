# Useful Sports Workflows Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for isolated implementation and independent review. Steps use checkbox syntax for tracking.

**Goal:** Add Roster Watch and Playoff Lab and make both sports repositories accurately explain what users can run.

**Architecture:** Two independent Python packages follow the existing plugin structure. The root coordinator owns catalogs, shared docs, package checks and GitHub delivery; each implementer owns only its new plugin directory.

**Tech Stack:** Python 3.9+ standard library; existing Node 22.12+ validation and TypeScript tooling.

**Spec:** ../specs/2026-11-21-useful-workflows-design.md

## Global constraints

- Preserve the seven current packages, existing endpoint configuration and source history.
- New packages require no API key or paid runtime.
- Snapshot data and examples must be explicitly attributed or labeled synthetic.
- Record and report data limitations; no invented transfers, probabilities or league rules.
- Git branches and pull requests only for repository changes. Do not merge or release during this task.

## Review focus

- Identity collisions and partial roster coverage must not produce false departure claims.
- Changed or omitted fields must remain distinguishable from explicit nulls.
- Ties at a playoff cutoff require ranges unless a complete declared tiebreak order resolves them.
- Contradictory or incomplete schedules must fail instead of producing confident postseason conclusions.
- Malformed inputs and output path collisions must fail cleanly without destroying source data.

## Task 1: Roster Watch

**Files:** Create only `plugins/roster-watch/` including `skills/roster-diff/scripts/roster_diff.py`, tests, example inputs and input contract.

**Interfaces:** CLI takes before and after JSON snapshots and emits JSON or Markdown. `compare_rosters(before, after)` returns the same report used by both renderers. The implementer documents exact field names in the input contract.

- [x] Write and run failing tests for additions, absences, field changes, ambiguous IDs, partial coverage and scope/time mismatch.
- [x] Implement comparison, strict validation, Markdown rendering and safe CLI file output.
- [x] Add manifests, skill, labeled examples and README; run Skill Creator validation and plugin tests.
- [x] Independently review and run extracted-archive examples.

## Task 2: Playoff Lab

**Files:** Create only `plugins/playoff-lab/` including `skills/playoff-scenarios/scripts/playoff_scenarios.py`, tests, example input and input contract.

**Interfaces:** CLI takes one league snapshot with optional winner constraints and emits JSON or Markdown. Deterministic enumeration returns seed and qualification bounds from the declared league policy.

- [x] Write and run failing tests against hand-computable leagues, cutoff ties, forced outcomes, unsupported settings and schedule inconsistencies.
- [x] Implement validated bounded enumeration and safe CLI output.
- [x] Add manifests, skill, labeled example and README; run Skill Creator validation and plugin tests.
- [x] Independently review and run extracted-archive examples.

## Task 3: Documentation and integration

**Files:** Root README, CONTRIBUTING, docs/CONTRIBUTING, docs/USE-CASES, both marketplace catalogs, package metadata, catalog contract test, project scorecard and roadmap. Companion repository: README, package metadata and workflow documentation.

- [x] Rewrite discovery around verified user jobs and document the two repos' distinct roles.
- [x] Register nine packages with exact catalog parity and update the count contract without relaxing validation.
- [x] Run both complete repository check commands and package extraction smoke tests.
- [x] Record evidence, limitations and sources in repository verification notes.
- [x] Update GitHub About text, push dedicated branches and open reviewable pull requests; verify remote heads and CI state.

Delivery: [Sports PR #26](https://github.com/ahump20/Sports-Plugins/pull/26) and [Texas PR #13](https://github.com/ahump20/Texas-Longhorns-Baseball-Intelligence/pull/13). Remote trees matched the local source. The initial Sports CI runner failure and platform correction are recorded in the dated verification note; latest checks remain attached to the PR.
