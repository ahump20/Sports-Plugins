---
name: texas-matchup
description: Pre-series matchup preview for Texas vs any SEC or non-conference opponent. Pulls both teams' live sabermetrics and produces an opponent intelligence brief.
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

1. Calls `bsi_get_team_sabermetrics team=texas` and `bsi_get_team_sabermetrics team={opponent}` in parallel
2. Calls `bsi_get_team_schedule` for both teams (recent form)
3. Calls `bsi_get_conference_power_index` for conference context
4. Calls `bsi_get_standings conference=SEC` for current position
5. Routes through the `texas-longhorns-baseball-intelligence` agent using the `scoutingReport` output mode
6. Applies the Opponent Intelligence framework for structured brief

## Output format

Structured matchup brief:

### Opponent Profile
- Conference, current record, PI rank
- Offensive identity (team wRC+, ISO, approach)
- Pitching identity (team FIP, staff strengths and weaknesses)
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
- Park factors applied when venue known
- SEC PI context for cross-opponent comparison
- Three-layer separation: Facts / Inference / Recommendation
- No projection without stated confidence
- Missing data flagged, not papered over
