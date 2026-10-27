---
name: texas-matchup
description: Pre-series matchup preview for Texas vs any SEC or non-conference opponent. Pulls both teams' live standings, results and player stats and produces an opponent intelligence brief.
arguments:
  - name: opponent
    description: Opponent team slug (e.g. "arkansas", "lsu", "ole-miss", "tennessee") or full team name
    required: true
  - name: venue
    description: Optional — "home" or "away" to factor park adjustments
    required: false
---

# /texas-matchup

Generates an opponent-intelligence brief for an upcoming Texas series using live MCP data and the Opponent Intelligence framework.

## What it does

1. Calls `bsi_get_team_schedule team=texas` and `bsi_get_team_schedule team={opponent}` in parallel (recent form, series date)
2. Calls `bsi_get_standings` for both teams' conferences (record, runs scored and allowed, run differential, position)
3. Calls `bsi_get_rankings` and applies the `conference-strength` skill for conference context computed from standings
4. Calls `bsi_get_player_stats` for each side's key hitters and pitchers and computes rate metrics (ISO, K%, BB%, FIP) from the returned counting stats, with formula and sample size
5. If the series is on the scoreboard, calls `bsi_get_match_detail matchId={id}` for venue, weather and win predictions
6. Routes through the `texas-longhorns-baseball-intelligence` agent using the `scoutingReport` output mode
7. Applies the Opponent Intelligence framework for structured brief

## Output format

Structured matchup brief:

### Opponent Profile
- Conference, current record, conference position, Top 25 rank if any
- Offensive identity (runs scored per game, key hitters' computed ISO and approach)
- Pitching identity (runs allowed per game, staff computed FIP, strengths and weaknesses)
- Recent form (last 10 games, run differential)

### Texas vs Opponent — Edge Breakdown
- Texas offense vs their pitching staff
- Their offense vs Texas pitching
- Defensive matchup
- Bullpen health comparison
- Leverage / pressure situation edges

### Park Factor Context
- UFCU Disch-Falk (home) OR opponent's park factors
- How this adjusts the matchup

### Recent Head-to-Head
- Last series' results with context
- Historical series patterns if notable

### The Call
- One-sentence analytical take
- Confidence level (high / medium / low)
- Key variable to watch

### Source Attribution
- Every statistic's source and as-of timestamp

## Examples

```
/texas-matchup arkansas
```
→ Texas vs Arkansas matchup preview (location auto-detected from schedule).

```
/texas-matchup lsu venue=away
```
→ Texas at LSU matchup with Alex Box park factors applied.

```
/texas-matchup oregon-state venue=home
```
→ Texas vs Oregon State (non-conference) at UFCU Disch-Falk.

## Quality gates applied

- Both teams' data fetched live, never from memory
- Park context noted when venue known; numeric park factors used only with a documented source
- Conference context computed from standings and the Top 25 for cross-opponent comparison
- Three-layer separation: Facts / Inference / Recommendation
- No projection without stated confidence
- Missing data flagged, not papered over
