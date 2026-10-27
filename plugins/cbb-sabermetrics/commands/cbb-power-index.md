---
name: cbb-power-index
description: Rank DI conferences by strength, computed from live BSI standings and the national Top 25.
arguments:
  - name: conference
    description: Optional — if provided, returns detailed breakdown for that conference
    required: false
---

# /cbb-power-index

Returns a conference strength ranking computed from standings. It ranks DI conferences by aggregate win percentage and run differential across all their teams, plus how many teams each has in the national Top 25. The BSI Conference Power Index route is paused until its source and method are documented, so this command labels its output as computed from standings, not as the BSI Conference Power Index.

## What it does

1. Calls `bsi_get_standings` (no conference filter) for every team's W, L, win pct, runs scored, runs allowed and run differential.
2. Calls `bsi_get_rankings` for the national Top 25.
3. Groups teams by conference and computes, per conference: combined W-L and win pct, total and per-game run differential, and ranked-team count.
4. Routes through the `college-baseball-intelligence` agent with the `conference-strength` skill loaded.
5. Formats the output as a ranked table with analytical context.

## Output format

Ranked table, headed by one line saying it is computed from standings and rankings:

| Rank | Conference | Win Pct | Run Diff / Game | Teams in Top 25 | Teams |
|---|---|---|---|---|---|

Followed by analytical notes:
- Tier reads (elite / strong / mid / developing)
- What the numbers can't show: conference win pct includes in-conference games, which net to .500, so non-conference results drive the differences
- Cross-conference comparison framework

With `conference` argument: deep-dive on that conference
- Each team's line from `bsi_get_standings` (record, win pct, run differential, streak, games back)
- Which of its teams are in the Top 25 and where
- How its aggregate numbers compare to peer-tier conferences

## Examples

```
/cbb-power-index
```
→ All conferences ranked by the computed standings measures.

```
/cbb-power-index conference=SEC
```
→ SEC team-by-team standings and ranked teams, compared with peer conferences.

## Quality gates applied

- Output labeled as computed from `bsi_get_standings` and `bsi_get_rankings`, with the method stated
- Source + timestamp on every response
- No strength-of-schedule adjustment or component scores are claimed, since no tool returns them
- When naming tournament-caliber teams, uses real conference position from `bsi_get_standings`
