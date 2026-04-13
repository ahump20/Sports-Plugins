---
name: fetch-scores
description: This skill should be used when the user asks about live scores, game results, current games, "what's the score", who won, or game outcomes for any sport. Retrieves real-time score data for MLB, NFL, NBA, college baseball, and college football.
version: 1.0.0
---

# Fetch Scores

Retrieves current and recent game scores for sports leagues.

## When This Skill Applies

This skill activates when the user's request involves:
- Checking live or recent game scores
- Asking "what's the score" for a specific game or team
- Looking up game results or outcomes
- Checking if a team won or lost

## Supported Leagues

| League | Sport | Key |
|--------|-------|-----|
| MLB | Major League Baseball | `baseball/mlb` |
| NFL | National Football League | `football/nfl` |
| NBA | National Basketball Association | `basketball/nba` |
| NCAA Baseball | College Baseball | `baseball/college-baseball` |
| NCAA Football | College Football | `football/college-football` |

## Instructions

When this skill is invoked:

1. Identify the sport and league from the user's query
2. Determine if the user wants a specific team or all games
3. Retrieve score data from the sports scores API endpoint
4. Format the results clearly with:
   - Team names and scores
   - Game status (Final, In Progress with inning/quarter, Scheduled)
   - Key stats if available (winning pitcher, top scorer)

## Response Format

```
🏟️ MLB Scores — April 13, 2026

  Texas Rangers  4    Final
  Houston Astros 3

  Boston Red Sox   2    Top 7th
  New York Yankees 5

  (more games...)
```

## Notes

- For college baseball, include the ranking if the team is ranked
- Always include game status (Final, In Progress, Postponed, Scheduled)
- If no games are currently playing, show the most recent completed games and next scheduled games
