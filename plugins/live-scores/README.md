# Live Scores Plugin

Real-time sports scores, schedules, and game updates for AI coding assistants.

## Features

- **Live scores** — Current game scores across MLB, NFL, NBA, and college sports
- **Scoreboard view** — Formatted multi-game scoreboards
- **Schedule lookup** — Upcoming games for any team or league
- **Game details** — Box scores, play-by-play summaries, and key stats

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `fetch-scores` | Model-invoked | Retrieves current scores for a specified sport or team |
| `scoreboard` | User-invoked | `/scoreboard` slash command for formatted scoreboard display |

## Supported Leagues

- **MLB** — Major League Baseball
- **NFL** — National Football League
- **NBA** — National Basketball Association
- **College Baseball** — NCAA Division I
- **College Football** — NCAA FBS

## Installation

```
/plugin install live-scores@Sports-Plugins
```

## Usage

The `fetch-scores` skill activates automatically when you ask about game scores, results, or schedules.

For a quick scoreboard view:

```
/scoreboard mlb
/scoreboard college-baseball
/scoreboard nfl 2026-10-15
```

## MCP Integration

This plugin connects to public sports score APIs. For Codex or other MCP-compatible assistants, the `.mcp.json` endpoint configuration provides tool-use access to the same data.

## Data Sources

Scores are retrieved from public sports APIs (ESPN, NCAA). No API key is required for basic score data.
