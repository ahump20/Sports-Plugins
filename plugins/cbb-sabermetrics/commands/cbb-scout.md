---
name: cbb-scout
description: Build a college baseball scouting brief from verified team, roster, schedule and player observations for an explicit season.
arguments:
  - name: team
    description: Team name or supported provider ID
    required: true
  - name: season
    description: Playing season; resolve from context when omitted
    required: false
  - name: opponent
    description: Optional team for a matchup comparison
    required: false
---

# /cbb-scout

Load `college-baseball-data` first. Resolve the requested team and season;
discover the actual BSI tools, then retrieve supported standings, schedule,
roster and player observations. Use the school's season-specific roster,
cumulative statistics and schedule for missing or conflicting feed data.
Do not guess player names from memory or join next year's roster to older stats.

Describe the sourced overall and conference records, batting/pitching profile,
key players, available recent results and scheduled opponent. A partial schedule
cannot establish the full record or a true last-ten-game trend. Identify poll
publisher/date when reporting a rank. Read original attributed reporting for
availability, injuries or lineup changes; roster absence proves none of these.

For an opponent comparison, align both teams' seasons, splits and cutoffs.
Use `interpreting-advanced-metrics` for supported calculations and
`conference-strength` for descriptive context. No invented strength adjustment,
psychological score or calibrated win probability is supplied by this workflow.
Label a provider prediction separately if the user asks for it and its method
and source are available.

Lead with the useful scouting findings, followed by a compact comparison or
stat table, source links and the material gaps. Distinguish observed results,
computed values and scouting interpretation. Drafting does not publish the brief.
