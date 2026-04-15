---
name: query-stats
description: This skill should be used when the user asks about sports statistics, player stats, team records, league leaders, historical data, or any natural language question about sports numbers. Retrieves and formats structured sports data.
version: 1.0.0
---

# Query Stats

Answers natural language questions about sports statistics across MLB, NFL, NBA, and college sports.

## When This Skill Applies

This skill activates when the user:
- Asks for a specific stat ("what is X's batting average?")
- Wants league leaders in a category
- Asks about team records or standings
- Needs historical or career statistics
- Asks any factual question about sports numbers

## Instructions

When this skill is invoked:

1. Parse the natural language question to identify:
   - **Subject** — Player, team, or league
   - **Stat category** — Batting, pitching, passing, scoring, etc.
   - **Time frame** — Current season, specific year, career, last N games
   - **Sport** — MLB, NFL, NBA, college baseball, college football

2. Retrieve the relevant data

3. Present results in a clean, structured format:

### Single Player Stats
```
📊 Aaron Judge — New York Yankees (2025)

  G    AB    H     HR    RBI   AVG    OBP    SLG    OPS    WAR
  148  520   152   52    118   .292   .398   .638   1.036  8.2
```

### League Leaders
```
📊 MLB Home Run Leaders — 2025

  Rk  Player              Team    HR
  ──  ──────────────────  ──────  ──
   1  Aaron Judge         NYY     52
   2  Shohei Ohtani       LAD     48
   3  Pete Alonso         NYM     42
   ...
```

### Team Stats
```
📊 Texas Longhorns Baseball — 2026

  Record: 38-8 (18-3 Big 12)
  National Rank: #1
  RPI: .628

  Team Batting: .289 AVG, .387 OBP, .472 SLG, 7.8 R/G
  Team Pitching: 3.12 ERA, 3.28 FIP, 10.2 K/9
```

4. Add context when helpful:
   - Where the stat ranks league-wide
   - Notable trends (career-high, slump, hot streak)
   - Relevant comparisons

## Handling Ambiguity

- If the sport is unclear, ask or infer from the stat type
- If the year is unspecified, default to the current season
- If multiple players share a name, present the most likely match and offer alternatives
