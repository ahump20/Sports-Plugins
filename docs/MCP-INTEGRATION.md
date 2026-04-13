# MCP Integration Guide

Most plugins in this marketplace consume one or more MCP (Model Context Protocol) servers. This doc explains how that wiring works and how to use the flagship Blaze Sports Intel MCP.

## The BSI MCP

**Endpoint:** `https://sabermetrics.blazesportsintel.com/mcp`
**Marketing page:** [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp)
**Server identity:** `blaze-sports-intel` version 4.0.0
**Transport:** Streamable HTTP (JSON-RPC 2.0)
**Auth:** None (free tier)
**Rate limit:** 30 requests/minute per caller
**REST mirror:** `https://sabermetrics.blazesportsintel.com/v1/*`

## Tools Exposed (31 total across 5 sports)

Grouped by sport family. Each group is designed to be surfaced by a dedicated plugin.

### NCAA DI College Baseball (10 tools) → surfaced by `cbb-sabermetrics`

| Tool | Purpose |
|---|---|
| `bsi_get_scoreboard` | Live/final DI scores with venue and status |
| `bsi_get_standings` | Conference standings with wins, losses, run differential |
| `bsi_get_rankings` | D1Baseball Top 25 national rankings |
| `bsi_get_team_sabermetrics` | Advanced team metrics (wOBA, wRC+, FIP, ERA-, BABIP, ISO) |
| `bsi_get_leaderboard` | Top hitters/pitchers by metric, filterable by conference |
| `bsi_get_conference_power_index` | SOS-adjusted conference strength rankings |
| `bsi_get_player_stats` | Player search with batting/pitching stats |
| `bsi_get_team_schedule` | Full team schedules (past and upcoming) |
| `bsi_get_match_detail` | Venue, weather, predictions, play-by-play, team stats |
| `bsi_search_intel` | Cross-entity search across teams, players, games |

### MLB (5 tools) → will be surfaced by `mlb-sabermetrics` (coming soon)

| Tool | Purpose |
|---|---|
| `bsi_get_mlb_scoreboard` | Live/final MLB scores with venue and status |
| `bsi_get_mlb_standings` | Division standings with wins, losses, run differential |
| `bsi_get_mlb_team` | Team detail with roster and recent performance |
| `bsi_get_mlb_game` | Game detail with box score and play-by-play |
| `bsi_get_mlb_leaders` | League leaders by stat category |

### NFL (5 tools) → will be surfaced by `nfl-analytics` (coming soon)

| Tool | Purpose |
|---|---|
| `bsi_get_nfl_scoreboard` | Live/final NFL scores with venue and status |
| `bsi_get_nfl_standings` | Division standings with records |
| `bsi_get_nfl_team` | Team detail with roster and recent performance |
| `bsi_get_nfl_game` | Game detail with box score and play-by-play |
| `bsi_get_nfl_leaders` | League leaders by stat category |

### NBA (5 tools) → will be surfaced by `nba-analytics` (coming soon)

| Tool | Purpose |
|---|---|
| `bsi_get_nba_scoreboard` | Live/final NBA scores with venue and status |
| `bsi_get_nba_standings` | Conference standings with records |
| `bsi_get_nba_team` | Team detail with roster and recent performance |
| `bsi_get_nba_game` | Game detail with box score and play-by-play |
| `bsi_get_nba_leaders` | League leaders by stat category |

### NCAA College Football (6 tools) → will be surfaced by `cfb-analytics` (coming soon)

| Tool | Purpose |
|---|---|
| `bsi_get_cfb_scoreboard` | Live/final CFB scores with venue and status |
| `bsi_get_cfb_standings` | Conference standings with records |
| `bsi_get_cfb_rankings` | AP/Coaches Poll national rankings |
| `bsi_get_cfb_team` | Team detail with roster and recent performance |
| `bsi_get_cfb_game` | Game detail with box score and play-by-play |
| `bsi_get_cfb_transfer_portal` | Transfer portal tracker |

Every response envelope includes `meta`:

```json
{
  "meta": {
    "source": "Highlightly | ESPN | BSI Savant",
    "fetched_at": "2026-04-12T14:30:00Z",
    "timezone": "America/Chicago"
  },
  "data": { /* tool result */ }
}
```

## Consuming from a Plugin

Every plugin that uses an MCP server declares it in the plugin's `.mcp.json`:

```json
{
  "mcpServers": {
    "college-baseball-sabermetrics": {
      "type": "http",
      "url": "https://sabermetrics.blazesportsintel.com/mcp"
    }
  }
}
```

When a user installs the plugin, Claude Code or Codex automatically registers the MCP server and makes its tools available in-session. No additional setup required.

## Consuming Without a Plugin

You can also register the BSI MCP directly in your Claude Code or Codex settings without installing a plugin:

**Claude Code (`~/.claude/settings.json`):**
```json
{
  "mcpServers": {
    "bsi-college-baseball": {
      "type": "http",
      "url": "https://sabermetrics.blazesportsintel.com/mcp"
    }
  }
}
```

**Codex (similar pattern in Codex settings).**

The plugins in this marketplace bundle the MCP config plus agents, skills, and commands that know how to use the tools effectively.

## Data Sources Behind the MCP

The BSI MCP fans out to three sources with defined primary/fallback priority:

1. **Highlightly** (primary) — live scores, standings, venue, match detail. Fastest, most comprehensive.
2. **BSI Savant** (primary for advanced metrics) — DI-calibrated wOBA/wRC+/FIP/BABIP/ISO computed daily from raw play-by-play.
3. **ESPN Site API** (fallback) — rankings, schedules, team metadata when Highlightly returns empty.

The `meta.source` field tells you which source served each response.

## Rate Limits and Caching

Free tier: **30 requests/minute per caller**. Identified by IP.

Cached responses at edge:
- Live scores: 15–30 seconds
- Standings: 60 seconds
- Final/completed games: 5 minutes
- Rosters and team metadata: 1 hour

If you exceed 30/min, the server returns HTTP 429. Wait and retry. For higher limits or enterprise tier, contact john.humphrey@blazesportsintel.com.

## Error Handling

Errors return a JSON-RPC 2.0 error object:

```json
{
  "jsonrpc": "2.0",
  "id": "<request-id>",
  "error": {
    "code": -32603,
    "message": "Upstream Highlightly temporarily unavailable",
    "data": {
      "degraded": true,
      "fallback_attempted": true
    }
  }
}
```

When `degraded: true`, the MCP attempted fallback to ESPN. If even the fallback failed, the tool returns an honest "source unavailable" message rather than fabricating data.

## Writing Your Own MCP-Backed Plugin

If you build a plugin that wraps a different sports MCP:

1. Include the MCP config in your plugin's `.mcp.json`.
2. Document the tools in your README, including any auth requirements.
3. Document rate limits and cache policy.
4. Include `meta` envelope handling in any commands or agent instructions.
5. Handle degraded-source conditions gracefully — never fabricate.

## Questions

- General MCP protocol: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- BSI MCP specifics: [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp)
- Marketplace issues: open an issue on this repo.
