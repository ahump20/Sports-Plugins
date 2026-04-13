---
name: cbb-power-index
description: Pull the BSI Conference Power Index — SOS-adjusted rankings for all 32 DI conferences.
arguments:
  - name: conference
    description: Optional — if provided, returns detailed breakdown for that conference
    required: false
---

# /cbb-power-index

Returns the BSI Conference Power Index. Ranks the 32 DI conferences by strength-of-schedule-adjusted performance, not record or RPI.

## What it does

1. Calls `bsi_get_conference_power_index`.
2. Routes through the `college-baseball-intelligence` agent with the `conference-strength` skill loaded.
3. Formats the output as a ranked table with analytical context.

## Output format

Ranked table:

| Rank | Conference | Power Index | Programs | Projected Tournament Teams |
|---|---|---|---|---|

Followed by analytical notes:
- Tier reads (elite / strong / mid / developing)
- Notable movers from last check
- Tournament projection implications
- Cross-conference comparison framework

With `conference` argument: deep-dive on that conference
- Full PI breakdown
- Component scores (non-conference record, opponent quality, postseason track record)
- Projected tournament teams and bubble watch
- How it compares to peer-tier conferences

## Examples

```
/cbb-power-index
```
→ Full 32-conference ranked table.

```
/cbb-power-index conference=SEC
```
→ Deep dive on SEC with component scores.

## Quality gates applied

- PI score includes methodology attribution
- Source + timestamp on every response
- Never presents PI as a pure win-percentage ranking — always frames as SOS-adjusted
- When flagging tournament teams, cross-references with `bsi_get_standings` for real conference position
