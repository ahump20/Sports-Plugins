---
name: texas-scout
description: Full Texas roster scouting breakdown — offensive and pitching profiles with HAV-F framework, position groups, key contributors.
arguments:
  - name: focus
    description: Optional — "offense" / "pitching" / "nil" / "draft" to narrow the scope
    required: false
---

# /texas-scout

Produces a full Texas roster scouting breakdown using live MCP data and Texas program doctrine.

## What it does

1. Calls `bsi_get_standings conference=SEC` and `bsi_get_team_schedule team=texas` for record, run differential and results
2. Calls `bsi_get_player_stats player={name} team=texas` for each Texas hitter and pitcher (names from the user or from `bsi_search_intel`, since no tool returns a roster)
3. Computes rate metrics (wOBA, ISO, BABIP, K%, BB%, FIP) from the returned counting stats with the baseball plugin's `saber.py`, as the `interpreting-advanced-metrics` skill sets out (wOBA, wRC+ and FIP need that season's Division I totals or are reported as not computable), stating formula and sample size; names any metric whose inputs weren't returned
4. Ranks Texas hitters and pitchers among the players pulled (no tool returns a leaderboard)
5. Routes through `texas-longhorns-baseball-intelligence` agent
6. Applies HAV-F framework to position-group breakdown

## Output format (default — full scouting)

### Team Identity
- Record, SEC position, conference context from standings
- Offensive and pitching profile in one paragraph each

### Offensive Core
- Top 3-5 hitters by computed wOBA among those pulled, with stat lines and PA
- HAV-F scoring applied
- Weaknesses in the lineup (position-group gaps)

### Pitching Core
- Rotation — starting pitcher quality, FIP separation
- Bullpen — late-innings depth, high-leverage reliever quality
- Arm count context if stretch-run

### Roster Gaps
- Positions needing portal or 2026 recruit attention
- Development priorities

### The Call
- Current program trajectory (ascending / holding / descending)
- Key variable watched over next 30 days

## Focus variations

### `/texas-scout focus=offense`
Offensive-only deep dive — lineup construction, approach breakdown, situational hitting.

### `/texas-scout focus=pitching`
Pitching-only deep dive — rotation depth, bullpen construction, usage patterns.

### `/texas-scout focus=nil`
NIL efficiency analysis — HAV-F to NIL ratio per player, Elite ROI identification, overpay flags, retention strategy.

### `/texas-scout focus=draft`
Draft prospect identification — 2026 MLB draft candidates on the roster, projected round, NIL-to-draft-leverage analysis.

## Examples

```
/texas-scout
```
→ Full roster scouting breakdown.

```
/texas-scout focus=nil
```
→ NIL efficiency analysis only.

```
/texas-scout focus=draft
```
→ MLB draft prospect identification.

## Quality gates applied

- HAV-F scoring applied to all named players
- Every stat line has source + timestamp
- Three-layer separation: Facts / Inference / Recommendation
- Weaknesses named directly — no hometown discount
- Program doctrine framed as context, not as proof of current-state quality
- Roster gaps identified with portal/recruit implications
