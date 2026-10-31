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

1. Calls `bsi_get_standings conference={team's conference}` for record, run differential, streak and position in league.
2. Calls `bsi_get_team_schedule team={team}` for recent form and next opponent.
3. Calls `bsi_get_rankings` for national rank, if any.
4. Calls `bsi_get_player_stats player={name} team={team}` for the key hitters and pitchers (names from the user or from `bsi_search_intel`), and computes rate metrics such as ISO, BABIP, K%, BB% and FIP from the returned counting stats, with formula and sample size. Metrics whose inputs were not returned are named as not computable.
5. Optionally calls `bsi_search_intel query="{team} baseball"` for injury, lineup and scouting news.
6. If opponent provided, repeats 1 to 4 for opponent and runs matchup comparison. If a scoreboard `matchId` for the game is available, `bsi_get_match_detail` adds venue, weather and win predictions.
7. Routes through the `college-baseball-intelligence` agent, applying the `interpreting-advanced-metrics` and `conference-strength` skills.

## Output format

Without opponent: structured scouting report
- Program context (conference, current record, conference position, Top 25 rank if any)
- Offensive profile (runs scored per game, key hitters with computed rate metrics)
- Pitching profile (runs allowed per game, staff leaders with computed FIP, K%, BB%)
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

- Every statistical claim records source, season and coverage; retrieval time alone is insufficient
- Computed metrics show formula and sample size; none are estimated when inputs are missing
- Record framed with conference context from standings, without claiming a strength-of-schedule adjustment
- Season-state lens applied before drawing conclusions

If a requested field or tool is unavailable, state that limitation. A provider win prediction, when returned, is not a prediction calibrated by this plugin.
