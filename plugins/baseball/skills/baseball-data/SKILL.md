---
name: baseball-data
description: Pull MLB and college baseball data from free, keyless sources — MLB Stats API (schedules, live scores, standings, box scores, player season stats), Baseball Savant leaderboards and pitch-level Statcast CSVs, and the Lahman database — with the exact URLs, JSON paths and gotchas. Use when you need real numbers instead of remembered ones, or when building a pipeline.
---

# Baseball data

Fetch, don't recall. Every number below came from these URLs on the date the skill was written; re-pull before quoting.

## MLB Stats API (statsapi.mlb.com, JSON, no key)

| Need | URL | Where the answer is |
|---|---|---|
| Games on a date | `/api/v1/schedule?sportId=1&date=2024-07-04&hydrate=linescore` | `dates[0].games[]` → `gamePk`, `teams.away/home.team.name`, `.score`, `status.detailedState` |
| Standings | `/api/v1/standings?leagueId=103,104&season=2024&standingsTypes=regularSeason` | `records[].teamRecords[]` → `team.name`, `wins`, `losses`, `winningPercentage`, `gamesBack`, `runDifferential`, `divisionRank` |
| Box score | `/api/v1/game/{gamePk}/boxscore` | `teams.away/home.teamStats.batting\|pitching\|fielding`; players under `teams.*.players["ID660271"].stats` (game) and `.seasonStats` |
| Player season | `/api/v1/people/{id}/stats?stats=season&season=2024&group=hitting` (or `pitching`) | `stats[0].splits[]` |

Prefix every path with `https://statsapi.mlb.com`. `sportId=1` is MLB; minor leagues use other ids.

Gotchas:
- `records[].division` carries only an id and link, not the division name. Map the ids to names yourself (`/api/v1/divisions?sportId=1` lists them).
- In a box score, `teamStats.pitching.runs` is runs **allowed** by that team's pitchers.
- A traded player's season stats come back as one split per team plus a combined split. `saber.py --mlb-person` takes the combined one; do the same.
- `inningsPitched` is a string in box-score notation (`"6.2"` = 6⅔).

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/baseball-analytics/scripts/saber.py batting --season 2024 --mlb-person 660271` fetches a season line and runs the metrics in one step.

## Baseball Savant (Statcast, CSV, no key)

Leaderboards return CSV when you add `csv=true`:

```
https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter&year=2024&position=&team=&filterType=pa&min=q&csv=true
https://baseballsavant.mlb.com/leaderboard/statcast?type=batter&year=2024&position=&team=&min=q&csv=true
https://baseballsavant.mlb.com/leaderboard/percentile-rankings?type=batter&year=2024&position=&team=&csv=true
```

Use `type=pitcher` for pitchers; `min=q` means qualified. The expected-stats file has `pa, bip, ba, est_ba, slg, est_slg, woba, est_woba` and the differences; its first column is a single quoted `"last_name, first_name"` field and the file starts with a UTF-8 byte-order mark, so open it with `encoding="utf-8-sig"`. Savant's 2024 wOBA for Ohtani (.431) matches `saber.py`.

Pitch-level data comes from `statcast_search/csv` (the endpoint pybaseball wraps), e.g. every pitch of one game: `https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details&game_pk={gamePk}`, with the `gamePk` from the schedule endpoint. Large date ranges time out; pull a few days at a time.

Expected stats (xBA, xwOBA) describe contact quality, not outcomes. A big wOBA − xwOBA gap is a question to investigate, not proof of luck: speed and spray direction aren't fully in the model.

## History: Lahman database

SABR's [Lahman database](https://sabr.org/lahman-database/) covers 1871–2025 (version released January 2, 2026), as CSV, SQL or Access. Use it for career and historical questions; the API above is better for anything current. One row per player-season-stint, so a traded player has several rows in a season; sum them.

## College baseball

No free official API is documented for NCAA baseball statistics. Copy team or league totals from the NCAA or conference stats pages and run `saber.py league --totals …` to build that league's own constants; never apply MLB constants to a college line.

## Rate and courtesy

These are public endpoints with no published rate limit. Cache responses, don't hammer them in loops, and prefer one season-level request over hundreds of per-game ones.
