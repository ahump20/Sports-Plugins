# Blaze Sports Intel (BSI) Plugin

Official plugin for [Blaze Sports Intel](https://blazesportsintel.com) — a mobile-first sports intelligence platform specializing in college baseball analytics, advanced sabermetrics, and Texas Longhorns coverage.

## Features

- **College baseball box scores** — Complete, formatted box scores with advanced metrics
- **Texas Longhorns intel** — Deep coverage of UT Austin baseball including player profiles, game recaps, and season analytics
- **Sabermetric profiles** — wOBA, FIP, wRC+, barrel rates, pitch mix, and more for every D1 player
- **Live game data** — Real-time scores and in-game analytics
- **Conference analytics** — Big 12, SEC, ACC, and all D1 conference breakdowns
- **Cross-sport scores** — MLB, NFL, NBA scoreboard integration

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `bsi-query` | Model-invoked | Query BSI analytics engine for college baseball data |
| `longhorns-intel` | Model-invoked | Texas Longhorns-specific baseball intelligence |

## MCP Endpoint

This plugin connects directly to the BSI MCP server:

```
https://blazesportsintel.com/mcp
```

The MCP endpoint provides tool-use access compatible with both Claude Code and OpenAI Codex assistants.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_box_score` | Retrieve a complete box score for a specific game |
| `get_player_stats` | Advanced sabermetric profile for a player |
| `get_team_stats` | Team-level analytics with conference context |
| `get_standings` | Conference and national standings with RPI |
| `get_schedule` | Team schedule with results and upcoming games |
| `get_live_scores` | Current live game scores |
| `search_players` | Search for players by name, team, or position |

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
