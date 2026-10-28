---
name: interpreting-advanced-metrics
description: >
  Interpret advanced college baseball metrics (wOBA, wRC+, FIP, ERA-, BABIP, ISO,
  K%, BB%) correctly in context. Use when explaining a player's or team's
  advanced stats, when comparing programs, when translating raw numbers into
  analytical conclusions, or when converting a leaderboard into a scouting
  takeaway. Pairs with bsi_get_player_stats, bsi_get_standings, and
  bsi_get_team_schedule from the cbb-sabermetrics plugin.
---

# Interpreting Advanced College Baseball Metrics

The BSI MCP returns traditional stats (`bsi_get_player_stats`) and team results (`bsi_get_standings`, `bsi_get_team_schedule`), not advanced metrics. The team sabermetrics and leaderboard routes are paused on the server until their source and method are documented. So the advanced metrics below are computed from the returned counting stats, with the baseball plugin's `baseball-analytics` script (`saber.py`). Rate stats (AVG, OBP, SLG, ISO, BABIP, K%, BB%) need no league constants. wOBA, wRC+ and FIP do: pass that season's Division I totals with `--totals`, copied from the NCAA or conference stats pages as the baseball plugin's `baseball-data` skill describes, and name the season and source of those totals. Without them, say wOBA, wRC+ and FIP can't be computed; never fall back to the script's MLB `--season` constants. With them, the wOBA scale, R/PA and cFIP come from the college totals, but the relative run values inside wOBA are still MLB's, so say that next to the number. Give the sample with each metric: PA for hitter rates, BF for pitcher K% and BB%, IP for FIP and ERA. Say a metric was computed and give the formula, and if a needed input wasn't returned (for example HBP or SF), say which metric can't be computed instead of guessing. Then frame it: this skill turns numbers into reads.

## The Core Metrics

