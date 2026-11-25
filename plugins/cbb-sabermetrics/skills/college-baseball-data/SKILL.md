---
name: college-baseball-data
description: Use when retrieving or verifying college baseball records, standings, schedules, rosters, team or individual statistics, statistical leaders and historical records from season-specific sources. Covers NCAA, NAIA and junior-college source research; do not substitute another association or season when coverage is missing.
---

# College baseball data

Resolve the season, association/division, team/player and overall or conference
split from the request. For “current,” inspect the source's season and cutoff;
the calendar year, retrieval timestamp and next spring's roster are different
things. Do useful retrieval before asking about genuinely ambiguous identities.

## Retrieve

Discover the BSI MCP tools and schemas at runtime. Pass a season only when the
schema supports it; otherwise verify the returned season independently. Use
the feed for supported scores, standings, schedules and player observations.
Treat a successful call as retrieved evidence, not automatic verification.

When a field is missing, stale, inconsistent or outside the feed's scope, open
the original school, conference or association source. Use
[source routes](references/sources.md) for records, rosters, statistics and
archives. Search discovers a page; inspect its contents before citing a number.
Do not stop after one failed provider when an accessible official source can
answer the question. Explain a genuine access block and use another permitted
source; do not invent a replacement endpoint, bypass access controls or buy data.

In an execution-capable host, the bundled helper retrieves attributed HTML
tables or inspects a saved page. Read `scripts/cbb_source.py --help` and
[its contract](references/contract.md). For example, from this skill directory:

```bash
python3 scripts/cbb_source.py --url https://texaslonghorns.com/sports/baseball/stats/2025 --season 2025 --kind stats --team Texas --format json
```

This is a historical source check. The helper is not a hosted MCP tool. In a
web-only host, inspect the same official pages with available search/browser
tools. For PDF-only or JavaScript data, use the host's PDF/page capabilities;
the HTML helper does not certify that no data exists when it cannot extract it.

## Verify and combine

- Check the visible season, identity, split and source cutoff on every source.
  Keep source time and retrieval time separate; unknown cutoff stays unknown.
- Preserve raw columns, explicit zeros and missing values. Do not infer walks,
  HBP, sacrifice flies, conference wins or losses from rounded rates.
- Separate detailed batting/pitching totals from summary widgets. If values
  disagree, cross-check the official cumulative PDF or game totals and identify
  the conflict. An official domain can still publish a faulty summary panel.
- Keep overall and conference W/L/T separate. Preserve the published standings
  order and tiebreak status. A win-percentage sort is a calculated ordering.
- Confirm roster year before joining to stats. An absent player, missing page
  or incomplete roster does not establish departure, eligibility or injury.
- National leaders require the actual division-wide source, qualification
  rules and cutoff. A retrieved sample is only a selected-player comparison.
- Keep NCAA DI/DII/DIII, NAIA and NJCAA distinct. The BSI feed's coverage does
  not establish coverage of every college program. Fall exhibitions and spring
  championship-season records also need distinct scopes.

Use `interpreting-advanced-metrics` for calculations. Convert innings to outs;
do not fill missing inputs with zero or apply MLB constants as NCAA constants.

## Return

Lead with the requested records or stat table. Attach source links, season,
split and cutoff to the facts they support; include qualification/coverage
where relevant. Label derived statistics and their inputs. State unresolved
conflicts and unavailable fields succinctly. Preserve source URL, fetched time
and raw observations in an evidence packet when the user needs reusable data.
Do not equate source access with commercial redistribution rights.
