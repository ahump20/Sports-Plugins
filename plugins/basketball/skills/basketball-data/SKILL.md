---
name: basketball-data
description: Pull NBA, men's college and women's college basketball data from free sources — sportsdataverse's ESPN box-score and schedule files, stats.nba.com via nba_api, and Basketball-Reference — with exact URLs, column names, season and game-type codes, rate limits and the traps that corrupt season totals. Use when you need real basketball numbers or are building a pipeline.
---

# Basketball data

## Box scores and schedules: sportsdataverse (GitHub releases, CSV, no key)

```
https://github.com/sportsdataverse/sportsdataverse-data/releases/download/{dataset}/{file}_{season}.csv
```

| Need | NBA | Men's college | Women's college |
|---|---|---|---|
| Team box scores | `espn_nba_team_boxscores` / `team_box` | `espn_mens_college_basketball_team_boxscores` / `team_box` | `espn_womens_college_basketball_team_boxscores` / `team_box` |
| Player box scores | `espn_nba_player_boxscores` / `player_box` | `espn_mens_college_basketball_player_boxscores` / `player_box` | same pattern |
| Schedules | `espn_nba_schedules` / `nba_schedule` | | |

Seasons are named by the year they end: `player_box_2024.csv` is 2023-24. The basketball-analytics script downloads and caches team box scores for you.

Traps, all checked against the 2023-24 NBA file:
- `season_type` is `2` for the regular season, `3` for playoffs and `5` for the play-in.
- **The All-Star Game is in `season_type` 2.** Stephen Curry has 75 regular-season rows that year: 74 Warriors games plus one for "Western Conf All-Stars". The file lists 32 teams, not 30. Drop rows whose team or opponent is an All-Star side before summing. `hoops.py` does this by pairing each game with a real opponent row.
- Player rows have `did_not_play`, `minutes`, `starter` and `plus_minus`; filter on `did_not_play` before counting games.
- Keys are ESPN ids (`athlete_id`, `team_id`, `game_id`), not NBA.com or Basketball-Reference ids.
- **Use `total_turnovers`, not `turnovers`.** `turnovers` is the players' sum and leaves out team turnovers (shot-clock and 8-second violations); `total_turnovers` matches Basketball-Reference's TOV (2015-16 Warriors 1245, not 1219). With it, team ratings from these files match Basketball-Reference to the tenth. One 2025-26 row has `total_turnovers` blank; fall back to `turnovers`.
- **The NBA Cup final is in `season_type` 2** but counts in no season totals (2023-24 Lakers: 83 rows, 82 games). Find it in the schedule file (`espn_nba_schedules` / `nba_schedule`), where `type_abbreviation` is `CC`; All-Star games there are `ALLSTAR`.
- The latest NBA file is the season in progress (`team_box_2027.csv` exists in October 2026). A season that isn't published returns 404 (men's and women's college have no 2027 file yet).

## NBA.com stats: nba_api

`nba_api` (Python) wraps stats.nba.com, the source for tracking, lineup and play-type data that box scores don't carry. Its own README warns that stats.nba.com throttles rapid requests and does not respond to many cloud-hosting IP ranges (AWS, GCP, Azure, Colab). From a server, expect hangs; sleep about a second between calls, raise the timeout, or run it from a home connection.

## Basketball-Reference

The reference for historical and advanced numbers (per-100, BPM, Win Shares) and for checking your own calculations. Sports Reference allows at most 20 requests a minute on its sites (10 on FBref and Stathead); going over locks you out for up to a day. Fetch a season page once and parse it, never a page per player in a tight loop. College lives on sports-reference.com/cbb.

## College specifics

- Opponent-adjusted ratings (KenPom, Bart Torvik, the NCAA's NET) are the standard for ranking teams. KenPom is paid; don't promise numbers from it you can't fetch.
- The 2023-24 men's file has 717 distinct teams, about twice the size of Division I, because every game a Division I team played is in it, NAIA and Division II opponents included. KenPom, Sports-Reference and the NET leave those games out (Baylor 2023-24: 24-11 on baylorbears.com, 23-11 against Division I). The file has no division column; a Division I team plays a full schedule while a non-Division I school shows up for at most 8 games, all before January, so games played separates them (362 teams in 2023-24, the NCAA's count). `hoops.py` does this for you.
- **Abbreviations repeat across schools.** In 2023-24, FSU is Florida State and Framingham State, LOU is Louisville and Lourdes, PENN (women) is Pennsylvania and Penn State-Beaver. Key on `team_id`.
- `season_type` 3 holds the NCAA tournament and other postseason events; conference tournaments are in 2. Sports-Reference and KenPom count both in a season.
