---
name: cbb-leaderboard
description: Pull a ranked leaderboard of DI players or teams by any advanced metric.
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

Returns a ranked leaderboard by advanced metric using live data from the BSI MCP.

## What it does

1. Calls `bsi_get_leaderboard metric={metric} type={type} conference={conference} limit={limit}`.
2. Routes through the `college-baseball-intelligence` agent.
3. Applies the `interpreting-advanced-metrics` skill to contextualize numbers.
4. Formats the output as a clean ranked table.

## Output format

A markdown table:

| Rank | Player / Team | Primary Metric | Key Context Stats |
|---|---|---|---|

Followed by a brief analytical note:
- What the leaderboard says (e.g., "SEC dominates the top — 6 of top 10")
- Any early-season caveats (e.g., small sample for Feb rankings)
- Notable omissions or surprises

## Examples

```
/cbb-leaderboard metric=wrc_plus type=batting limit=10
```
→ Top 10 hitters nationally by park-adjusted wRC+.

```
/cbb-leaderboard metric=fip type=pitching conference=SEC limit=15
```
→ Top 15 SEC pitchers by FIP.

```
/cbb-leaderboard metric=woba type=team conference=ACC
```
→ ACC team offensive leaders by wOBA.

## Quality gates applied

- Park-adjusted metrics used when available (wRC+, ERA−, FIP−)
- Every entry has source + timestamp
- Early-season caveats surfaced when applicable
- Conference PI referenced when cross-conference rankings shown
