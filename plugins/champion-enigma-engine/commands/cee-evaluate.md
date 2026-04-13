---
name: cee-evaluate
description: Run an end-to-end Champion Enigma Engine evaluation on an athlete. Integrates VCA / PD / PP outputs into a full readout with feasibility tags and caveats.
---

# /cee-evaluate

Invoke the `cee-evaluator` agent to produce a CEE readout.

## Usage

```
/cee-evaluate athlete=<id>
/cee-evaluate athlete=<id> mode=daily-readiness
/cee-evaluate athlete=<id> mode=scouting
/cee-evaluate athlete=<id> mode=clutch-profile
```

## Modes

- **daily-readiness** (default) — today's physical / mental / focus readout with recommendations.
- **scouting** — draft-prospect evaluation combining what's available (often broadcast-footage VCA + public psych + combine cognitive). Heavier caveat footprint.
- **clutch-profile** — pressure-response profile from historical observations; requires ≥ 20 pressure moments in the record.
- **full** — all-up readout including longitudinal resilience trajectory (requires ≥ 60 days of data).

## Output

Markdown report using the `cee-evaluator` agent's template. Every metric is feasibility-tagged (Feasible / Emerging / Speculative). Missing inputs are explicit.

## Rules

- If required data is absent, the command returns "insufficient data for {mode}" rather than a degraded report.
- No evaluation output is final training or scouting authority — it's decision-support for human staff.
- For minor athletes, add `--consent-confirmed` flag; the command refuses without it.
