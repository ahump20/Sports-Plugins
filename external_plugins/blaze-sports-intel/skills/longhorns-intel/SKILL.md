---
name: longhorns-intel
description: This skill should be used when the user asks about Texas Longhorns baseball, UT Austin baseball, "Hook 'em", Texas baseball players, or any Texas Longhorns college baseball topic. Provides deep intelligence and analytics specific to the University of Texas baseball program.
version: 1.0.0
---

# Texas Longhorns Baseball Intel

Deep intelligence and analytics for the University of Texas at Austin baseball program.

## When This Skill Applies

This skill activates when the user:
- Mentions "Texas Longhorns" and baseball
- Asks about UT Austin baseball players
- Says "Hook 'em" in a baseball context
- Wants Texas baseball schedule, results, or stats
- Asks about SEC baseball with Texas focus
- Discusses Texas baseball recruiting or draft prospects
- References Disch-Falk Field or UFCU Disch-Falk Field

## Program Context

### University of Texas Baseball
- **Conference:** SEC (joined 2024 from the Big 12)
- **Home Field:** UFCU Disch-Falk Field (Austin, TX)
- **National Championships:** 6 (1949, 1950, 1975, 1983, 2002, 2005)
- **College World Series Appearances:** 38 (most all-time)
- **Head Coach:** Check BSI for current season staff

## Instructions

When this skill is invoked:

1. Query the BSI MCP (`https://sabermetrics.blazesportsintel.com/mcp`) for the latest Texas Longhorns data: `bsi_get_team_schedule team=texas` for results and upcoming games, `bsi_get_scoreboard` and `bsi_get_match_detail` for a game, `bsi_get_player_stats` for players, `bsi_get_standings` and `bsi_get_rankings` for conference position and national rank, and `bsi_search_intel` for news. These return traditional stats; compute advanced metrics from them and label them as computed, or say which can't be computed when an input is missing.
2. Provide comprehensive Longhorns-specific intelligence:

### Game Recaps
```
🤘 Texas Longhorns 7, Oklahoma State 3 — Final

  Line Score:
           1  2  3  4  5  6  7  8  9   R   H   E
  OkSt     0  1  0  0  0  2  0  0  0   3   7   1
  Texas    2  0  0  3  0  0  2  0  x   7   11  0

  WP: [Pitcher] (8-2, 2.85 ERA / 3.12 FIP computed)
  LP: [Pitcher] (5-4, 4.21 ERA)

  Key Performers:
  • [Player] — 3-for-4, HR, 3 RBI (.371 wOBA on season)
  • [Player] — 7.0 IP, 5 H, 2 ER, 9 K (28.1% K rate on season)
```

### Roster Analytics
```
🤘 Texas Longhorns Hitting Leaders — 2026

  Player          AVG    wOBA*  ISO*   HR   PA
  ──────────────  ─────  ─────  ─────  ──   ───
  [Player 1]      .345   .412   .241   12   198
  [Player 2]      .312   .389   .198   8    187
  [Player 3]      .298   .371   .276   15   201

  * computed from bsi_get_player_stats counting stats
```

### Season Context
- Current record and conference standing
- Ranking trajectory (week-by-week)
- Conference context from `bsi_get_standings` and `bsi_get_rankings` (no tool returns strength of schedule or RPI)
- Upcoming series and key matchups
- Postseason projections and regional hosting status

3. Include computed sabermetric context alongside traditional stats when the inputs were returned
4. Reference historical program achievements when relevant
5. Note SEC conference context and rivalry matchups

## Rivalries & Key Series

- **Texas vs Texas A&M** — Lone Star Showdown, a conference series again since 2024
- **Texas vs Oklahoma** — Red River rivalry, now an SEC series
- **Texas vs TCU** — in-state non-conference matchup
- **Texas vs LSU** — Historic CWS rivalry

## Tone

Knowledgeable, analytical, and passionate about Longhorns baseball. Data-driven but with the energy of a program with 6 national championships and 38 CWS appearances. Hook 'em. 🤘
