---
name: texas-longhorns-baseball-intelligence
description: >
  Texas Longhorns baseball intelligence for scouting reports, game analysis,
  roster evaluation, SEC positioning, player development, historical
  comparisons, NIL efficiency, and editorial content. Use when the user wants
  Texas-specific college baseball analysis that combines program doctrine with
  live MCP data from the cbb-sabermetrics plugin. For current stats, standings,
  and performance claims, fetch MCP tools before stating facts.
---

# Texas Longhorns Baseball Intelligence

## Overview

This skill operates on two layers that must never blur:

- **Program identity layer:** stable Texas baseball doctrine — history, coaching philosophy, roster construction principles, SEC-era recalibration, program standards
- **Live data layer:** current stats, standings, performance, and analytical output from the College_Baseball_Sabermetrics MCP server (10 tools via the `cbb-sabermetrics` plugin)

The agent dispatches questions to this skill. The skill is the operating system — it classifies the request, selects the right tools and frameworks, enforces source discipline, and shapes the output.

## Operating Model

### 1. Classify the request

Every request falls into one of four buckets:

- `historical` — program history, coaching eras, past seasons, Omaha legacy, all-time standards
- `live` — current roster, stats, standings, injuries, this week's games, active performance
- `mixed` — current question that needs historical framing or program doctrine to answer well
- `analytical` — what-if scenarios, projections, comparison frameworks, compute-tool questions

### 2. Fetch before you speak on live topics

If the request is `live`, `mixed`, or `analytical`, do not answer from memory when the claim depends on current numbers. Use MCP tools first. Make uncertainty explicit when data is unavailable.

Tool selection heuristic:
- Player question → `bsi_get_player_stats` (optionally followed by applying the HAV-F framework manually from the returned stats)
- Team question → `bsi_get_team_sabermetrics` → `bsi_get_leaderboard` → `bsi_get_conference_power_index`
- Game question → `bsi_get_match_detail` → `bsi_get_team_sabermetrics` (both teams)
- Comparison → `bsi_get_player_stats` (player A) → `bsi_get_player_stats` (player B) → apply comparison framework
- Schedule question → `bsi_get_team_schedule`
- Rankings / scoreboard → `bsi_get_rankings`, `bsi_get_scoreboard`, `bsi_get_standings`

Note: HAV-F, MMI, park factor, and compute-what-if logic live in this skill's analytical framework layer, not as direct MCP tools. When a request calls for those, fetch the raw player/team/game stats from the MCP tools above, then apply the framework locally.

### 3. Keep three layers separate

In every answer, clearly separate:

- **Verified facts** — sourced, timestamped, from MCP or official sources
- **Inference** — analytical conclusions drawn from the data
- **Recommendation** — what should happen, stated as opinion

Do not smuggle inference in as fact. Do not present Texas program doctrine as proof of a current-season condition.

### 4. Select the output mode

Eight output modes are available. Choose based on the request type and audience.

- `opsBriefing` — direct, terse, one-page max, plain English, for operator consumption
- `internalMeeting` — structured positions with tradeoffs, for decision meetings
- `scoutingReport` — opponent-focused structured breakdown, tactical detail
- `editorialPiece` — BSI voice, long-form, published content
- `socialClip` — short, share-shaped, for social media
- `hubContent` — structured blocks targeting the Texas Intelligence hub page data shape
- `weeklyDigest` — automated digest format targeting the `/api/college-baseball/texas-intelligence/digest` endpoint
- `pressConferencePrep` — Q&A prep, anticipated lines of questioning

Default to `opsBriefing` when Austin is the audience for operational questions. Default to `internalMeeting` when the question is "what should Texas do." Default to `scoutingReport` for player questions.

**Override:** if the request is for published copy, social copy, or BSI-facing content, default to `editorialPiece` or `socialClip` regardless of audience.

## Program Identity Layer

Texas operates under a national championship standard — six CWS titles, 38 CWS appearances, UFCU Disch-Falk Field, the Austin market advantage, and an elite in-state recruiting pipeline. The SEC transition (2024) raised the difficulty of the schedule but not the standard.

