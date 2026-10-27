# MCP Integration Guide

Most plugins in this marketplace consume one or more MCP (Model Context Protocol) servers. This doc explains how that wiring works and how to use the flagship Blaze Sports Intel MCP.

## The BSI MCP

**Endpoint:** `https://sabermetrics.blazesportsintel.com/mcp`
**Marketing page:** [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp) (a web page, not the connector URL)
**Server identity:** `blaze-sports-intel` version 4.0.0 (Cloudflare Worker `college-baseball-mcp`)
**Protocol:** MCP 2024-11-05
**Transport:** HTTP POST, JSON-RPC 2.0 only, no streaming
**Auth:** None (free tier)
**Rate limit:** 30 requests/minute per IP
**REST mirror:** `https://sabermetrics.blazesportsintel.com/v1/*`

## Tools Exposed (7, college baseball only)

### NCAA DI College Baseball (7 tools) → surfaced by `cbb-sabermetrics`

All 7 tools are read-only.

| Tool | Arguments | Purpose |
|---|---|---|
| `bsi_get_scoreboard` | `date` (YYYY-MM-DD, optional), `conference` (optional) | DI scores with venue and status |
| `bsi_get_standings` | `conference` (optional) | W, L, win pct, runs scored, runs allowed, run differential, streak, games back |
| `bsi_get_rankings` | none | National Top 25 with rank, record and movement |
| `bsi_get_player_stats` | `player` (required), `team` (optional) | Identity, team, position, traditional batting or pitching stats when the source has them |
| `bsi_get_team_schedule` | `team` (required, name or slug like `texas`, `lsu`) | Past results and upcoming games |
| `bsi_get_match_detail` | `matchId` (required, from the scoreboard) | Venue, weather, win predictions, play-by-play, team stats |
| `bsi_search_intel` | `query` (required), `limit` (1-10), `domains` (optional) | Web search of trusted college-baseball sources for news and scouting context |

The server has no MLB, NFL, NBA or college football tools. Team sabermetrics, leaderboards and the conference power index are paused on purpose: the server answers those routes with "This metric route is paused until its source, method, sample boundaries, and update metadata are documented" (code `closed_until_sourced`). Plugins compute advanced metrics from the counting stats `bsi_get_player_stats` returns (formulas in `plugins/college-baseball-sabermetrics/src/metrics.ts`) and label them as computed.

Every response envelope includes `meta`:

```json
{
  "meta": {
    "source": "Highlightly | ESPN",
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
    "blaze-sports-intel": {
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

The BSI MCP fans out to these sources with defined primary/fallback priority:

1. **Highlightly** (primary) — live scores, standings, venue, match detail. Fastest, most comprehensive.
2. **ESPN Site API** (fallback) — rankings, schedules, team metadata when Highlightly returns empty.

The `meta.source` field tells you which source served each response.

## Rate Limits and Caching

Free tier: **30 requests/minute per IP**.

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
- BSI MCP specifics: [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp) (marketing page; connect to `https://sabermetrics.blazesportsintel.com/mcp`)
- Marketplace issues: open an issue on this repo.
