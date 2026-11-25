---
name: cbb-data
description: Find verified college baseball records, standings, schedules, rosters, team or individual statistics and historical records.
arguments:
  - name: request
    description: Team/player and the requested records, roster, schedule, standings or statistic
    required: true
  - name: season
    description: Playing season; resolve from context when omitted
    required: false
  - name: division
    description: NCAA division or another named college association
    required: false
---

# /cbb-data

Follow `college-baseball-data`. Retrieve the requested observations from the
available BSI catalog and inspected official sources. Confirm identities,
season, split and cutoff before joining results. Return a useful sourced table
and preserve unresolved coverage. In a host with local execution, use the
bundled HTML source helper; in a web-only host, read the original page with
available page/browser capabilities. Never claim that source collection ran
when only a link was found.
