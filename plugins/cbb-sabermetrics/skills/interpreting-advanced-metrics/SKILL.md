---
name: interpreting-advanced-metrics
description: >
  Interpret advanced college baseball metrics (wOBA, wRC+, FIP, ERA-, BABIP, ISO,
  K%, BB%) correctly in context. Use when explaining a player's or team's
  advanced stats, when comparing programs, when translating raw numbers into
  analytical conclusions, or when converting a leaderboard into a scouting
  takeaway. Pairs with bsi_get_team_sabermetrics, bsi_get_player_stats, and
  bsi_get_leaderboard from the cbb-sabermetrics plugin.
---

# Interpreting Advanced College Baseball Metrics

When raw sabermetric numbers come back from the BSI MCP, they need framing before they mean anything. This skill turns numbers into reads.

## The Core Metrics

### wOBA (weighted On-Base Average)
- Combines all offensive events (walks, singles, doubles, triples, HR, HBP) with linear weights derived from run expectancy.
- **Scale:** .290 is roughly league average DI, .350+ is strong, .400+ is elite.
- **Why it matters:** OBP treats every time on base as equal; wOBA weights doubles and home runs higher. A player with .380 OBP driven by walks has a different profile than one with .380 OBP driven by extra-base hits. wOBA differentiates.
- **Use when:** comparing offensive players, building order projections, evaluating recruiting targets.

### wRC+ (weighted Runs Created Plus)
- Park-adjusted, league-adjusted measure of total offensive contribution. 100 is exactly average; 150 means 50% better than average; 70 means 30% below.
- **Scale:** 100 = average, 120+ = strong regular, 150+ = conference all-star, 180+ = all-American.
- **Why it matters:** wOBA doesn't account for park effects (UFCU Disch-Falk plays differently than Alex Box). wRC+ normalizes that. One number, fully contextualized, directly comparable across programs.
- **Use when:** the *only* single number you want for overall offensive value. Lead with this in scouting reports.

### FIP (Fielding Independent Pitching)
- ERA-scaled metric built only from strikeouts, walks, and home runs allowed — the three outcomes a pitcher controls without defensive help.
- **Scale:** matches ERA scale. 4.00 = DI average-ish, 3.50 = strong, 3.00 = elite.
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
- **Scale:** .130 = average, .200+ = elite DI power.
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

The BSI MCP returns park-adjusted versions (wRC+, ERA−, FIP−) when available. Prefer these over raw wOBA / ERA / FIP for cross-program comparison.

Why: UFCU Disch-Falk is a pitcher-friendly park. Alex Box (LSU) plays neutral. Goss Stadium (Oregon State) is pitcher-friendly with marine layer. A .400 wOBA at Disch-Falk is more impressive than .400 at a hitter's park.

## Translating Numbers Into Reads

### Hitter Read Template
> "[Name] posts a .XXX wOBA / XXX wRC+ in [PA] plate appearances across [games] — a [above/below/around] league-average profile. Breakdown: .XXX BABIP (stable/high/low relative to his career), .XXX ISO ([slap hitter / gap power / true slugger] profile), XX% BB rate ([approach-driven / aggressive] bat), XX% K rate ([contact / swing-and-miss] tendency). [Park adjustment note]. [Season-state caveat if Feb/Mar]."

### Pitcher Read Template
> "[Name] runs a X.XX FIP (X.XX ERA) in [IP] innings through [date]. XX% K rate (elite / strong / needs work), XX% BB rate (command / erratic). [Gap between ERA and FIP explains defense/luck contribution]. Park-adjusted ERA− of XX means [X]% better/worse than league-average SOS-adjusted. [Arm-count context for May stretch run if applicable]."

### Team Read Template
> "[Team] carries a [XXX] offensive wRC+ (rank X-of-XXX in conference / national) and a [XXX] team ERA− (pitching rank). Run differential of [+/- XX] through [X] games suggests [sustainable / lucky / unlucky] record. Notable strength: [specific metric leader]. Vulnerability: [specific weakness]. SOS-adjusted conference strength index ranks [X]-of-32."

## Quality Gates

- Every number cited gets a source and timestamp from the MCP response `meta` envelope.
- Never present a raw wOBA without park context.
- Never present ERA without FIP (they tell different stories).
- When BABIP is extreme, flag regression expectation explicitly.
- When season state is early, name the phase and what metrics are still noise.

## Example Invocations

A user asks: "How's Texas's offense?"
1. Call `bsi_get_team_sabermetrics team=texas`
2. Apply Team Read Template above
3. Context: SEC-adjusted, UFCU Disch-Falk park context, current season phase
4. Return a 3-sentence read with source + timestamp

A user asks: "Who are the top DI hitters right now?"
1. Call `bsi_get_leaderboard metric=wrc_plus type=batting limit=10`
2. Present ranked list with park-adjusted context
3. Flag any early-season caveats
4. Return top 10 with wOBA, wRC+, ISO, BB%, K% for each
