---
name: bsi-query
description: This skill should be used when the user asks about college baseball data, box scores, NCAA baseball statistics, college baseball rankings, D1 baseball players, or any request that could be served by the Blaze Sports Intel analytics engine. Queries the BSI MCP endpoint for structured college baseball data.
version: 1.0.0
---

# BSI Query

Queries the Blaze Sports Intel analytics engine for college baseball data via the BSI MCP endpoint.

## When This Skill Applies

This skill activates when the user:
- Asks for a college baseball box score
- Wants NCAA baseball statistics or rankings
- Requests sabermetric data for college players
- Asks about D1 baseball conference standings
- Needs schedule or game results for college teams
- Inquires about college baseball recruiting or draft prospects

## MCP Endpoint

All queries are routed through: `https://sabermetrics.blazesportsintel.com/mcp`

POST JSON-RPC only, no streaming, no API key, 30 requests per minute per IP. Every response carries `meta.source`, `meta.fetched_at` and `meta.timezone` (America/Chicago). The server exposes 7 read-only college baseball tools, listed below. It has no box score, team stats, leaderboard, power index, or MLB, NFL, NBA or college football tools.

## Available Queries

### Scoreboard
```
Tool: bsi_get_scoreboard
Params: { "date": "2026-04-12", "conference": "SEC" }   (both optional)

Returns: Games for the date with scores, venue and status
```

### Game Detail
```
Tool: bsi_get_match_detail
Params: { "matchId": "<id from bsi_get_scoreboard>" }

Returns: Venue, weather, win predictions, play-by-play and team stats for one game
```

### Player Stats
```
Tool: bsi_get_player_stats
Params: { "player": "Player Name", "team": "texas" }   (team optional)

Returns: Identity, team, position, and traditional batting or pitching stats
when the source has them
```

Advanced metrics (wOBA, FIP, BABIP, ISO) are not returned. Compute them from the counting stats with the baseball plugin's `saber.py`. wOBA and FIP need that season's Division I totals passed with `--totals` (never the script's MLB constants); without them, say those two can't be computed, and with them, note that wOBA's relative run values are still MLB's. Then show the formula and sample size, and say they were computed. If an input such as HBP or SF wasn't returned, say which metric can't be computed.

### Team Schedule
```
Tool: bsi_get_team_schedule
Params: { "team": "texas" }   (name or slug, like "texas" or "lsu")

Returns: Past results and upcoming games
```

### Standings
```
Tool: bsi_get_standings
Params: { "conference": "SEC" }   (optional)

Returns: W, L, win pct, runs scored, runs allowed, run differential, streak, games back
```

### Rankings
```
Tool: bsi_get_rankings
Params: {}

Returns: National Top 25 with rank, record and movement
```

### News and Scouting Context
```
Tool: bsi_search_intel
Params: { "query": "Texas baseball weekend rotation", "limit": 5 }   (limit 1-10, domains optional)

Returns: Web search results from trusted college-baseball sources
```

## Instructions

When this skill is invoked:

1. Identify what data the user needs
2. Map it to the appropriate BSI MCP tool
3. Format the response clearly with traditional stats, plus any advanced metrics computed from them (labeled as computed)
4. Add context — conference standing, national ranking, notable trends

## Error Handling

- If the BSI MCP endpoint is unavailable, inform the user and suggest checking blazesportsintel.com directly
- If a player or team is not found, suggest similar matches
- For games not yet played, return the schedule entry instead
