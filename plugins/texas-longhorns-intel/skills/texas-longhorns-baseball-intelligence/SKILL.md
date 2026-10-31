---
name: texas-longhorns-baseball-intelligence
description: Use when researching Texas Longhorns baseball, preparing an opponent preview, evaluating sourced player statistics, checking historical context, or drafting a Texas baseball briefing.
---

# Texas Longhorns baseball intelligence

Use Texas history as context, never as evidence of present performance. Distinguish source observations, interpretation and editorial recommendations.

## Collect evidence

Discover available tools before selecting a workflow. The BSI MCP catalog inspected on October 31, 2026 contained seven read-only tools; discovery, not this snapshot, is authoritative.

| Question | Read path |
|---|---|
| Team or SEC position | `bsi_get_standings` with conference SEC, then `bsi_get_team_schedule` with team texas |
| Player | `bsi_get_player_stats` with player identity and team texas |
| Series | Both team schedules and standings, then source-confirmed player data |
| Game | `bsi_get_scoreboard`, then `bsi_get_match_detail` with the returned matchId |
| Rankings | `bsi_get_rankings`; name the poll and release date |
| Roster, availability or news | `bsi_search_intel`, then read the original official source |

Use exact team identity, not a substring that also matches Texas A&M. Preserve provider metadata and request arguments. A retrieval time is not a season or statistical coverage date. Missing conference counts remain unavailable; do not reverse-engineer them from percentages. The tools do not provide a complete roster, calibrated projection or all advanced team metrics.

## Analyze only supported inputs

For metric calculations, use `interpreting-advanced-metrics` and the installed `baseball-analytics` helper. If the helper or required league totals are missing, state the dependency; do not improvise constants. For conference comparisons, use the descriptive `conference-strength` workflow rather than assigning a reputation multiplier.

Texas entered the SEC institutionally in 2024; its first SEC baseball season was 2025. The 2024 baseball season belongs to the Big 12. Confirm current coach, roster, venue details and ongoing achievement totals against official Texas sources when needed. Source: https://texaslonghorns.com/news/2024/9/12/baseball-announces-2025-sec-schedule.

Do not manufacture HAV-F, momentum, psychological-readiness, NIL-return, park-factor or draft-probability scores. A qualitative scouting opinion needs an identified basis and limitations. Do not infer injuries or bullpen availability from usage alone. Historical program benchmarks are editorial expectations, not validated championship thresholds.

## Deliver the requested format

Lead with the supported finding. Give a compact observations table with source, season, sample and missing fields; follow with interpretation and an explicitly labeled recommendation. Use [output modes](references/output-modes.md) only when a specialized format helps. Preserve Austin's writing voice; a factual check does not authorize rewriting the argument.

For a game fact sheet, route to `gameday-packet` when installed. For publication checks, route to `editorial-evidence`. Both require actual source observations, not bundled test fixtures. The companion Texas intelligence repository supplies an executable HTTP evidence collector; do not claim it is installed unless verified locally.

## Failure behavior

Report failed tools, ambiguous identity, absent season coverage and incomplete samples. Do not fill gaps with memory or examples. A one-time digest is not a scheduled service. Drafting does not authorize publishing, deploying, emailing or changing production data.
