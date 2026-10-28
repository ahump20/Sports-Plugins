---
name: cbb-leaderboard
description: Build a ranked list of DI players or teams by an advanced metric, computed from stats pulled live from the BSI MCP.
arguments:
  - name: metric
    description: Metric to rank by. Options — hitters — wrc_plus, woba, iso, babip, k_rate, bb_rate. Pitchers — fip, era_minus, k_rate, bb_rate, whip
    required: true
  - name: type
    description: "batting" or "pitching" or "team"
    required: true
  - name: conference
    description: Optional — filter to one conference (SEC, ACC, Big 12, Big Ten, etc.)
    required: false
  - name: limit
    description: Number of entries to return (default 10, max 50)
    required: false
---

# /cbb-leaderboard

Builds a ranked list by advanced metric from players or teams it actually pulls from the BSI MCP. The BSI server no longer returns a ranked leaderboard: that route is paused until its source, method and sample boundaries are documented. So this command never presents a national or conference leaderboard it did not build itself.

## What it does

1. Decides which players or teams to pull. The user names them, or the command takes teams from `bsi_get_rankings` (Top 25) or `bsi_get_standings conference={conference}` (teams in a conference). No tool returns a roster, so for player lists the user names the players, or `bsi_search_intel` is used to find names to look up.
2. For `type=batting` or `type=pitching`, calls `bsi_get_player_stats player={name} team={team}` for each player and takes the traditional counting stats returned.
3. For `type=team`, calls `bsi_get_standings conference={conference}` for W, L, run differential and runs scored or allowed, and `bsi_get_team_schedule team={team}` for game results.
4. Computes the metric from those counting stats with the baseball plugin's `saber.py`, as the `interpreting-advanced-metrics` skill sets out (wOBA, wRC+ and FIP need that season's Division I totals or are reported as not computable), and states the formula and sample size (PA for hitters, BF for pitcher K% and BB%, IP for FIP and ERA) next to each value.
5. If a metric needs a stat the source did not return (for example HBP or SF for wOBA, or league and park constants for wRC+ and ERA-), says that metric cannot be computed for that player instead of estimating it.
6. Routes through the `college-baseball-intelligence` agent and applies the `interpreting-advanced-metrics` skill to contextualize numbers.
7. Formats the output as a ranked table.

## Output format

A markdown table:

| Rank | Player / Team | Primary Metric (computed) | Sample (PA / BF / IP) | Key Context Stats |
|---|---|---|---|---|

Headed by one line saying the list covers only the players or teams pulled for this request, not all of DI.

Followed by a brief analytical note:
- What the leaderboard says (e.g., "SEC dominates the top — 6 of top 10")
- Any early-season caveats (e.g., small sample for Feb rankings)
- Notable omissions or surprises

## Examples

```
/cbb-leaderboard metric=wrc_plus type=batting limit=10
```
→ Top 10 by wRC+ among the hitters pulled, or a note that wRC+ cannot be computed if the league and park constants are not available.

```
/cbb-leaderboard metric=fip type=pitching conference=SEC limit=15
```
→ SEC pitchers pulled for this request, ranked by computed FIP.

```
/cbb-leaderboard metric=woba type=team conference=ACC
```
→ ACC teams ranked by what the standings and schedules support (runs scored per game, run differential). Team wOBA is computed only if team counting stats are returned.

## Quality gates applied

- Every computed value shows its formula and sample size
- Metrics whose inputs were not returned are named as not computable, never estimated
- The list is labeled as covering only the players or teams pulled
- Every entry has source + timestamp from the MCP `meta` envelope
- Early-season caveats surfaced when applicable
