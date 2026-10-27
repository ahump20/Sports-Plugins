# Scoring values and stat conventions

Playing-rule values come from the 2026 NFL and NCAA rulebooks. The stat conventions (sacks, kneels, spikes) are statisticians' rules, not playing rules. Each item below names its source; the NCAA and NFL stat manuals themselves weren't reachable for this skill, so treat the conventions as secondary-sourced.

## Contents
- Scoring values
- NFL passer rating
- NCAA passing efficiency
- Sacks, kneels and spikes
- Reading traps

## Scoring values

| Score | NFL | NCAA (8-1-1) |
|---|---|---|
| Touchdown | 6 | 6 |
| Field goal (including a fair catch kick) | 3 | 3 |
| Safety | 2 to the opponent | 2 to the opponent |
| Try: kick | 1 (snapped from the 15; 11-3-1) | 1 (snapped from the 3; 8-3-2-c) |
| Try: run or pass into the end zone | 2 (snapped from the 2) | 2 |
| Try: defense returns the ball for a score | 2 (11-3-2-b) | 2 (a touchdown on a try is 2 for either team) |
| Try: safety | Check 11-3-2 (unverified here) | 1 point (8-1-1) |
| Try at the end of the game | Not played after a winning touchdown at the end of regulation (since 2018) or a touchdown that ends overtime | Not played unless it could affect the outcome (8-3-2-a) |

Overtime scoring is different in NCAA from the second overtime on. See `clock-and-overtime.md`.

**One-point safeties.** In NCAA a safety during a try is worth 1 point (8-1-1). It is rare, but it is the only way a team can score exactly 1 point on a play without kicking. The NCAA forfeit score is recorded as 1–0 for the offended team, unless it was already ahead (8-1-2).

## NFL passer rating

Adopted in 1973 (Pro Football Hall of Fame). Four components from attempts (Att), completions (Cmp), passing yards (Yds), touchdown passes (TD) and interceptions (Int). Each component is **clamped to the range 0 to 2.375**.

```
a = (Cmp/Att − 0.3) × 5
b = (Yds/Att − 3) × 0.25
c = (TD/Att) × 20
d = 2.375 − (Int/Att × 25)
rating = (a + b + c + d) / 6 × 100
```

- Range 0 to 158.3. A "perfect" 158.3 needs every component at its cap: at least a 77.5% completion rate, 12.5 yards per attempt and an 11.875% TD rate, with no interceptions.
- Sacks, sack yards, rushing and fumbles are not in it.
- **Check example** (a hypothetical stat line): 20 of 30, 250 yards, 2 TD, 1 INT.
  - a = 1.8333, b = 1.3333, c = 1.3333, d = 1.5417.
  - Sum 6.0417, so the rating is **100.7**.
- Always apply the clamps before summing. Leaving them out is the most common error in hand calculations.

## NCAA passing efficiency

```
efficiency = (8.4 × Yds + 330 × TD + 100 × Cmp − 200 × Int) / Att
```

- No caps (sports-reference.com glossary). The theoretical range is −731.6 to 1261.6 (Wikipedia, "Passer rating").
- **Check example**, same line: (2100 + 660 + 2000 − 200) / 30 = **152.0**.
- NCAA statistical leaderboards set a minimum number of attempts per game for qualifying. Check the current NCAA stats manual for the threshold.
- **Never convert between the two.** A 150 college efficiency and a 150 NFL rating mean very different things, and the formulas aren't linear transforms of each other.
- ESPN's Total QBR is a third, proprietary metric on a 0–100 scale. Don't confuse it with either formula, and don't try to compute it.

## Sacks, kneels and spikes

| | NFL | NCAA |
|---|---|---|
| Sack | Charged to **team passing**: team net passing yards = gross passing − sack yards. The quarterback's individual passing line is unchanged, and the sack is **not** a rushing attempt. Individual defensive sacks have been official since 1982 | Charged as a **rushing attempt** for negative yards, for the quarterback and the team. Team passing yards are gross |
| Kneel-down | Rushing attempt for a loss (typically −1 or −2) (unverified — check the stat manual) | Same (unverified) |
| Spike to stop the clock | Incomplete pass attempt (unverified) | Same (unverified) |

Sources: Wikipedia, "Quarterback sack" and "Carry (gridiron football)". The official stat manuals weren't retrieved.

**Consequences for reading stats:**
- A college quarterback's season rushing total is net of every sack. A mobile quarterback who is sacked often can show modest or negative rushing yards despite big gains on designed runs. To compare with an NFL quarterback, add sack yards back to the college rushing total, or subtract them from the NFL team's passing.
- College team rushing totals are lower, and team passing totals higher, than the same plays would produce under NFL conventions.
- NFL team "net passing yards" in a box score won't equal the sum of the quarterbacks' passing yards; the difference is sack yards.
- Kneel-downs pull down the quarterback's and team's yards per carry, especially for a team protecting late leads.
- Play-by-play feeds don't always follow the official convention: a sack may be labeled as a pass play even in college data. Check how a data source codes sacks before computing rushing or passing rates from raw plays.

## Reading traps

- **Two-point attempts** generally don't count toward a player's season rushing or passing totals (unverified — check the stat manual). The extra points scored count only in the score.
- **Defensive two-point returns** on tries (2 points, both codes) explain odd final scores, such as a team scoring 2 points with no safety.
- **College overtime** inflates team point totals with possessions from the 25 and two-point plays. Many analysts separate regulation scoring from overtime.
- **Rule eras matter** for kicking stats:
  - The NFL moved the try kick to the 15 in 2015, so earlier extra-point percentages aren't comparable.
  - The NFL's dynamic kickoff (2024+) changed return and touchback rates.
  - NCAA's fair catch rule on free kicks, placing the ball at the 25 (2018+), changed kick-return rates.
