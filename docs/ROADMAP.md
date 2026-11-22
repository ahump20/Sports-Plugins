# Next useful sports workflows

These priorities come from the existing code and recurring reporting, roster and fantasy questions. “Implemented” below means source and tests in this branch, not a public-directory submission or a connected account installation.

| Work | Status | User question | Input → useful output | Acceptance before release |
|---|---|---|---|---|
| Roster Watch | Implemented in this branch | What changed since my last roster check? | Two scoped source snapshots → observed additions/absences/field changes and coverage caveats | Stable identity; partial coverage respected; no inferred transfer or injury |
| Playoff Lab | Implemented in this branch | What seeds remain possible, and what if I win? | Declared league rules + records + remaining games → exact scenario bounds | Correct ties; supported rules only; explicit assumptions; no mislabeled odds |
| Series Desk | Proposed extension to Texas engine/plugin | What evidence do I need for this Texas series preview? | Team packets + official game notes + season totals → schedule, comparison, starter/workload evidence and gaps | Same-season joins; sourced probable starters; innings converted to outs; conflicting times preserved |
| Game Flow | Proposed extension to football/Gameday Ops | Where did the lead disappear? | Identified plays/drives → half, quarter and score-state splits with supporting play IDs | Exclude no-plays; separate overtime and defensive scores; define explosive plays; avoid causal claims from descriptive splits |
| Manuscript evidence adapter | Proposed extension to Editorial Desk | Which statements in this draft still need verification? | Manuscript + reviewed sources → claims linked into the existing evidence ledger | Quote/number extraction tested; opinions separated; voice preserved; no automatic publication |

## Why snapshots first

The useful first deliverable is a calculation or comparison that can be inspected and repeated. A hosted account integration can supply those same inputs later. That keeps provider setup and billing separate from proving the workflow.

A future connector should normalize to the existing contracts, preserve its raw response and declare source/season/coverage. It must not invent missing settings or turn an incomplete capture into a complete one.

## Provider constraints checked November 21, 2026

| Provider | Current documentation | Consequence for this project |
|---|---|---|
| Yahoo Fantasy | [Access applications](https://sports.yahoo.com/developer/access/) are reviewed; current access page describes read-only access. [API docs](https://sports.yahoo.com/developer/docs/) cover OAuth and league settings/standings/scoreboards. | Start with supplied exports or an existing authorized connector. A new Yahoo app is a separate integration task; do not promise instant private-league access. |
| Sleeper | [Official API documentation](https://docs.sleeper.com/) says free use is noncommercial and commercial use needs licensing discussion. | An unauthenticated API is not permission to advertise a free commercial BSI data feed. |
| Official team rosters | The [Texas roster](https://texaslonghorns.com/sports/baseball/roster) can show a later season than the [2026 stats page](https://texaslonghorns.com/sports/baseball/stats/2026). | Require season identity and scoped player IDs; compare observations without inventing reasons for absence. |
| BSI MCP | Discover tools at `https://sabermetrics.blazesportsintel.com/mcp`; use the companion engine's retained evidence. | Do not replace discovery with historical tool lists or infer coverage from request time. |

Older Yahoo API material still mentions read/write application choices. Use its current access page for approval expectations and confirm permitted capabilities for any actual integration.

## Where the selected tools fit

- **GitHub:** source, reviewable branches, test evidence and release history.
- **Firecrawl:** collect permitted public source content with URL and capture time; review extracted tables before declaring completeness.
- **Context7:** check the target host's actual manifests and installation syntax.
- **Data quality workflows:** validate identity, grain, completeness, denominators, chronology and unsupported assumptions.
- **Supabase:** optional future private snapshot/history store once recurring use requires persistence. Inspect the existing project first; no new project or schema is required by these local plugins.
- **Plugin Creator:** keep source, manifests, skills, packaged resources and validation aligned. Account installation and public submission are separate delivery actions.

For a future Supabase integration, use owner-scoped access policies for private league snapshots and keep service keys on the backend; see [Supabase's security guidance](https://supabase.com/docs/guides/database/secure-data). The current work creates no database, migration, subscription or scheduled fetch.
