---
name: cbb-leaderboard
description: Retrieve a sourced college baseball statistical leaderboard or compare an explicitly selected set of players or teams.
arguments:
  - name: metric
    description: Requested published or computable statistic
    required: true
  - name: type
    description: batting, pitching or team
    required: true
  - name: season
    description: Playing season; resolve from context when omitted
    required: false
  - name: conference
    description: Optional conference filter for that season
    required: false
  - name: limit
    description: Number of returned entries, default 10 and maximum 50
    required: false
---

# /cbb-leaderboard

Use `college-baseball-data` to resolve season, division, split and qualification
rules. For a national or conference leaderboard, inspect the actual official
statistical leaders table and preserve its cutoff and eligibility thresholds.
Poll rankings are not statistical leaderboards. Apply a requested limit after
retrieving the relevant ordered population, not before ranking a searched sample.

If the user requests a selected comparison, retrieve those players/teams with
unambiguous identities. Call it a **Selected-player comparison** or
**Selected-team comparison**, identifying omissions and unavailable fields.
Search results, Top 25 teams and individually looked-up players never establish
a complete national population.

Use `interpreting-advanced-metrics` for derived values. Missing counts or
season/division constants make the requested metric unavailable; do not invent
wOBA, wRC+, FIP, WAR or park adjustments. Keep published values distinct from
local calculations and do not silently substitute another metric.

Return rank (only where supported), player/team, metric, sample, season/split,
source and cutoff. Identify qualification rules and any gaps. Treat a zero-game
row or zero denominator as unqualified/unavailable rather than ranking it first.
