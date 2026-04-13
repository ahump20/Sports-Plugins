---
name: cbb-scout
description: Generate a scouting report for any NCAA DI college baseball team using live BSI MCP data.
arguments:
  - name: team
    description: Team slug (e.g. "texas", "lsu", "florida", "ole-miss") or full team name
    required: true
  - name: opponent
    description: Optional — if provided, produces a matchup-focused scouting report
    required: false
---

# /cbb-scout

Produces a scouting report on the named team using live data from the `cbb-sabermetrics` MCP.

## What it does

1. Calls `bsi_get_team_sabermetrics team={team}` for offensive and pitching advanced metrics.
2. Calls `bsi_get_standings conference={team's conference}` for position in league.
3. Calls `bsi_get_team_schedule team={team}` for recent form and next opponent.
4. Calls `bsi_get_conference_power_index` for SOS context.
5. If opponent provided, repeats 1 and 3 for opponent and runs matchup comparison.
6. Routes through the `college-baseball-intelligence` agent, applying the `interpreting-advanced-metrics` and `conference-strength` skills.

## Output format

Without opponent: structured scouting report
- Program context (conference, current record, PI rank)
- Offensive profile (team wRC+, ISO, BB%, K%, key hitters)
- Pitching profile (team FIP, ERA−, K%, BB%, staff leaders)
- Recent form (last 10 games, run differential)
- Next up (opponent, date, venue)
- Source attribution and timestamps

With opponent: matchup preview
- Both teams' profiles side-by-side
- Matchup edges (offense vs their pitching, their offense vs the defense)
- Historical series context if available
- One-sentence analytical call

## Example

```
/cbb-scout texas
```

Returns the Texas Longhorns' current scouting profile.

```
/cbb-scout texas opponent=arkansas
```

Returns a Texas vs Arkansas matchup preview.

## Quality gates applied

- Every statistic cited has source + timestamp from MCP `meta` envelope
- wRC+ and ERA− preferred over raw wOBA/ERA for cross-program framing
- SOS-adjustment applied when discussing record
- Season-state lens applied before drawing conclusions