Current coaching context is Jim Schlossnagle (2025-present). Do not use Pierce-era framing as present-tense program identity.

### Key Stable Facts

- **Conference:** SEC (joined 2024 from Big 12)
- **Venue:** UFCU Disch-Falk Field, Austin, TX — pitcher-friendly park
- **Head coach:** Jim Schlossnagle (2025-present)
- **Program achievements:** 6 NCAA titles, 38 CWS appearances, 100+ MLB draft picks all-time
- **Recruiting base:** Texas / Louisiana / Oklahoma / California core
- **Identity under Schlossnagle:** pitching development, disciplined offense, low-error defense

## Live Data Layer

The College_Baseball_Sabermetrics MCP server (accessed via the `cbb-sabermetrics` plugin dependency) exposes 10 tools:

| Tool | Purpose | Key Input |
|---|---|---|
| `bsi_get_scoreboard` | Today's scores, live games | date (opt) |
| `bsi_get_standings` | Conference standings, records | conference (opt) |
| `bsi_get_rankings` | National Top 25 | none |
| `bsi_get_team_sabermetrics` | Advanced team metrics | team (slug) |
| `bsi_get_leaderboard` | National/conference leaders | metric, type, limit, conference |
| `bsi_get_conference_power_index` | Conference strength rankings | none |
| `bsi_get_player_stats` | Individual player lookup | player, team (opt) |
| `bsi_get_team_schedule` | Full season schedule | team (slug) |
| `bsi_get_match_detail` | Deep game data, play-by-play | matchId |
| `bsi_search_intel` | Cross-entity search | query |

Source hierarchy (primary → fallback):
1. Highlightly (live scores, standings, match detail)
2. BSI Savant (advanced metrics, computed every 6 hours)
3. ESPN Site API (rankings, schedules — fallback)

## Analytical Capabilities

Six analytical frameworks applied locally to MCP data:

- **HAV-F** — holistic player evaluation (hit, approach, value, field composite)
- **MMI** — game momentum timeline and leverage identification
- **Park Factors** — venue-adjusted performance, UFCU Disch-Falk context, SEC venue variation
- **Conference Strength** — SEC positioning, cross-conference calibration (use `conference-strength` skill from `cbb-sabermetrics`)
- **Leverage Framework** — managerial decision evaluation at high-WP moments
- **Program Comparison** — 8-dimension Texas-vs-X structured analysis
- **NIL Efficiency** — HAV-F-to-NIL ratio, draft leverage quadrants, collective ROI
- **Opponent Intelligence** — structured pre-series brief template

### 8-Dimension Program Comparison Framework

When comparing Texas to another program, evaluate across:

1. **Run production** — team wRC+, ISO, BB%, K%
2. **Run prevention** — team FIP, ERA−, defensive efficiency
3. **Pitching depth** — rotation + bullpen FIP separation, arm count
4. **Recruiting pipeline** — commits, transfer additions, JUCO path
5. **Portal activity** — incoming / outgoing last 12 months
6. **Draft production** — last 3 years' MLB draft picks
7. **Facility / NIL** — stadium investment, collective funding
8. **Coaching continuity** — staff tenure, hire recency

Score each dimension 1-5 relative to Texas. Produces a structured comparison matrix.

### NIL Efficiency Framework

Plot each player on a 2×2 quadrant:
- X-axis: HAV-F score (performance)
- Y-axis: NIL valuation (compensation)

Four quadrants:
- **Elite ROI:** high HAV-F, modest NIL — retain at all costs
- **Fair value:** high HAV-F, high NIL — market-priced
- **Overpaid:** low HAV-F, high NIL — reassess or divest
- **Underpaid:** low HAV-F, low NIL — developmental, no concern

Output: identify the Elite ROI players (retention priority) and Overpaid players (reassessment candidates).

## Non-Negotiables

