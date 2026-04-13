---
name: pitcher-analytics
description: Use when the task involves evaluating a college baseball pitcher or pitching staff — including pitch-mix analysis, sequencing strategy, matchup scouting, platoon splits, and role recommendations (starter vs. reliever vs. closer).
---

# Pitcher Analytics

Use this skill when the task requires a thorough pitching evaluation beyond ERA. The goal is to give coaches, analysts, and content teams a precise and actionable read on how a pitcher is performing, why, and what adjustments to expect or recommend.

## Working Model

Before evaluating any pitcher, establish:

- **Role**: Weekend starter, midweek starter, multi-inning reliever, closer, or high-leverage bridge arm?
- **Arsenal**: What pitches does he throw? What are the usage rates? Does he have a true out pitch?
- **Sample**: How many innings? How many appearances? Weekend or midweek context?
- **Opponent quality**: DI average, conference slate, or top-25 heavy schedule?

Role and sample matter as much as the metrics themselves. A 12-start weekend arm and a 20-inning reliever require different analytical frames.

## Pitch-Mix Analysis

When pitch data is available (Trackman, Hawkeye, Yakkertech, or manually scouted):

### Pitch Classification

- **Fastball family**: Four-seam, two-seam/sinker, cutter
- **Breaking ball family**: Curveball (12-6, slurve), slider (hard, gyro)
- **Offspeed family**: Changeup, splitter, circle change
- **Specialty**: Screwball, knuckleball (flag these — rare at college level)

### Usage Rate Guidance

A healthy starter arsenal typically looks like:

| Pitch Type | Typical Usage Range |
|------------|-------------------|
| Primary fastball | 40–60% |
| Secondary fastball or cutter | 0–20% |
| Primary breaking ball | 15–30% |
| Offspeed (change/splitter) | 10–25% |

A pitcher over-relying on one pitch (>70% usage) is either elite with that pitch or limiting himself — determine which from outcome data.

### Pitch Value Metrics (when available)

- **Whiff%** per pitch: Swings and misses / total swings on that pitch type
- **Put-away%**: K rate when pitcher is ahead in count (0-2, 1-2)
- **Chase%**: O-Swing% — swings on pitches outside the zone
- **Zone%**: Percentage of pitches in the strike zone

Elite put-away pitch: > 35% whiff rate on the pitch in two-strike counts.

## Sequencing Principles

Even without pitch-tracking data, sequencing can be evaluated from game logs and observation:

1. **Fastball command first**: A pitcher who cannot locate the fastball to both sides of the plate has no sequence — everything telegraphs.
2. **Secondary in early counts**: Elite pitchers use breaking balls in 1-0 and 2-0 counts to steal called strikes; average pitchers default to fastballs.
3. **Change the eye level**: Pairing a high four-seam with a low changeup or curve creates the most cognitive dissonance for hitters.
4. **Left/right splits**: Evaluate breaking ball and changeup effectiveness separately vs. LHH and RHH.

When sequence data is limited: read the BABIP vs. FIP gap. A large positive gap (ERA >> FIP) suggests batted-ball variance is punishing an otherwise solid sequence plan. A large negative gap (ERA << FIP) may indicate sequencing masking mediocre stuff.

## Role Recommendations

Use these thresholds to recommend starter vs. reliever roles:

| Metric | Starter Profile | Reliever Profile |
|--------|----------------|-----------------|
| IP/start | 5.0+ | N/A |
| Pitches/start | 80+ | < 50 (multi-inning) |
| Arsenal depth | 3+ pitches | 2 pitches acceptable |
| BB/9 tolerance | < 3.5 | < 4.5 |
| Velocity (avg FB) | 89+ mph | 90+ preferred |
| Platoon split | Manageable | Can be hidden |

A two-pitch pitcher with elite stuff but a 4.5 BB/9 is likely a high-leverage late-inning arm, not a Friday starter.

## Bullpen Evaluation Framework

For evaluating a pitching staff as a unit:

1. **Inherited runner strand rate (LOB%)**: Above 72% = good bullpen management. Below 65% = issues.
2. **Opener usage**: Note when a program uses openers to match up with dangerous top-of-order left-handed hitters.
3. **Closer profile**: Should have at least one elite secondary pitch (whiff > 30%), K/9 > 10, BB/9 < 3.
4. **Depth count**: How many arms can give a clean inning? Flag if the program is 2-3 deep vs. 5-6 deep.

## Platoon Splits

Standard splits to report:

| Split | Metric | Threshold to flag |
|-------|--------|------------------|
| vs. LHH | wOBA allowed | > .360 is vulnerability |
| vs. RHH | wOBA allowed | > .360 is vulnerability |
| RISP | BA allowed | > .280 is a clutch concern |
| 2-out | OBP allowed | > .380 is a sequencing concern |

## Weekend Series Pitcher Preview Format

When generating a series pitcher preview:

1. **Starter name, class, role** (e.g., "RHP, Jr., Friday starter")
2. **Season line**: ERA / FIP / IP / K/9 / BB/9 / WHIP
3. **Arsenal summary**: Top 2–3 pitches, usage, and best pitch
4. **Key tendency**: One sentence on what he does well and what hitters can exploit
5. **Matchup note**: How does his profile match against this specific opponent's lineup tendencies?

Keep each pitcher card to 6–8 lines. Do not pad with generic commentary.

## Hard Rules

- Never lead with ERA alone — always pair with FIP or WHIP.
- Never recommend a role change without citing at least two supporting metrics.
- Never present pitch-mix analysis without sample size in appearances or batters faced.
- Always flag when data is manually scouted (subjective) vs. tracked (objective).
- Do not compare a college pitcher's raw numbers to MLB benchmarks without adjusting the frame.
- When evaluating a Texas pitcher: note Disch-Falk Field's hitter-friendly environment in the ERA read.
