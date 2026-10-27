---
name: football-analytics
description: Measure and interpret football efficiency correctly — EPA per play, success rate, CPOE, passer rating, NCAA passing efficiency, early-down passing, garbage time, and why yards and points mislead — using nflverse play-by-play for the NFL and the same concepts for college. Use when ranking offenses or defenses, evaluating a quarterback, explaining why a team's record and its efficiency disagree, or computing a passer rating.
---

# Football analytics

```bash
F=${CLAUDE_PLUGIN_ROOT}/skills/football-analytics/scripts/nflfast.py
python3 $F teams  --season 2024 --weeks 1-9          # offense and defense EPA/play, success rate, pass vs rush splits
python3 $F player --season 2024 --name L.Jackson     # nflverse short name or GSIS id (00-0034796)
python3 $F rating --cmp 343 --att 502 --yds 4643 --td 45 --int 6          # NFL passer rating → 122.5
python3 $F rating --cmp 402 --att 527 --yds 5671 --td 60 --int 6 --ncaa   # NCAA efficiency → 202.0
```

The script downloads nflverse play-by-play from GitHub releases (free, no key, about 20 MB a season, cached 12 hours). Its player totals equal nflverse's own player stats to three decimals; the tests check that against Lamar Jackson's 2024 season and one full game.

## Expected points and EPA

Every snap starts in a state — down, distance, field position, time — that is worth some number of points to the offense on average. EPA is the change in that value across one play. A 4-yard gain on 3rd-and-3 is worth far more than a 4-yard gain on 3rd-and-10, and EPA says so; yards do not.

- **EPA per play** is the best single efficiency number. Offense is higher-is-better; for defense, lower EPA allowed is better.
- **Pass and rush EPA separate.** In the 2024 NFL regular season, passes averaged +0.07 EPA per play and runs −0.07 (this script, standard filter). A run-heavy offense needs a reason beyond "establishing the run".
- **qb_epa vs epa.** When a receiver fumbles after the catch, `epa` charges the whole play to the passer; `qb_epa` credits him up to the fumble. nflverse's `passing_epa` uses `qb_epa`.
- **The model is nflverse's** (nflfastR). Values can shift slightly between data releases; cite the season and the date you pulled it.

## Success rate

Two definitions are in common use. Name the one you use.

- **EPA > 0** (nflverse's `success` column, used by this script).
- **Yardage thresholds**: 50% of the yards to go on 1st down, 70% on 2nd, 100% on 3rd and 4th. This is Bill Connelly's definition and the one College Football Data publishes.

Success rate measures consistency; EPA per play adds explosiveness. A team high in both is good; high EPA with low success rate lives on big plays, which repeat less reliably.

## The standard filter, and why

The script keeps plays where EPA exists and `pass == 1` or `rush == 1`. That keeps sacks and scrambles as passes, drops kneels, spikes and special teams, and keeps plays nullified by penalty, because a holding call is part of how an offense played. When you compare against another site's numbers, check its filter first: most disagreements are filter disagreements.

Common optional cuts:
- **Garbage time.** Many analysts drop plays where the offense's win probability is below 10% or above 90% (`wp` column) so blowouts don't distort efficiency. State the cut if you use one.
- **Early downs.** Pass rate and EPA on 1st and 2nd down tell you more about play-calling than overall pass rate, which is inflated by trailing teams throwing late.

## Quarterbacks

- **EPA per dropback** (sacks and scrambles included) is the best single passing number; sacks are partly the quarterback's.
- **CPOE** compares completion rate to what the throw difficulty predicts. Pair it with EPA: CPOE alone rewards short, safe throws.
- **NFL passer rating** caps each of its four parts between 0 and 2.375, so 158.3 is the ceiling; it counts no sacks, rushing or fumbles, and treats a 1-yard touchdown like a 70-yard one.
- **NCAA passing efficiency** has no caps (above 200 is possible) and is not on the same scale as NFL rating. Never compare the two.

## Why records, points and yards mislead

- **Yards per game** rewards pace and garbage time. Use per-play rates.
- **Points allowed** includes defensive and special-teams scores and short fields the offense gave away. Split them.
- **One-score games** are close to coin flips over a season. A record built on many close wins usually falls back toward what point differential and EPA say.
- **Turnovers** swing EPA and wins heavily, and who recovers a fumble is close to random. Don't project a fumble-recovery edge forward.
- **Sample size.** A 17-game NFL season gave each offense 1,025 to 1,176 plays in 2024 (standard filter); a single game's EPA per play is noisy, and a college team plays 12 or 13 regular-season games against schedules that vary enormously.

## College specifics

- **Schedule strength dominates.** Raw EPA in college mostly measures opponents; prefer opponent-adjusted ratings (SP+, FPI) when you can get them, and say whose.
- **Clock rules differ.** Since 2023 the college clock no longer stops after a first down except in the last two minutes of each half. Compare college offenses per play, never per game.
- **Data.** nflverse covers the NFL only. College play-by-play with EPA and success rate comes from College Football Data (free key, 1,000 calls a month); see the football-data skill.