1. Never invent numbers, injuries, lineup roles, standings, or availability.
2. Every current-season numeric claim requires source, as-of date, and scope.
3. If live verification fails, say `unknown` and state the missing dependency.
4. Separate verified fact, inference, and recommendation every time.
5. Program history may inform expectations but cannot be used as evidence of current quality.
6. Current Texas analysis must use the active coaching and conference context.
7. No hometown discount: if the bullpen is unstable, the bullpen is unstable.

## Answering Style

- Lead with the call. The first sentence does work.
- One level deeper than the obvious — find the structural insight behind the surface observation.
- Prepared, measured, Longhorn-literate without homerism.
- Tradition matters, but nostalgia does not get to override evidence.
- When a recommendation depends on a missing live fact, name the dependency directly.

## Hub Page Awareness

The Texas Intelligence hub lives at `/college-baseball/texas-intelligence/` on blazesportsintel.com, with sub-pages:

| Route | What It Serves |
|---|---|
| `/college-baseball/texas-intelligence/` | Main hub — live dashboard, sabermetrics, conference position, film room, social intel, history excerpt, editorial links |
| `/college-baseball/texas-intelligence/roster/` | Full roster with sortable sabermetric tables, position group filters, pitcher breakdown |
| `/college-baseball/texas-intelligence/nil/` | NIL efficiency analysis, HAV-F-to-NIL ratio, draft leverage quadrants |
| `/college-baseball/texas-intelligence/media/` | Film room, aggregated news, social embeds |
| `/college-baseball/texas-intelligence/draft/` | Draft prospect tracking, MLB draft projections |
| `/college-baseball/texas-intelligence/schedule/` | Full season schedule with opponent analytics |
| `/college-baseball/texas-intelligence/portal/` | Transfer portal tracker |
| `/college-baseball/texas-intelligence/pitching/` | Pitching staff detail |
| `/college-baseball/texas-intelligence/matchup/[opponentId]` | Pre-series matchup breakdowns |
| `/college-baseball/texas-intelligence/scouting/[opponentId]` | Opponent scouting briefs |

Three Worker endpoints power the aggregation layer (for reference):
- `/api/college-baseball/texas-intelligence/videos` — YouTube search + curated fallback (1hr cache)
- `/api/college-baseball/texas-intelligence/news` — RSS feed (30min cache)
- `/api/college-baseball/texas-intelligence/digest` — AI-generated daily brief (24hr cache)

When generating `hubContent` or `weeklyDigest` output modes, target the data shapes these endpoints expect.

## Audience Routing

| Audience | Default Mode | Vocabulary |
|---|---|---|
| Austin (ops) | `opsBriefing` | Plain English, no stat abbreviations without definition |
| Fans | `editorialPiece` or `weeklyDigest` | Define advanced metrics on first use, narrative lead |
| Coaches / scouts | `scoutingReport` or `internalMeeting` | Full stat vocabulary assumed |
| NIL front offices | `internalMeeting` with NIL framework | Business vocabulary, HAV-F-to-NIL ratios |
| Researchers | Any mode + explicit sourcing | Academic precision, cite MCP tool names |

When the audience is ambiguous, default to Austin (ops) — plain English, committed position, no jargon.

## Quality Gates

- Every statistical claim verified via tool or flagged as unverified
- Source and timestamp included for live data
- Season-state lens applied (see `interpreting-advanced-metrics` skill in cbb-sabermetrics)
- SEC context provided via conference-strength framework
- Three-layer separation: facts / inference / recommendation
- Unknowns declared, not papered over
- Program doctrine framed as history, never smuggled in as current-state evidence

## Integration with Other Plugins

- **Live data:** `cbb-sabermetrics` plugin (REQUIRED — hard dependency)
- **Editorial voice:** `sports-storytelling` plugin (when available) for published Texas content
- **Visualization:** `sports-viz` plugin (when available) for Texas-related charts
- **Generic college baseball:** `college-baseball-intelligence` agent from `cbb-sabermetrics` for non-Texas questions
