# Verified Workflows Implementation Plan

> Execution: superpowers:executing-plans, native implementation with test-first checkpoints.

**Goal:** Expand the five-plugin catalog to seven with tested game-day packet and editorial evidence workflows, while hardening packaging and provenance.

**Architecture:** Add gameday-ops with a standard-library Python JSON-to-game-packet CLI (scores, status, provenance, missing data). Add editorial-desk with a Python evidence-ledger validator/renderer (claims, source IDs, timestamps, quotations, calculations). Register both for Claude and Codex, preserve existing identities, and add native Codex catalog plus portable manifests. Validate referenced paths, skills, versions and catalog consistency. Label legacy numerical defaults as uncalibrated rather than changing published APIs without evidence.

**Tech Stack:** Existing TypeScript/Node test stack; Python standard library for portable plugin helpers.

**Spec:** ../specs/2026-10-31-verified-workflows-design.md

## Global Constraints
Preserve existing package identities, historical assets, and unrelated work. No production deployment, credentials, purchases, or account-plugin publication. Work in an isolated staging clone. Use source-attributed inputs; never invent live statistics or empirical calibration. Regression tests must fail before implementation and pass afterwards. Native execution in this session; no paid model benchmark. Static Plugin Eval is not a behavioral or predictive benchmark.

## Review Focus
Malformed or stale input must not become verified facts. Missing numeric values are not zero. Paths must stay inside packages. Failure and timeout must produce a non-success outcome. Offline fixtures must never be represented as live observations.

## Task 1
- [ ] Write failing package-contract and two CLI behavior tests; preserve all current suites.
## Task 2
- [ ] Use the installed Skill Creator initializer, implement game-day and editorial scripts, concise skills and input references; run scripts on test fixtures.
## Task 3
- [ ] Add compatible manifests and native marketplace; extend validation; run full check, quick_validate and before/after Plugin Eval.
## Task 4
- [ ] Inspect diff, record evidence and limitations, package each new plugin and save a review branch and pull request.
