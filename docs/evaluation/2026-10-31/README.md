# Plugin Eval: October 31, 2026

These are static heuristic scores from installed Plugin Eval 0.1.2, not model behavior, factual accuracy, predictive quality, measured tokens, or a public-directory approval. Full reports below retain all findings; local absolute paths are normalized for privacy.

| Plugin | Baseline | After | Grade | Remaining failing checks |
|---|---:|---:|---|---:|
| [baseball](after-baseball.json) | 7 | 35 | F | 4 |
| [basketball](after-basketball.json) | 0 | 26 | F | 4 |
| [cbb-sabermetrics](after-cbb-sabermetrics.json) | 67 | 81 | C | 1 |
| [editorial-desk](after-editorial-desk.json) | new | 44 | F | 3 |
| [football](after-football.json) | 0 | 21 | F | 5 |
| [gameday-ops](after-gameday-ops.json) | new | 49 | F | 3 |
| [texas-longhorns-intel](after-texas-longhorns-intel.json) | 72 | 81 | C | 1 |

## Interpretation

The new scripts and revised libraries pass their deterministic tests, but the static evaluation is not fully green. The evaluator still penalizes estimated loading costs, Python function complexity or long lines, and missing public-listing privacy/terms URLs in several local-only packages. Those results are retained, not suppressed. Missing optional publication metadata is not evidence that a local calculation failed, and passing calculations is not evidence that publication requirements are complete.

No legal policies were invented merely to increase a score. No paid model benchmark, fresh-chat trigger benchmark or prediction calibration was performed. Some legacy context files remain large and should be assessed against actual usage before further compression.

## Evaluator compatibility correction

The installed evaluator crashes when a valid legacy `interface.defaultPrompt` is a string. A staging copy, not the installed tool, used this one-line normalization in `src/core/budget.js`:

```diff
- (manifest?.interface?.defaultPrompt || []).join("\n")
+ [manifest?.interface?.defaultPrompt || []].flat().join("\n")
```

Both before and after runs used that same correction. It normalizes string-or-array prompts for token estimation; it does not change package contents, deductions, thresholds or grading. Reproduce with the installed evaluator copied into a temporary directory, apply that change, then run:

```bash
node /path/to/copied/plugin-eval/scripts/plugin-eval.js analyze plugins/gameday-ops --format json
```

The `before-*.json` files are baseline reports for the original five packages. The `after-*.json` files cover all seven. Source files, scripts, deterministic tests and package validators are separate evidence and must not be substituted for model-based skill testing.
