# Blaze Sports Intel (BSI) Plugin

Official plugin for [Blaze Sports Intel](https://blazesportsintel.com) — a mobile-first sports intelligence platform specializing in college baseball analytics, advanced sabermetrics, and Texas Longhorns coverage.

## Features

- **College baseball scores and game detail**: Scoreboard plus venue, weather, win predictions, play-by-play and team stats for a game
- **Texas Longhorns intel** — Deep coverage of UT Austin baseball including player profiles, game recaps, and season analytics
- **Player stats**: Traditional batting and pitching stats when the source has them; advanced metrics such as wOBA and FIP are computed from those counting stats and labeled as computed
- **Standings and rankings**: Conference standings with run differential, plus the national Top 25
- **News and scouting context**: Search of trusted college-baseball sources

College baseball only. The MCP server has no MLB, NFL, NBA or college football tools.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `bsi-query` | Model-invoked | Query BSI analytics engine for college baseball data |
| `longhorns-intel` | Model-invoked | Texas Longhorns-specific baseball intelligence |

## MCP Endpoint

This plugin connects directly to the BSI MCP server:

```
https://sabermetrics.blazesportsintel.com/mcp
```

The MCP endpoint provides tool-use access compatible with both Claude Code and OpenAI Codex assistants. It takes POST JSON-RPC (MCP protocol 2024-11-05) with no streaming, needs no API key, and allows 30 requests per minute per IP. `https://blazesportsintel.com/mcp` in a browser is a marketing page, not the connector URL.

### Available MCP Tools

Seven read-only college baseball tools:

| Tool | Description |
|------|-------------|
| `bsi_get_scoreboard` | Scores, venue and status (`date` YYYY-MM-DD and `conference` optional) |
| `bsi_get_standings` | W, L, win pct, runs scored, runs allowed, run differential, streak, games back (`conference` optional) |
| `bsi_get_rankings` | National Top 25 with rank, record and movement |
| `bsi_get_player_stats` | Identity, team, position, traditional batting or pitching stats when the source has them (`player` required, `team` optional) |
| `bsi_get_team_schedule` | Past results and upcoming games (`team` name or slug, like `texas` or `lsu`) |
| `bsi_get_match_detail` | Venue, weather, win predictions, play-by-play, team stats (`matchId` from the scoreboard) |
| `bsi_search_intel` | Web search of trusted college-baseball sources for news and scouting context (`query` required, `limit` 1-10, `domains` optional) |

Every response carries `meta.source`, `meta.fetched_at` and `meta.timezone` (America/Chicago).

## Installation

```
/plugin install blaze-sports-intel@Sports-Plugins
```

## Usage

The BSI skills activate automatically when you discuss college baseball, Texas Longhorns baseball, or request sabermetric data.

## About BSI

Blaze Sports Intel is built with Next.js, deployed on Cloudflare Pages with Cloudflare Workers backend, and powered by a custom analytics engine for college baseball sabermetrics. The platform covers:

- **College Baseball** — Primary focus with complete box scores, rankings, and analytics
- **MLB** — Major League Baseball stats and scores
- **NFL** — National Football League coverage
- **NBA** — Basketball scores and stats
- **College Football** — Including transfer portal tracking
- **NIL Valuation** — Name, Image, and Likeness valuation tools

Source: [github.com/ahump20/BSI](https://github.com/ahump20/BSI)
