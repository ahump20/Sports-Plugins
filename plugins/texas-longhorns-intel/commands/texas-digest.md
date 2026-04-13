---
name: texas-digest
description: Generate the weekly Texas baseball intelligence digest — live stats, conference position, recent results, upcoming schedule, analytical read.
arguments:
  - name: timeframe
    description: "week" (default) or "month" or "season"
    required: false
---

# /texas-digest

Produces a structured weekly digest on Texas baseball using live data from the BSI MCP.

## What it does

1. Calls `bsi_get_team_sabermetrics team=texas` for current offensive and pitching profile
2. Calls `bsi_get_team_schedule team=texas` for recent results and next upcoming games
3. Calls `bsi_get_standings conference=SEC` for conference position
4. Calls `bsi_get_conference_power_index` for SEC strength context
5. Routes through the `texas-longhorns-baseball-intelligence` agent using the `weeklyDigest` output mode
6. Assembles the digest in the structured format targeting the BSI hub's `/api/college-baseball/texas-intelligence/digest` endpoint shape

## Output format

Markdown digest with sections:

1. **This Week's Headline** — the structural story (e.g., "Texas wins weekend series vs Arkansas despite bullpen struggles")
2. **Verified Facts** — conference record, key wins/losses, individual performances with stats and sources
3. **Inference** — what the data suggests about trajectory
4. **Recommendation** — operational take: what should the program prioritize this week
5. **Upcoming Week** — next opponents with matchup-specific angles
6. **Source Attribution** — every number's source and as-of timestamp

## Examples

```
/texas-digest
```
→ Weekly digest (default).

```
/texas-digest timeframe=month
```
→ Full month review with trend analysis.

```
/texas-digest timeframe=season
```
→ Season-to-date overview.

## Quality gates applied

- Every statistical claim verified via MCP before inclusion
- Three-layer separation: Verified Facts / Inference / Recommendation
- Season-state lens applied to any metric interpretation
- SEC context provided via conference-strength framework
- No hometown discount — weaknesses named directly
- Program doctrine framed as history context only, not current-state evidence
