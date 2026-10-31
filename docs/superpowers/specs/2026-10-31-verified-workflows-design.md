# Sports-Plugins: verified workflows

## Goal
Expand the five-plugin catalog to seven with tested game-day packet and editorial evidence workflows, while hardening packaging and provenance.

## Design
Add gameday-ops with a standard-library Python JSON-to-game-packet CLI (scores, status, provenance, missing data). Add editorial-desk with a Python evidence-ledger validator/renderer (claims, source IDs, timestamps, quotations, calculations). Register both for Claude and Codex, preserve existing identities, and add native Codex catalog plus portable manifests. Validate referenced paths, skills, versions and catalog consistency. Label legacy numerical defaults as uncalibrated rather than changing published APIs without evidence.

## Constraints
Preserve existing package identities, historical assets, and unrelated work. No production deployment, credentials, purchases, or account-plugin publication. Work in an isolated staging clone. Use source-attributed inputs; never invent live statistics or empirical calibration. Regression tests must fail before implementation and pass afterwards. Native execution in this session; no paid model benchmark. Static Plugin Eval is not a behavioral or predictive benchmark.

## Approaches
A prompt-only expansion was rejected because recent repository cleanup explicitly removed unsupported tools. A broad application rewrite was rejected because these repositories own plugins and an analytical library, not production hosting. The selected approach adds small executable workflows and corrects demonstrated defects. This is the implementer’s choice under the user’s request to upgrade and finish the repositories.

## Acceptance
Existing tests remain green except corrections to demonstrably wrong historical assertions. New failure cases and CLI execution are tested. Package components are present and discoverable. Live-provider limitations are reported rather than substituted with sample data.
