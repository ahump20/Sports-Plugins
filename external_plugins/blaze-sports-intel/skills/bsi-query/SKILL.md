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

All queries are routed through: `https://blazesportsintel.com/mcp`

## Available Queries

### Box Scores
```
Tool: get_box_score
Params: { "team": "Texas", "date": "2026-04-12" }

Returns: Complete box score with:
  - Line score (runs by inning)
  - Batting stats (AB, R, H, RBI, BB, SO + wOBA)
  - Pitching stats (IP, H, R, ER, BB, SO, ERA + FIP)
  - Game notes and highlights
```

### Player Stats
```
Tool: get_player_stats
Params: { "name": "Player Name", "team": "Texas" }

Returns: Full sabermetric profile with:
  - Traditional stats (AVG, HR, RBI or W-L, ERA, K)
  - Advanced metrics (wOBA, wRC+, FIP, xFIP, BABIP)
  - Batted ball / pitch mix data
  - Splits (vs LHP/RHP, home/away, conference/non-conf)
```

### Team Analytics
```
Tool: get_team_stats
Params: { "team": "Texas", "season": 2026 }

Returns: Team-level analytics with:
  - Overall and conference record
  - Team batting and pitching aggregates
  - Advanced metrics (team wOBA, FIP, wRC+)
  - National and conference rank in each category
```

### Standings
```
Tool: get_standings
Params: { "conference": "Big 12" }

Returns: Full conference standings with RPI and advanced metrics
```

## Instructions

When this skill is invoked:

1. Identify what data the user needs
2. Map it to the appropriate BSI MCP tool
3. Format the response clearly with both traditional and advanced stats
4. Add context — conference strength, national ranking, notable trends

## Error Handling

- If the BSI MCP endpoint is unavailable, inform the user and suggest checking blazesportsintel.com directly
- If a player or team is not found, suggest similar matches
- For games not yet played, return the schedule entry instead