### wOBA (weighted On-Base Average)
- Combines all offensive events (walks, singles, doubles, triples, HR, HBP) with linear weights derived from run expectancy.
- **Scale:** league average equals league OBP when wOBA is scaled the FanGraphs way. Division I hit .280/.380/.449 in 2024 ([Pitcher List](https://pitcherlist.com/standardizing-college-statistics-evaluating-pitchers/)), so a DI-average wOBA is about .380, not MLB's .310. Judge a hitter by the gap to that season's league figure (+.040 is strong, +.080 is elite), and check which scale the source uses before comparing.
- **Why it matters:** OBP treats every time on base as equal; wOBA weights doubles and home runs higher. A player with .380 OBP driven by walks has a different profile than one with .380 OBP driven by extra-base hits. wOBA differentiates.
- **Use when:** comparing offensive players, building order projections, evaluating recruiting targets.

### wRC+ (weighted Runs Created Plus)
- Park-adjusted, league-adjusted measure of total offensive contribution. 100 is exactly average; 150 means 50% better than average; 70 means 30% below.
- **Scale:** 100 = average, 120+ = strong regular, 150+ = conference all-star, 180+ = all-American.
- **Why it matters:** wOBA doesn't account for park effects (UFCU Disch-Falk plays differently than Alex Box). wRC+ normalizes that. One number, fully contextualized, directly comparable across programs.
- **Use when:** the *only* single number you want for overall offensive value. Lead with this in scouting reports.

### FIP (Fielding Independent Pitching)
- ERA-scaled metric built only from strikeouts, walks, and home runs allowed — the three outcomes a pitcher controls without defensive help.
- **Scale:** matches ERA scale, so it inherits the college run environment: Division I averaged a 6.14 ERA in 2024. A 4.00 FIP is well below the DI average, which makes it much better than average. Compare to the season's league ERA, or use FIP− where the source provides it.
- **Why it matters:** A pitcher can have a high ERA because their defense is bad, or a low ERA because their defense is elite. FIP strips defense out. If ERA and FIP diverge, the pitcher's "true talent" is closer to FIP.
- **Use when:** evaluating pitcher quality absent team defense, projecting forward (FIP is more stable than ERA).
- **ERA− vs FIP−:** both are park- and league-adjusted. 100 = average, below 100 is better (opposite of wRC+).

### BABIP (Batting Average on Balls in Play)
- Batting average when the ball is put in play (excludes strikeouts and home runs).
- **Scale:** DI hitter norm is .310–.330. Pitcher BABIP against is similar, slightly lower.
- **Why it matters:** High hitter BABIP often means good contact + luck. Low BABIP often means bad contact + unluck. When a hitter's season is way above their career BABIP, regression is coming. When a pitcher's BABIP against is way below their norm, their ERA will rise.
- **Use when:** explaining why a hot start may not last, or why a slow start may be luck-driven.

### ISO (Isolated Power)
- SLG minus AVG. Pure extra-base hit production.
- **Scale:** Division I averaged a .169 ISO in 2024 (.449 SLG − .280 AVG). .220+ is real power; MLB's .156 in 2024 is not the right baseline.
- **Why it matters:** separates "slap hitters who make contact" from "slugger." Two hitters can both hit .310 — one with .110 ISO (singles hitter) and one with .230 ISO (middle-of-order bat). Profile matters.

### K% and BB%
- Strikeout rate and walk rate as % of plate appearances. For pitchers, the same — strikeouts and walks issued per batter faced.
- **Scale (hitters):** 18% K% is good, 10% BB% is elite.
- **Scale (pitchers):** 25%+ K% is strong, 8% BB% is problematic, 5% BB% is elite command.
- **Why it matters:** K% and BB% stabilize very early in the season (first 3 weeks). Use them to evaluate pitchers when FIP/ERA are still noisy.

## Season-State Reading

Apply the right lens at the right time:

| Phase | Reliable Metrics | Treat Cautiously |
|---|---|---|
| Feb Wk 1–3 | K%, BB% | ERA, BABIP, ISO, wOBA, FIP |
| Mar Wk 4–8 | Conference rate stats, run diff | Individual BABIP, FIP |
| Apr Wk 9–12 | Most rates | RISP splits (small sample) |
| May Wk 13–16 | Everything | Nothing |

Reading a player's numbers in April with Feb-phase caution is malpractice. Reading them in Feb with May confidence is worse.

## Park-Adjusted Metrics

The BSI MCP does not return park-adjusted metrics (wRC+, ERA−, FIP−) or park factors. Compute them only when you have documented league and park constants to put into the formula, and name the source of those constants. Otherwise present the unadjusted computed metric with a plain-language park note.

Why: UFCU Disch-Falk is a pitcher-friendly park. Alex Box (LSU) plays neutral. Goss Stadium (Oregon State) is pitcher-friendly with marine layer. A .400 wOBA at Disch-Falk is more impressive than .400 at a hitter's park.

## Translating Numbers Into Reads

### Hitter Read Template
> "[Name] posts a .XXX wOBA / XXX wRC+ in [PA] plate appearances across [games] — a [above/below/around] league-average profile. Breakdown: .XXX BABIP (stable/high/low relative to his career), .XXX ISO ([slap hitter / gap power / true slugger] profile), XX% BB rate ([approach-driven / aggressive] bat), XX% K rate ([contact / swing-and-miss] tendency). [Park adjustment note]. [Season-state caveat if Feb/Mar]."

### Pitcher Read Template
> "[Name] runs a X.XX FIP (X.XX ERA) in [IP] innings through [date]. XX% K rate (elite / strong / needs work), XX% BB rate (command / erratic). [Gap between ERA and FIP explains defense/luck contribution]. [ERA− only if league and park constants are documented: XX means [X]% better/worse than league average]. [Arm-count context for May stretch run if applicable]."

### Team Read Template
> "[Team] is [W-L] ([win pct]) and [Xth] in [conference] per `bsi_get_standings`, scoring [X.X] and allowing [X.X] runs per game. Run differential of [+/- XX] through [X] games suggests [sustainable / lucky / unlucky] record. Notable strength: [player with computed metric, formula and sample]. Vulnerability: [specific weakness]. Conference context: [N] Top 25 teams per `bsi_get_rankings`."

## Quality Gates

- Every number cited gets a source and timestamp from the MCP response `meta` envelope.
- Never present a raw wOBA without park context.
- Never present ERA without FIP (they tell different stories).
- When BABIP is extreme, flag regression expectation explicitly.
- When season state is early, name the phase and what metrics are still noise.

## Example Invocations

A user asks: "How's Texas's offense?"
1. Call `bsi_get_standings conference=SEC` and `bsi_get_team_schedule team=texas` for runs scored, run differential and recent results
2. Call `bsi_get_player_stats player={name} team=texas` for the key hitters, and compute their rate metrics from the counting stats returned
3. Apply Team Read Template above
4. Context: SEC, UFCU Disch-Falk park context, current season phase
5. Return a 3-sentence read with source + timestamp, noting which metrics were computed

A user asks: "Who are the top DI hitters right now?"
1. No tool returns a national leaderboard; the BSI leaderboard route is paused. Say so.
2. Offer to rank a set of hitters the user names (or that `bsi_search_intel` surfaces) by pulling each with `bsi_get_player_stats`
3. Compute wOBA, ISO, BABIP, BB%, K% from the counting stats, with sample size, and label the list as covering only those players
4. Flag any early-season caveats
