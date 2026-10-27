---
name: basketball-analytics
description: Measure and interpret basketball efficiency correctly — possessions, pace, offensive/defensive/net rating per 100, Dean Oliver's Four Factors, true shooting, effective field goal percentage, usage — for the NBA and college. Use when ranking teams, explaining why a team wins, comparing scorers, or converting per-game numbers into per-possession ones.
---

# Basketball analytics

```bash
H=${CLAUDE_PLUGIN_ROOT}/skills/basketball-analytics/scripts/hoops.py
python3 $H player --stats '{"FG":805,"FGA":1598,"3P":402,"3PA":886,"FT":363,"FTA":400,"PTS":2375}'
python3 $H team --league nba --season 2016 --team GS      # ratings + Four Factors from every box score
python3 $H team --league mbb --season 2024 --team DUKE    # men's college; wbb for women's
python3 $H player --stats '{"FGA":1598,"FTA":400,"TOV":262,"MP":2700}' --team-stats '{"FGA":7159,"FTA":1790,"TOV":1245,"MP":19830}'   # usage
```

Seasons are named by the year they end (2016 = 2015-16). Team mode downloads ESPN box scores from sportsdataverse's GitHub releases (free, no key; a finished season is cached for good, the current one for 12 hours; a failed download falls back to the cached copy) and pairs each game with the opponent's own line. `--team` takes ESPN's abbreviation (GS, DUKE), Basketball-Reference's (GSW), the school or city, or ESPN's team_id, in any case; ESPN reuses some college abbreviations (FSU is also Framingham State), so the script picks the team with the most games and names the others. Default is the regular season, without the NBA Cup final, and for college only games between two Division I teams (the output says how many it left out; `--include-non-d1` keeps them). Before mid-January the schedule can't yet tell an NAIA school from a Division I team, so the script uses last season's Division I teams and says so; `--postseason` is postseason only and `--all` both (Sports-Reference and KenPom count a college team's NCAA tournament games in its season). Player stats take FG/FGM, 3P/FG3M/3PM, FT/FTM and TOV/TO; unknown keys are an error, not a silent zero.

Tests check Curry 2015-16 (TS% .669, eFG% .630), Jokic 2023-24 (eFG% .612) and the 2015-16 Warriors to the tenth of Basketball-Reference (ORtg 114.5, DRtg 103.8). The 2015-16 Spurs (110.3 / 99.0), 2023-24 Lakers (115.9 / 115.3, 82 games) and 2023-24 Celtics (123.2 / 111.6) also match. Turnovers come from ESPN's `total_turnovers`, which includes team turnovers as Basketball-Reference's TOV does.

## Think in possessions

Both teams get almost the same number of possessions in a game, so per-game totals mostly measure tempo. A fast team scores more points per game and allows more; that says nothing about whether it is good.

- **Possessions** (Basketball-Reference's estimate): FGA + 0.4·FTA − 1.07·(ORB share)·missed FG + TOV, averaged over both teams. The quick one-team version is FGA − ORB + TOV + 0.475·FTA (KenPom's free-throw weight). Say which you used; the two differ by a possession or two per game.
- **Offensive / defensive rating** = points scored / allowed per 100 possessions. **Net rating** = the difference, the single best summary of team strength over a season.
- **Pace** = possessions per 48 minutes (NBA) or per 40 (WNBA, college). The script reports possessions per game, not Pace: ESPN's team box scores carry no minutes, so overtime isn't removed (2015-16 Warriors: 100.3 per game against Basketball-Reference's Pace of 99.3).
- Ratings differ by source. Basketball-Reference, NBA.com and KenPom each count possessions a little differently; quote the source with the number.

## Four Factors

Dean Oliver's breakdown of why a team scores or stops scoring, with his approximate weights ([Basketball-Reference](https://www.basketball-reference.com/about/factors.html)):

| Factor | Formula | Weight |
|---|---|---|
| Shooting | eFG% = (FG + 0.5·3P) / FGA | 40% |
| Turnovers | TOV% = TOV / (FGA + 0.44·FTA + TOV) | 25% |
| Rebounding | ORB% = ORB / (ORB + Opp DRB) | 20% |
| Free throws | FT / FGA | 15% |

Run each factor for the offense and for the defense (the opponent's factors). Shooting usually explains the most; a team that turns it over rarely and crashes the offensive glass can win with ordinary shooting.

## Scoring efficiency

- **TS%** = PTS / (2·(FGA + 0.44·FTA)). Counts threes and free throws; the best single shooting-efficiency number for a scorer.
- **eFG%** credits threes but ignores free throws. A player who lives at the line looks worse by eFG% than by TS%.
- **Usage rate** is the share of team plays a player ends (shot, free-throw trip, turnover) while on the floor. Efficiency and usage trade off: hold TS% against usage, and don't compare a 30% usage star's TS% to a 15% usage spot-up shooter's without saying so.
- **Points per game** mixes minutes, pace and usage. Convert to per-36 or per-100 possessions before comparing players.

## When the numbers lie

- **Three-point percentage** swings for a long time. Over a few hundred attempts, a good and an average shooter can trade places. Lean on volume and career rate before calling a shooter hot or cold.
- **Opponent three-point percentage** is mostly outside a defense's control; how many threes it allows, and from where, is more repeatable.
- **Plus-minus and on/off** depend on teammates and opponents. Single-season, single-player on/off is noisy; use multi-season or adjusted versions and say which.
- **Garbage time** inflates bench numbers and deflates starters' net rating in blowouts.
- **Close-game record** regresses; net rating predicts next season's wins better than win-loss does.

## College specifics

- Games are 40 minutes, not 48, and possessions run fewer per game, so per-game numbers aren't comparable with the NBA's even before talent.
- **Schedule strength dominates.** Raw efficiency against a weak non-conference slate means little. Opponent-adjusted efficiency (KenPom, Bart Torvik, the NCAA's NET) is the standard; name the system you cite.
- **Home court** is worth more in college than in the NBA. Check where games were played before reading a single-game result.
- **Rosters turn over fast** with the transfer portal; last season's team ratings are a weak prior.
