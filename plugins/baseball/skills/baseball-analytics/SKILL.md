---
name: baseball-analytics
description: Compute and interpret baseball metrics correctly — wOBA, wRC+, FIP, BABIP, ISO, K%, BB%, ERA vs FIP gaps, sample-size reliability, park and era context — for MLB and college. Use when calculating or explaining a hitter's or pitcher's numbers, comparing players across seasons or leagues, judging whether a hot or cold stretch is real, or building NCAA league baselines from totals.
---

# Baseball analytics

Never compute these in your head. Run the script; it carries FanGraphs' published constants for 2010–2026 and reproduces FanGraphs' numbers (tests check Ohtani 2024 wOBA .431 and Skubal 2024 FIP 2.49).

```bash
S=${CLAUDE_PLUGIN_ROOT}/skills/baseball-analytics/scripts/saber.py
python3 $S batting  --season 2024 --stats '{"PA":731,"AB":636,"H":197,"2B":38,"3B":7,"HR":54,"BB":81,"IBB":10,"HBP":6,"SF":5,"SO":162}'
python3 $S pitching --season 2024 --stats '{"IP":"192.0","HR":15,"BB":35,"HBP":9,"SO":228,"ER":51,"BF":753}'
python3 $S batting  --season 2024 --mlb-person 660271      # pulls counting stats from the MLB Stats API
python3 $S league   --totals '{"PA":182449,"AB":163687,"R":21343,"H":39823,"2B":7771,"3B":697,"HR":5453,"BB":14929,"IBB":509,"HBP":2020,"SF":1261,"SO":41197}'
```

The `league` line is MLB 2024 (Baseball-Reference totals); swap in your league's. Add `"ERA"` and `"IP"` (a string, `"14000.1"`) from the same totals to get cFIP. Without `R` and `PA`, wRC+ comes back `null`; without `ERA` and `IP`, FIP does. The script never fills them with MLB's values, and says so on stderr.

Batting output: AVG/OBP/SLG/OPS, ISO, BABIP, K%, BB%, wOBA, wRAA, wRC+. Pitching: FIP, ERA, K/9, BB/9, HR/9, K%, BB%. Pass `--park-factor 1.05` (or FanGraphs' displayed `105`) to park-adjust wRC+. A rate with a zero denominator (0 AB, 0 PA, 0 IP) is `null`, not `.000`. Bad input (IBB above BB, more extra-base hits than hits, negative counts, an unknown season, an unreachable API) exits 2 with a one-line error.

## Inputs that trip people up

- `IP` is box-score notation: `6.2` is 6⅔ innings. The script rejects `6.5`.
- wOBA uses unintentional walks (BB − IBB). Leave IBB out and a hitter who gets pitched around looks better than he is.
- A traded player's MLB Stats API record has one split per team plus a combined one; the script takes the combined split.
- wRC+ from the script matches FanGraphs within a few points, not exactly: FanGraphs divides by the league's non-pitcher wRC/PA (AL or NL) and uses its own park factors. Quote FanGraphs' published wRC+ when you can fetch it; use the script for leagues FanGraphs doesn't cover.

## What each number means, and when it lies

| Metric | Scale | What it captures | When it misleads |
|---|---|---|---|
| wOBA | On the OBP scale; league average equals league OBP that season | Each way of reaching base weighted by its run value | Not park- or league-adjusted. A .340 at Coors and a .340 in Seattle are different hitters |
| wRC+ | 100 = league average; 150 = 50% better | Park- and league-adjusted run creation | Inherits wOBA's blind spots: no baserunning, no defense, no position |
| wRAA | Runs above average | Counting version of wOBA | Grows with playing time; compare per PA for rate questions |
| FIP | ERA scale | What ERA would be from K, BB, HBP and HR alone | Ignores contact quality on balls in play. Extreme ground-ball or weak-contact pitchers can beat it for years |
| ERA − FIP | Runs per 9 | Defense, sequencing, BABIP and strand-rate luck | A gap of 0.5+ usually narrows, but not to zero for every pitcher |
| BABIP | Around .290–.300 in MLB | Hits on balls in play | Hitters own their BABIP more than pitchers do: speed and line drives sustain a high one. Pitcher BABIP needs ~2000 balls in play to mean much |
| ISO | SLG − AVG | Raw extra-base power | Doubles-heavy and homer-heavy hitters can share an ISO |
| K%, BB% | Per PA (hitters) or BF (pitchers) | Plate discipline and bat-missing | Use these, not K/9, to compare pitchers: K/9 rewards pitchers who allow more baserunners |

xFIP needs fly-ball counts, which box scores don't carry. Don't approximate it from FIP.

## How much data before a rate means something

Russell Carleton's .49 reliability points, from the [FanGraphs sample-size page](https://library.fangraphs.com/principles/sample-size/):

| Hitters | | Pitchers | |
|---|---|---|---|
| K% | 60 PA | K% | 70 BF |
| BB% | 120 PA | BB% | 170 BF |
| HR rate | 170 PA | GB% / FB% | 70 BIP |
| ISO | 160 AB | OBP against | 540 BF |
| SLG | 320 AB | AVG against | 630 BF |
| OBP | 460 PA | HR/FB | 400 FB |
| BABIP | 820 BIP | BABIP | 2000 BIP |
| AVG | 910 AB | | |

At that sample, observed rate and true talent count about equally; below it, lean on the prior (career rate, projection, league average). A 56-game college season gives a regular roughly 230–270 PA, so a college hitter's single-season AVG and BABIP are mostly noise, while K% and BB% are already informative.

## Context before comparison

- **Era.** League run scoring moves: MLB wOBA was .320 in 2019–2020 and .310 in 2022 and 2024. Compare players through league-relative stats (wRC+, ERA−, FIP−) or through wOBA minus that season's league wOBA.
- **Park.** Coors Field inflates offense more than any other MLB park; a road/home split is the quickest sanity check when you have no park factor.
- **College is a different run environment.** Division I averaged a 6.14 ERA and a .280/.380/.449 line in 2024 ([Pitcher List](https://pitcherlist.com/standardizing-college-statistics-evaluating-pitchers/)), driven partly by BBCOR bats. MLB baselines do not transfer. Build constants from the league's own totals with `league` mode: it sets league wOBA equal to league OBP with intentional walks removed (FanGraphs' rule; MLB 2024: .310 against a .312 OBP), derives the wOBA scale, R/PA and cFIP from those totals, and keeps MLB's relative run values (an approximation worth saying out loud).
- **Conference and schedule strength** matter more in college than park does. Weekend Friday starters face a different lineup quality than midweek arms.
- **Role.** Relievers post lower ERAs and higher K% than starters with the same stuff; don't compare a closer's FIP to a starter's without saying so.

## Reading a line, in order

1. Playing time first: PA or BF tells you which rates to trust.
2. K% and BB%: the most stable signal early.
3. Contact: ISO for power, BABIP against the player's own history.
4. The run-value summary: wOBA/wRC+ for hitters, FIP beside ERA for pitchers.
5. Context: park, league, era, role, opponent quality.
6. Only then a verdict, and name the uncertainty that remains.
