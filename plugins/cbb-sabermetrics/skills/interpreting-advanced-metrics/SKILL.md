---
name: interpreting-advanced-metrics
description: Use when interpreting or calculating college baseball wOBA, wRC+, FIP, BABIP, ISO, strikeout rates or walk rates, especially when source inputs, league constants or sample coverage are incomplete.
---

# Advanced metrics with explicit inputs

A computed rate is a description of observed events, not a validated talent forecast. Follow `college-baseball-data` to retrieve and verify the requested player/team observations, preserving source, season, split and cutoff. Check raw inputs against any published rate before calculating; partial accumulation or zero-filled missing fields can make a provider's own line internally inconsistent. Allow for documented display rounding before calling a difference an error.

## Calculation path

Use the installed `baseball-analytics` skill's `scripts/saber.py`; read its `--help` and input contract rather than guessing arguments. For NCAA calculations needing league constants, pass published totals for the requested division and season with `--totals`. If the helper supports only Division I for that calculation, do not relabel DI results for DII, DIII, NAIA or junior college. Do not silently use the helper's MLB `--season` defaults for college players. If the helper or totals are unavailable, name what cannot be computed.

The helper's totals object shares HR, BB, HBP and SO between batting and FIP calculations. Report FIP from `--totals` only after confirming those counts also match the pitching totals for the same league, season and game population. Out-of-league games can break that agreement. If matching pitching totals are unavailable, leave FIP unavailable.

The college-total workflow rescales its weights to the supplied run environment, but its relative event values still originate from MLB. Label that methodological limitation; do not call the result an official NCAA metric or a college-trained model.

| Metric | Required context |
|---|---|
| AVG, OBP, SLG, ISO | Exact counting-stat inputs and denominator; ISO is SLG minus AVG |
| BABIP | Hits, home runs, at-bats, strikeouts and sacrifice flies |
| Hitter K% / BB% | Strikeouts / walks and plate appearances |
| Pitcher K% / BB% | Strikeouts / walks and batters faced, not innings |
| FIP | Home runs, walks, HBP, strikeouts, innings and the correct league constant |
| wOBA | Event counts and documented weights for the specified scale |
| wRC+, ERA-, FIP- | Defined league, season and park adjustments; no guessed park factor |

Baseball innings notation is not decimal arithmetic: .1 and .2 denote one and two outs. Use the helper's documented conversion. Missing HBP, sacrifice flies, batters faced or league totals are not zero. A zero denominator is unavailable, not a rate of zero.

## Interpretation

Show the formula or named method, sample size, constants source, and any adjustment. Compare like seasons, leagues, units and selection populations. A list of searched players is not a national leaderboard. Distinguish a provider's statistic from a locally computed statistic.

Treat ERA/FIP divergence and unusual BABIP as questions to investigate, not proof of defense, luck, future regression or hidden talent. No calendar week makes every metric reliable; uncertainty depends on events observed, role, opponents and measurement quality. Do not assign universal All-American or elite-command labels from unsupported cutoffs.

## Deliver and verify

Return supported metrics, missing inputs and a restrained scouting interpretation. Explain whether a metric is descriptive or supplied by an explicitly identified forecast model. Never replace a requested unavailable metric with a different one without labeling the substitution and explaining the limitation.

Method references: [FanGraphs pitching definitions](https://library.fangraphs.com/pitching/complete-list-pitching/) and [park/league-adjusted pitching metrics](https://library.fangraphs.com/pitching/era-fip-xfip/). Use the baseball plugin's source-backed tests for executable formula checks; this interpretation skill has no independent predictive calibration.
