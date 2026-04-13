---
name: game-data-pipeline
description: Use when the task involves ingesting, normalizing, storing, or processing college baseball game data — including box scores, play-by-play events, lineup data, and pitching logs — from NCAA stats, Baseball Reference, BSI's pipeline, or manually entered game sheets.
---

# Game Data Pipeline

Use this skill when quality depends on getting raw sports data correctly into a structured, queryable, and computable format. Bad data in means bad metrics out. This skill enforces clean ingestion, normalization, and storage patterns before any analytics layer runs.

## Working Model

Before building any pipeline, establish:

- **Source**: NCAA stats API, Baseball Reference scrape, BSI MCP endpoint, manual entry, or a school's own stats feed?
- **Granularity**: Game-level box scores, inning-by-inning logs, at-bat level, or pitch-level?
- **Target**: In-memory computation, database storage, file export (JSON/CSV), or live display?
- **Update frequency**: One-time load, daily batch, or live during a game?

The right architecture depends on all four answers. A live in-game pitch feed has very different latency and error-handling requirements than a season-end batch import.

## Data Schema Patterns

### Box Score Schema (game level)

```typescript
interface GameBoxScore {
  gameId: string;           // Unique identifier (source-prefixed: "ncaa-2025-04-05-texas-tcu")
  date: string;             // ISO 8601 date
  venue: string;
  homeTeam: TeamGameLine;
  awayTeam: TeamGameLine;
  innings: InningLine[];
  duration?: number;        // Minutes, if available
  attendance?: number;
  source: DataSource;
}

interface TeamGameLine {
  teamId: string;
  teamName: string;
  conference: string;
  runs: number;
  hits: number;
  errors: number;
  lineScore: number[];      // Runs per inning
  batting: BatterLine[];
  pitching: PitcherLine[];
}

interface BatterLine {
  playerId: string;
  name: string;
  position: string;
  ab: number;
  r: number;
  h: number;
  rbi: number;
  bb: number;
  k: number;
  hbp: number;
  sf: number;
  doubles: number;
  triples: number;
  hr: number;
  sb: number;
  cs: number;
}

interface PitcherLine {
  playerId: string;
  name: string;
  ip: number;             // Innings pitched as decimal (e.g. 6.1 = 6⅓)
  h: number;
  r: number;
  er: number;
  bb: number;
  k: number;
  hr: number;
  hbp: number;
  decision?: 'W' | 'L' | 'S' | 'H' | 'BS' | null;
  pitchCount?: number;
  strikes?: number;
}
```

### Season Aggregate Schema

```typescript
interface PlayerSeasonStats {
  playerId: string;
  teamId: string;
  season: number;
  gamesPlayed: number;

  // Batting
  pa: number;
  ab: number;
  h: number;
  doubles: number;
  triples: number;
  hr: number;
  rbi: number;
  r: number;
  bb: number;
  k: number;
  hbp: number;
  sf: number;
  sb: number;
  cs: number;

  // Pitching (if applicable)
  ip?: number;
  gs?: number;
  sv?: number;
  er?: number;
  bbAllowed?: number;
  kPitching?: number;
  hrAllowed?: number;
  hbpAllowed?: number;

  // Computed (populate after ingestion)
  avg?: number;
  obp?: number;
  slg?: number;
  ops?: number;
  iso?: number;
  babip?: number;
  woba?: number;
  wrcPlus?: number;
  era?: number;
  fip?: number;
  xfip?: number;
  whip?: number;
  kPer9?: number;
  bbPer9?: number;
}
```

## Ingestion Patterns

### NCAA Stats API

The NCAA provides a public stats endpoint. Key parameters:

```
GET https://stats.ncaa.org/player/game_by_game
  ?game_sport_year_ctl_id={year_ctl_id}
  &org_id={team_ncaa_id}
  &stats_player_seq={player_seq}
  &year_stat_category_postfix=_baseball
```

- Rate limit conservatively: 1 request per 2 seconds.
- Parse HTML tables (the API returns rendered HTML, not JSON).
- Use a cheerio or JSDOM parser server-side. Do not scrape client-side.
- Cache responses with a 24-hour TTL for historical games; 15-minute TTL for in-season.

### Baseball Reference College Pages

Baseball Reference does not have a public API. Scraping rules:

- Respect robots.txt. Do not automate at high frequency.
- For historical season stats, use the CSV download link pattern.
- For season-over-season archives, prefer the Sports Reference college baseball section.

### BSI MCP Endpoint

The BSI MCP server at `https://blazesportsintel.com/mcp` exposes college baseball data:

- Box scores for tracked D1 programs
- Live game state during active games
- Season-to-date aggregate stats for tracked rosters

Use the MCP server as the primary source for real-time data during a game. Fall back to NCAA stats for historical archives.

## Normalization Rules

### Innings Pitched

NCAA reports IP as integers for full innings and `.1` / `.2` for partial (1 out, 2 outs). Convert to decimals:

```typescript
function normalizeIP(ncaaIP: string | number): number {
  const str = String(ncaaIP);
  const [full, partial = '0'] = str.split('.');
  return parseInt(full) + parseInt(partial) / 3;
}
// Example: "6.2" → 6.667
```

### Player ID Normalization

Different sources use different player IDs. Build a cross-reference table:

```typescript
interface PlayerRef {
  bsiId: string;           // Internal BSI identifier
  ncaaId?: string;
  brefId?: string;
  name: string;
  team: string;
  season: number;
}
```

Never assume two players with the same name are the same player. Always resolve by team + season + name, then store the cross-reference.

### Handling Missing Data

- Missing `sf` (sacrifice flies): default to 0 if not in source.
- Missing `hbp`: default to 0.
- Missing `pitchCount`: leave null — do not estimate.
- Missing `attendance`: leave null — do not estimate.

Document every default explicitly in the pipeline config.

## Storage Recommendations

| Use Case | Recommended Storage |
|----------|-------------------|
| Historical season archives | Cloudflare D1 (SQLite) or Postgres |
| In-game live state | Cloudflare KV or Redis |
| Raw ingest cache | Cloudflare R2 or S3 (JSON blobs) |
| Computed aggregates | D1 or Postgres (materialized views) |
| File exports | JSON + CSV in R2 |

For the BSI stack specifically: use D1 for structured queries, KV for low-latency live reads, and R2 for raw ingest archival.

## Error Handling

- **Parse failures**: Log the raw source content to R2/S3 before throwing. Never lose raw data.
- **Missing games**: Track expected game count per team per week. Alert if fewer games than expected are found after a weekend.
- **Duplicate games**: Deduplicate by `(teamId, date, opponent)` — not just gameId, as sources may differ.
- **Score discrepancies**: If computed runs don't match the line score, flag for manual review. Do not silently accept.

## Hard Rules

- Never compute FIP or wOBA until IP and PA normalizations are complete and validated.
- Never store raw scraped HTML or DOM in the primary database — only parsed, structured data.
- Always log the source URL and timestamp of every ingest operation.
- Always validate that computed ERA = (ER / IP) × 9 within floating-point tolerance before storing.
- Do not backfill historical data in the same transaction as live data — separate pipelines, separate runs.
- When using the BSI MCP endpoint, always check the `lastUpdated` timestamp before consuming data in a time-sensitive context.
