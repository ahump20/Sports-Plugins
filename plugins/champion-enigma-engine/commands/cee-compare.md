---
name: cee-compare
description: Compare two athletes on CEE composite metrics. Produces a side-by-side with matched feasibility tags and explicit caveats where the comparison is weak.
---

# /cee-compare

Side-by-side CEE comparison.

## Usage

```
/cee-compare a=<athlete-id> b=<athlete-id>
/cee-compare a=<id> b=<id> dimensions=readiness,clutch,resilience
```

## What it does

1. Runs `cee-evaluate` on both athletes in the same mode.
2. Aligns cohort baselines — if A and B are in different leagues / age groups, flag the comparison as weakened.
3. Produces a table:

| Dimension | A | B | Delta | Feasibility | Caveat |
|---|---|---|---|---|---|
| Daily Readiness (composite) | 0.83 | 0.76 | +0.07 | Feasible | None. |
| Clutch Likelihood | 72% | 58% | +14pp | Emerging | Based on 23 vs. 31 observed pressure moments. |
| Cognitive Agility | 7.2 | 6.8 | +0.4 | Feasible | Different test batteries; normalization approximate. |

4. Produces a qualitative summary that explicitly avoids verdicts ("A > B"). Instead: "Across feasible dimensions, A shows moderately higher daily readiness; the emerging-tier clutch dimension shows a gap within overlapping confidence intervals — not decisive."

## Rules

- **Never produce a ranking winner.** Ranking implies certainty the feasibility tags don't support.
- **Never compare across feasibility tiers.** A Feasible readiness score and a Speculative killer-instinct score are not comparable.
- **Always surface cohort mismatches.** A Division I baseball player and a Division III player aren't directly comparable on most dimensions.

## Scouting use

When used for scouting, the comparison is one input among many. Game tape, stat lines, interviews, and medical data all remain primary inputs. CEE comparison adds a quantitative lens on intangibles, not a replacement for human scouting.
