---
name: texas-matchup
description: Prepare an evidence-based Texas opponent preview from both teams' schedules, observations and sourced availability.
arguments:
  - name: opponent
    description: Opponent name or provider team identifier
    required: true
  - name: venue
    description: Optional home or away; verify against the source schedule
    required: false
---

# /texas-matchup

Load `texas-longhorns-baseball-intelligence`. Resolve the opponent exactly, read both schedules, and confirm the requested series, date and venue. Read available standings, rankings and individually sourced player observations. Use scoreboard matchId for match detail when a game exists there.

Build a side-by-side table of supported offense, pitching, recent completed results and documented availability. State selection scope and data cutoff. Report run rates only with a known denominator. Use `interpreting-advanced-metrics` for any calculated metric and `conference-strength` only for descriptive context.

Finish with an explicitly qualitative matchup interpretation and the most important missing input. Do not imply a calibrated confidence probability. No numerical park adjustment without a documented season-specific factor, no bullpen-health inference from box scores, and no unsourced head-to-head history. Provider forecasts, when actually returned, must remain attributed to their provider and method; do not present them as this plugin's model.
