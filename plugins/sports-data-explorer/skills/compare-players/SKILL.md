---
name: compare
description: Compare two sports players side-by-side with advanced stats and contextual analysis
argument-hint: <player-a> vs <player-b> [season|career]
allowed-tools: [Read, Bash, Grep]
---

# Compare Players

Side-by-side player comparison with advanced statistics and contextual analysis.

## Arguments

The user invoked this with: $ARGUMENTS

Expected format: `/compare <player-a> vs <player-b> [season|career]`

- `player-a` — First player name
- `player-b` — Second player name
- `season|career` — Optional. Specify a year (e.g., `2025`) or `career` for career totals. Default: current season.

## Instructions

When this command is invoked:

1. Parse both player names and the optional time frame
2. Determine the sport from the players (or ask if ambiguous)
3. Retrieve stats for both players
4. Present a side-by-side comparison

## Output Format

### Baseball Comparison
```
⚾ Player Comparison — 2025 Season

                    Mike Trout          Aaron Judge
  Team              LAA                 NYY
  Position          CF                  RF
  Age               33                  33
  ─────────────     ──────────────      ──────────────
  AVG               .278                .292
  OBP               .385                .398
  SLG               .555                .638
  OPS               .940                1.036
  HR                32                  52
  wOBA              .380                .418
  wRC+              148                 182
  BABIP             .305                .312
  WAR               5.4                 8.2
  ─────────────     ──────────────      ──────────────
  Edge                                  ✓ Judge
```

### Football Comparison
```
🏈 Player Comparison — 2025 Season

                    Jalen Hurts         Lamar Jackson
  Team              PHI                 BAL
  Position          QB                  QB
  ─────────────     ──────────────      ──────────────
  Pass Yds          3,800               3,400
  Pass TD           28                  24
  INT               8                   6
  Rush Yds          550                 820
  Rush TD           10                  6
  Passer Rating     98.5                102.3
  QBR               72.1                75.8
  ─────────────     ──────────────      ──────────────
  Edge              Mixed               Mixed
```

## Notes

- Highlight the winner in each category
- Provide a summary verdict with reasoning
- Note context like games played, injury time missed, or team quality differences
- For college players, note conference strength differences

## Example Usage

```
/compare Mike Trout vs Aaron Judge 2025
/compare Jalen Hurts vs Lamar Jackson career
/compare Ivan Melendez vs Jace Jung college-career
```
