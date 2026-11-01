# Plugin evaluation follow-up, November 1, 2026

These seven reports are static analysis, not measured sports-answer quality. The installed Plugin Eval plugin release is 0.1.2; its internal package and report version are 0.1.0. As documented in the [earlier report](../2026-10-31/README.md), a temporary copy needs one string-or-array prompt compatibility correction. The installed plugin was not edited. Source/evaluator paths alone are replaced by placeholders; findings, deductions and summary counts are retained.

| Plugin | Static score | Remaining failing checks |
|---|---:|---|
| baseball | 54 | Listing privacy policy and terms URLs |
| basketball | 45 | Listing privacy policy and terms URLs |
| cbb-sabermetrics | 100 | None |
| editorial-desk | 58 | Listing privacy policy and terms URLs |
| football | 49 | Listing privacy policy and terms URLs |
| gameday-ops | 58 | Listing privacy policy and terms URLs |
| texas-longhorns-intel | 100 | None |

Read each JSON report for all warnings, including long functions, complexity and line lengths. The evaluator's informational count still double-counts checks with both severity and status `info`. Count the checks array for the actual number of informational findings.

Do not infer a measured improvement from the October score differences: the installed environment's budget baseline is external to these repositories and has changed. No baseline snapshot was pinned in the earlier run. These are current static outputs with the same documented compatibility correction, not a controlled before-and-after experiment.

Local-only calculation packages do not have newly invented legal URLs. Public-directory listing requirements remain open. The live NCAA package has existing policy links; an evaluator score does not verify their legal adequacy or source accuracy. No directory approval is claimed.

The [50-request benchmark catalog](../../benchmarks/real-requests-v1.json) starts with every case `not_run`. Native host install/invocation checks and standalone CLI tests are separate evidence; neither replaces the full substantive source-review benchmark.

To reproduce, copy the installed evaluator to a temporary directory, apply the exact correction in the earlier README, then run from this repository:

```bash
node /path/to/copied/plugin-eval/scripts/plugin-eval.js start plugins/editorial-desk --request 'Evaluate this plugin.' --format markdown
node /path/to/copied/plugin-eval/scripts/plugin-eval.js analyze plugins/editorial-desk --format json
```
