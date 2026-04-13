# Use Cases — Codex Taxonomy Applied to Sports

This marketplace organizes plugins using the same category vocabulary as [OpenAI Codex's use-cases page](https://developers.openai.com/codex/use-cases). That taxonomy was built for generic software work — applied to sports, the categories still hold, but the examples change.

## Categories

### Data
Structured sports data — stats, rates, rankings, projections. Plugins in this category wrap data sources and expose them as tool calls.

- **cbb-sabermetrics** — 10 tools covering 330 NCAA DI college baseball programs. wOBA, wRC+, FIP, BABIP, ISO, park-adjusted metrics, conference power index. Free tier, 30 req/min.
- Coming: MLB sabermetrics wrapper, NFL advanced stats, NBA shot charts.

### Integrations
Plugins that wire external services into an AI coding assistant's tool space. For sports, this usually means MCP servers wrapping live data APIs.

- **cbb-sabermetrics** — wraps Blaze Sports Intel MCP at `blazesportsintel.com/mcp`. JSON-RPC 2.0 over HTTPS, 10 tools exposed.
- Coming: ESPN, SportsRadar, Highlightly wrappers for sports not yet covered.

### Knowledge Work
Research, scouting, editorial, and analysis. Plugins that take raw data and produce human-readable intelligence.

- **texas-longhorns-intel** — Texas baseball scouting reports, matchup previews, NIL analysis, program history. Depends on `cbb-sabermetrics` for live data.
- Coming: `cardinals-intel` (MLB Cardinals), other program-specific intelligence plugins.

### Workflow
Multi-step automation — editorial pipelines, recap generation, weekly digest production, newsletter drafting.

- Coming: `sports-storytelling` editorial voice plugin; automated recap pipelines for weekend college baseball series.

### Front-end
Visualization, interactive dashboards, game UIs. For sports, this is the visual half of intelligence — charts that make patterns legible.

- Coming: `sports-viz` — Savant-style charts with texture encoding, spray charts, percentile bands, matchup theaters.
- Coming: biomechanics motion rendering (batting stance, pitch delivery, swing path).

### Engineering
Infrastructure, data pipelines, app development. For sports, this means building the platforms that serve the intelligence.

- Coming: `sports-arcade-dev` — browser sports game development (Canvas/WebGL physics, input handling, scoring, leaderboard integration, Cloudflare Pages deployment).
- Coming: patterns for building sports data pipelines on Cloudflare Workers + D1 + KV + R2.

### Automation
Scheduled jobs — daily/weekly recomputes, scraped data pipelines, alert triggers.

- Coming: patterns for Cloudflare Worker crons that refresh sabermetrics every 6 hours, ingest box scores nightly, publish weekly recaps Sunday mornings.

### Quality
Data validation, stat verification, cross-source reconciliation. For sports, this is enforcing that every claim has a source and a timestamp.

- Baked into `cbb-sabermetrics` meta envelope (`source`, `fetched_at`, `timezone`) on every response.
- Coming: standalone validators for sports data freshness and cross-source agreement.

### Evaluation
Testing plugin outputs against known-good answers. For sports, this means checking that a scouting report cites real numbers, that a leaderboard matches the canonical source.

- Coming: `sports-evals` suite — deterministic golden tests against frozen historical data.

## Blueprints

### Blueprint 1: Scouting Workflow
**Question:** Give me a scouting report on Texas for this weekend's Arkansas series.

1. User runs `/texas-scout opponent=arkansas` (from `texas-longhorns-intel` plugin).
2. Command routes to `texas-longhorns-baseball-intelligence` agent.
3. Agent calls `bsi_get_team_sabermetrics team=texas` (from `cbb-sabermetrics`).
4. Agent calls `bsi_get_team_sabermetrics team=arkansas`.
5. Agent calls `bsi_get_conference_power_index` for SEC context.
6. Agent applies Texas program doctrine + HAV-F framework.
7. Agent produces structured scouting report: Verified facts → Inference → Recommendation.

### Blueprint 2: Leaderboard Lookup
**Question:** Who are the top 10 college baseball hitters by wRC+ in the SEC?

1. User runs `/cbb-leaderboard metric=wrc_plus conference=SEC limit=10`.
2. Command calls `bsi_get_leaderboard` with those parameters.
3. Returns a ranked table with source + timestamp metadata.

### Blueprint 3: Matchup Preview
**Question:** What's the edge in tomorrow's Vanderbilt at LSU game?

1. User runs `/texas-matchup` (or `/cbb-preview` once built).
2. Agent chain fetches both teams' advanced metrics, ballpark context, recent form, pitcher matchup, bullpen health.
3. Agent applies MMI (momentum timeline) and leverage framework.
4. Agent returns a pre-series brief.

## Team Lenses

From Codex's use-case framing, these plugins serve multiple developer teams:

- **Engineering** — build sports data pipelines, integrate MCP tools, deploy to Cloudflare
- **Product** — prototype sports features with real data
- **Design** — visualize sports data with Savant-style patterns
- **Operations** — automate daily data refreshes, content pipelines
- **QA** — validate sports data freshness and cross-source agreement

## Task Types

- **Analysis** — sabermetric interpretation, matchup breakdowns, trend detection
- **Code** — building sports apps, games, dashboards, data pipelines
- **Design** — chart composition, interactive viz, game UIs
- **Workflow** — editorial pipelines, recap generation, weekly digests
