---
name: football-data
description: Pull NFL and college football data from free sources — nflverse play-by-play, weekly player stats, schedules with scores and betting lines, rosters and player ids, and College Football Data for the college game — with exact URLs, column meanings, sign conventions and limits. Use when you need real football numbers, are joining data across sources, or are building a pipeline.
---

# Football data

## NFL: nflverse (GitHub releases, CSV, no key)

| Need | URL |
|---|---|
| Play-by-play with EPA, WP, CPOE | `https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2024.csv.gz` |
| Weekly player stats | `https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2024.csv.gz` |
| Schedules, scores, lines | `https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv` (every season in one file) |
| Rosters | `https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2024.csv` |
| Player ids across sites | `https://github.com/nflverse/nflverse-data/releases/download/players/players.csv` |

The football-analytics script downloads and caches play-by-play for you. In Python, `nflreadpy` wraps all of these; `nfl_data_py` is deprecated in its favor and gets no more updates.

Keys and conventions:
- Players are keyed by GSIS id (`00-0034796` is Lamar Jackson). Names collide and change format between files; join on ids.
- Weekly player stats carry `season_type` (`REG`, `POST`). Filter before summing. Lamar Jackson's 2024 regular-season `passing_epa` sums to 172.279 there, the same figure the play-by-play script computes.
- In `games.csv`, `result` is home score minus away score, and `spread_line` is the home team's spread with **positive meaning the home team is favored** (2024 week 1: Chiefs at home, `spread_line` 3, `result` 7). The home team covered when `result > spread_line`. `location` is `Neutral` for the Super Bowl and international games.
- `game_id` looks like `2024_01_BAL_KC` (season, week, away, home) and matches the play-by-play file.
- Team abbreviations follow nflverse (`LA` is the Rams, `LAC` the Chargers, `LV` the Raiders).
- Play-by-play for the current season updates through the week; cite the date you pulled it.

## College: College Football Data

[College Football Data](https://api.collegefootballdata.com/getting-started.md) is the standard source for college games, plays, drives, recruiting and opponent-adjusted stats. Base URL `https://api.collegefootballdata.com`, header `Authorization: Bearer $CFBD_API_KEY`. The key is free (email sign-up, no card) and the free tier is capped at 1,000 calls a month, so pull season-level endpoints and cache them rather than calling per game. Ask the user for their key; never invent one or proceed without telling them it's needed.

College numbers need the same care as NFL ones plus more: success rate there usually means Connelly's yardage definition, not EPA > 0, and schedule strength dominates any raw efficiency number (see football-analytics).

## What not to use

- ESPN's and NFL.com's site APIs are undocumented and change without notice. Use them only for a live score nothing else has yet, and say the source is unofficial.
- Remembered stats. Pull the file.
