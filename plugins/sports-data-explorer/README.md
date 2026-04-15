# Sports Data Explorer Plugin

A general-purpose sports data exploration plugin for querying stats, comparing players, and generating analytical insights.

## Features

- **Stat queries** — Look up any stat for any player, team, or season
- **Player comparisons** — Side-by-side advanced stat comparisons
- **Leaderboards** — League leaders in any category with filters
- **Historical data** — Season-by-season stat lookups and career progressions
- **Team profiles** — Roster, season stats, schedule, and standings context

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `query-stats` | Model-invoked | Answers natural language questions about sports statistics |
| `compare-players` | User-invoked | `/compare` command for side-by-side player comparisons |

## Supported Sports

- **MLB** — Complete batting, pitching, and fielding statistics
- **NFL** — Passing, rushing, receiving, defensive stats
- **NBA** — Traditional and advanced basketball metrics
- **College Baseball** — Full sabermetric profiles (via BSI)
- **College Football** — Team and player stats with transfer portal data

## Installation

```
/plugin install sports-data-explorer@Sports-Plugins
```

## Usage

The query-stats skill activates automatically when you ask about sports data, statistics, or historical records.

```
# Compare two players
/compare Mike Trout vs Aaron Judge 2025
/compare Jalen Hurts vs Lamar Jackson career
```

## Data Philosophy

This plugin aims to make sports data as accessible as possible to AI coding assistants. Whether you're building a sports app, writing an article, or just curious — ask in natural language and get structured data back.
