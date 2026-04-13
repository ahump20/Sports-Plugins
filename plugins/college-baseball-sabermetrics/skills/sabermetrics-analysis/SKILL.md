---
name: sabermetrics-analysis
description: Use when the task involves computing, interpreting, or displaying advanced baseball statistics for college teams or players. Covers rate stats, context-neutral metrics, park and era adjustments (where applicable in NCAA), and narrative generation from raw numbers.
---

# Sabermetrics Analysis

Use this skill when quality depends on correctly computing and contextualizing advanced baseball metrics rather than raw counting stats. The goal is to produce analysis that is analytically grounded, readable to an educated fan, and specific enough to be actionable for a coaching staff or content team.

## Working Model

Before computing or displaying any metric, establish three things:

- sample size context: how many plate appearances, innings pitched, or games are in the dataset?
- data source: NCAA stats, Baseball Reference, BSI pipeline, or manual entry?
- comparison baseline: conference average, national percentile, or historical program benchmark?

Metrics without context are noise. Always pair a number with a frame of reference.

## Core Metric Definitions

### Pitching

| Metric | Formula / Notes |
|--------|----------------|
| ERA | (ER / IP) × 9 |
| FIP | ((13×HR + 3×(BB+HBP) − 2×K) / IP) + FIP constant (~3.10 for NCAA) |
| xFIP | FIP but replaces HR with expected HR based on FB% and park HR/FB rate |
| WHIP | (BB + H) / IP |
| K/9 | (K / IP) × 9 |
| BB/9 | (BB / IP) × 9 |
| K/BB | K / BB |
| K% | K / BF |
| BB% | BB / BF |
| BABIP | (H − HR) / (AB − K − HR + SF) |
| Strand Rate (LOB%) | (H + BB + HBP − R) / (H + BB + HBP − 1.4×HR) |
| HR/9 | (HR / IP) × 9 |
| GB% / FB% / LD% | Batted-ball distribution by type |

### Hitting

| Metric | Formula / Notes |
|--------|----------------|
| AVG | H / AB |
| OBP | (H + BB + HBP) / (AB + BB + HBP + SF) |
| SLG | TB / AB |
| OPS | OBP + SLG |
| ISO | SLG − AVG |
| BABIP | (H − HR) / (AB − K − HR + SF) |
| wOBA | Weighted on-base average using linear weights (college calibrated) |
| wRC+ | wRC scaled to 100 = league average; above 100 is above average |
| BB% | BB / PA |
| K% | K / PA |
| Contact% | (PA − K) / PA (approximation without Statcast) |

## NCAA Data Considerations

- **No Statcast**: exit velocity, launch angle, spin rate, and pitch-tracking data are generally unavailable at the college level unless sourced from Yakkertech or a school's own Trackman/Hawkeye setup.
- **Small samples matter more**: College seasons are 55–65 games. 100 PA is a meaningful threshold; 50 PA is borderline.
- **Park factors**: College parks vary wildly. Do not compare raw HR totals across programs without park context. Use conference-relative comparisons when park data is absent.
- **Weekday vs. weekend splits**: Midweek starters face different competition. Flag midweek-only samples clearly.
- **Transfer portal volatility**: Rosters change substantially year to year. Always verify current roster status before projecting.

## Metric Interpretation Guidelines

### Pitching tiers (college baseline)

| Metric | Elite | Above Avg | Average | Below Avg |
|--------|-------|-----------|---------|-----------|
| ERA | < 2.50 | 2.50–3.50 | 3.50–4.50 | > 4.50 |
| FIP | < 2.80 | 2.80–3.60 | 3.60–4.50 | > 4.50 |
| K/9 | > 11.0 | 9.0–11.0 | 7.0–9.0 | < 7.0 |
| BB/9 | < 2.0 | 2.0–3.0 | 3.0–4.0 | > 4.0 |
| WHIP | < 1.00 | 1.00–1.20 | 1.20–1.40 | > 1.40 |

### Hitting tiers (college baseline)

| Metric | Elite | Above Avg | Average | Below Avg |
|--------|-------|-----------|---------|-----------|
| wRC+ | > 140 | 115–140 | 85–115 | < 85 |
| OPS | > .950 | .850–.950 | .720–.850 | < .720 |
| ISO | > .220 | .160–.220 | .100–.160 | < .100 |
| BB% | > 14% | 10–14% | 6–10% | < 6% |
| K% | < 16% | 16–22% | 22–28% | > 28% |

## Narrative Generation Rules

When converting metrics into prose:

- Lead with the most decision-relevant finding, not the most impressive number.
- Use one sentence to state what the metric is, one sentence to say what it means for this player/team.
- Avoid stacking more than three metrics in a single paragraph.
- Flag sample-size caveats inline: "through 12 starts (64 IP)".
- Comparisons should be specific: "better than 80% of Big 12 starters" beats "above average".
- Do not editorialize beyond what the data supports. "FIP is 0.8 runs better than ERA, suggesting luck on batted balls" is fine. "He will be an ace" is not.

## Hard Rules

- Never present FIP or xFIP without stating the sample size in innings pitched.
- Never compare raw ERA across programs without park context.
- Never omit opponent-quality context for a pitcher with an outlier ERA.
- Never show wRC+ or wOBA for a player with fewer than 40 PA as anything other than preliminary.
- Always include at least one counting stat alongside any rate stat to anchor the reader.
- When data is incomplete, say so explicitly rather than leaving gaps silently.

## Texas Longhorns Context

When the subject is Texas baseball specifically:

- The primary comparison baseline is Big 12 conference pitching and hitting averages.
- Weekend starters (typically three Friday/Saturday/Sunday arms) should be evaluated separately from midweek depth.
- Disch-Falk Field is a hitter-friendly environment in Austin heat; adjust ERA interpretation upward slightly in raw park reads.
- Track transfer portal adds and departures each offseason — roster continuity strongly predicts xFIP regression direction.
- Texas typically leads or competes for the Big 12 title; set expectations accordingly (compare against top-25 national programs, not just conference peers).
