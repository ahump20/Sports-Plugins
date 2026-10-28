---
name: football-data
description: Pull NFL and college football data from free sources — nflverse play-by-play, weekly player stats, schedules with scores and betting lines, rosters and player ids; sportsdataverse college play-by-play, box scores and opponent-adjusted ratings; College Football Data for rankings, recruiting and the transfer portal — with exact URLs, column meanings, sign conventions and limits. Use when you need real football numbers, are joining data across sources, or are building a pipeline.
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

## College: sportsdataverse (GitHub releases, CSV, no key)

| Need | URL |
|---|---|
| Play-by-play with EPA and win probability | `https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_pbp/play_by_play_2024.csv` |
| Player box scores (official lines) | `https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_player_box/player_box_2024.csv` |
| Team box scores | `https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_team_box/team_box_2024.csv` |
| Advanced game boxes (EPA, success, explosiveness) | `.../espn_cfb_adv_team/adv_team_2024.csv`, `.../espn_cfb_adv_passing/adv_passing_2024.csv`, `.../espn_cfb_adv_situational/adv_situational_2024.csv` |
| Opponent-adjusted EPA ratings | `https://github.com/sportsdataverse/sportsdataverse-data/releases/download/cfb_ratings/cfb_ratings_2026.csv` |
| ESPN FPI by week | `https://github.com/sportsdataverse/sportsdataverse-data/releases/download/cfb_fpi_weekly/cfb_fpi_weekly_2026.csv` |

The football-analytics script downloads, trims and caches the play-by-play and player box for you. The play-by-play file is about 550 MB a season with 500 columns; don't load it whole when a few columns will do.

Keys and conventions:
- Teams are keyed by ESPN id (`251` is Texas, `130` Michigan); players by ESPN athlete id (`4889929` is Quinn Ewers). `pos_team` is the full name ("Texas Longhorns"); `homeTeamName` is the school ("Texas") and `homeTeamAbbrev` the abbreviation ("TEX").
- `seasonType` is `2` for the regular season and `3` for the postseason, and every postseason game is week 1.
- Flags are the strings `true` and `false`. `scrimmage_play` is false for kneels, penalties and kicks; `EPA_success` is EPA > 0.
- The advanced boxes round EPA totals to two decimals. Summing them reproduces a season within a few hundredths.
- The ratings file adjusts EPA for opponents (`adj_off_epa`, `adj_def_epa`, `adj_net`, with ranks) and updates through the season; `games` says how many games it has seen.
- These files are rebuilt from ESPN as the season goes, and a rebuild can move old values slightly. Cite the date you pulled them.

## College: College Football Data (free key)

[College Football Data](https://api.collegefootballdata.com/getting-started.md) covers what sportsdataverse doesn't: poll rankings, recruiting and the transfer portal. Base URL `https://api.collegefootballdata.com`, header `Authorization: Bearer $CFBD_API_KEY`. The key is free (email sign-up). Ask the user for their key; never invent one or proceed without telling them it's needed. Pull season-level endpoints and cache them rather than calling per game.

| Need | Endpoint |
|---|---|
| AP, Coaches and CFP polls | `/rankings` |
| Recruits and class rankings | `/recruiting/players`, `/recruiting/teams` |
| Transfer portal | `/player/portal` |
| SP+, FPI, SRS, Elo | `/ratings/sp`, `/ratings/fpi`, `/ratings/srs`, `/ratings/elo` |
| Roster talent composite | `/talent` |

Recruiting stars and portal entries change by the day; give the date with any list. College Football Data's success rate uses Connelly's yardage thresholds and its "PPA" is its own expected-points model, so neither matches sportsdataverse's EPA figures.

## What not to use

- ESPN's and NFL.com's site APIs are undocumented and change without notice. Use them only for a live score nothing else has yet, and say the source is unofficial.
- Remembered stats. Pull the file.
