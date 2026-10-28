---
name: football-analytics
description: Measure and interpret football efficiency correctly — EPA per play, success rate, CPOE, passer rating, NCAA passing efficiency, early-down passing, garbage time, and why yards and points mislead — using nflverse play-by-play for the NFL and sportsdataverse play-by-play for college. Use when ranking offenses or defenses, evaluating a quarterback, explaining why a team's record and its efficiency disagree, or computing a passer rating.
---

# Football analytics

```bash
F=${CLAUDE_PLUGIN_ROOT}/skills/football-analytics/scripts/nflfast.py
python3 $F teams  --season 2024 --weeks 1-9          # offense and defense EPA/play, success rate, pass vs rush splits
python3 $F player --season 2024 --name L.Jackson     # nflverse short name or GSIS id (00-0034796); a short name two players share is refused
python3 $F rating --cmp 343 --att 502 --yds 4643 --td 45 --int 6          # NFL passer rating → 122.5
python3 $F rating --cmp 402 --att 527 --yds 5671 --td 60 --int 6 --ncaa   # NCAA efficiency → 202.0
```

The NFL script downloads nflverse play-by-play from GitHub releases (free, no key, about 20 MB a season; a finished season is cached for good, the current one for 12 hours; if a refresh fails it falls back to the cached copy and says so). Its passing and rushing EPA match nflverse's own player stats to three decimals; the tests check Lamar Jackson's 2024 season, Josh Allen's 2023 season and one full game.

Short names collide (in 2024 `B.Robinson` is both Bijan and Brian Robinson; `J.Williams` and `Ja.Williams` are one player in different rows), so the script refuses an ambiguous name and lists the ids; pass the id. Weeks 1-18 are the regular season since 2021 and the postseason follows (19-22); use `--season-type POST` or `ALL` for playoff weeks.

College, from sportsdataverse play-by-play (every FBS game, the current season included):

```bash
C=${CLAUDE_PLUGIN_ROOT}/skills/football-analytics/scripts/cfbfast.py
python3 $C teams  --season 2024 --team Texas         # school, full name, abbreviation (TEX) or ESPN id (251); omit --team to rank every team
python3 $C teams  --season 2026 --weeks 1-6 --season-type REG
python3 $C player --season 2024 --name "Quinn Ewers" # passing and rushing EPA, plus the official box-score line and NCAA efficiency → 148.98
```

## Expected points and EPA

Every snap starts in a state — down, distance, field position, time — that is worth some number of points to the offense on average. EPA is the change in that value across one play. A 4-yard gain on 3rd-and-3 is worth far more than a 4-yard gain on 3rd-and-10, and EPA says so; yards do not.

- **EPA per play** is the best single efficiency number. Offense is higher-is-better; for defense, lower EPA allowed is better.
- **Pass and rush EPA separate.** In the 2024 NFL regular season, passes averaged +0.07 EPA per play and runs −0.07 (this script, standard filter). A run-heavy offense needs a reason beyond "establishing the run".
- **qb_epa vs epa.** When a receiver fumbles after the catch, `epa` charges the whole play to the passer; `qb_epa` credits him up to the fumble. nflverse's `passing_epa` sums `qb_epa` over pass and spike plays only, so a two-point try wiped out by a penalty or a fake kick with the kicker throwing doesn't count.
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
- **The college script.** `cfbfast.py` reads sportsdataverse's ESPN play-by-play (free, no key; about 550 MB a season, trimmed to a few MB in the cache; a finished season is kept for good, the current one is refreshed after 24 hours). Its filter is the publisher's: every scrimmage play with an EPA value, so penalties ESPN files as their own plays are out (unlike the NFL script) and a fumble returned for a score is in. Texas' 2024 offense and defense match sportsdataverse's published game boxes game for game; Quinn Ewers' 2024 box-score line matches the official NCAA line (293/445, 3,472 yards, 31 TD, 12 INT, 148.98).
- **Passing lines come from the box score.** ESPN's play-by-play drops a few plays a season (it has 443 Ewers attempts in 2024 against 445 official), so `player` reports EPA from the plays and attempts, yards, touchdowns and efficiency from ESPN's box scores, which add up to the official totals.
- **Season types.** College season totals include bowls and the playoff, so the script's default is `--season-type ALL`. ESPN files every postseason game as week 1; `--weeks` always means regular-season weeks.
- **Success rate** in the script is EPA > 0, the publisher's definition. College Football Data and SP+ use Connelly's yardage thresholds; don't mix them.
- **Opponent adjustment.** The script's EPA is raw. sportsdataverse publishes opponent-adjusted EPA ratings (see football-data); use those to compare teams across conferences.
