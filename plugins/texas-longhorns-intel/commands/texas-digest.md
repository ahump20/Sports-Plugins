---
name: texas-digest
description: Draft a one-time Texas baseball digest covering an explicit week, month or season, with sources and missing-data limits.
arguments:
  - name: timeframe
    description: week, month or season; default week
    required: false
---

# /texas-digest

Load `texas-longhorns-baseball-intelligence` and use its weeklyDigest output mode. Resolve explicit start/end dates and the relevant season before filtering the schedule. Read standings and rankings with their coverage metadata; do not infer a complete week's individual stats from season totals.

Return a supported headline, source observations, labeled interpretation, editorial recommendation, upcoming games and provenance. Missing conference records or season coverage remain unavailable. In the offseason, do not present historical results as games played this week.

This command produces a one-time Markdown draft, not a deployed API payload or a scheduled service. For publication review, use `editorial-evidence` when installed. Do not post or send the digest automatically.
