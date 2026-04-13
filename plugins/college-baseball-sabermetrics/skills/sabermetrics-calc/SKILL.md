---
name: sabermetrics-calc
description: This skill should be used when the user asks about sabermetric formulas, "what is wOBA", "how to calculate FIP", "explain wRC+", college baseball advanced stats, or wants to compute sabermetric values from raw stats. Provides formulas, explanations, and calculations for all major sabermetric metrics.
version: 1.0.0
---

# Sabermetrics Calculator

Calculates, explains, and applies advanced sabermetric formulas for college baseball analytics.

## When This Skill Applies

This skill activates when the user:
- Asks what a sabermetric stat means (wOBA, FIP, wRC+, BABIP, etc.)
- Wants to calculate a metric from raw stats
- Needs to evaluate a player using advanced metrics
- Compares traditional stats vs. sabermetrics
- Asks about college baseball analytics methodology

## Core Formulas

### wOBA (Weighted On-Base Average)
```
wOBA = (0.69×uBB + 0.72×HBP + 0.89×1B + 1.27×2B + 1.62×3B + 2.10×HR) / (AB + BB - IBB + SF + HBP)
```
- League average: ~.320
- Excellent: >.400
- NCAA weights may vary slightly from MLB — adjust for college run environment

### FIP (Fielding Independent Pitching)
```
FIP = ((13×HR) + (3×(BB+HBP)) - (2×K)) / IP + FIP_constant
```
- FIP constant ≈ 3.10 (adjusts to league ERA each season)
- College FIP constant recalculated per season for NCAA environment

### wRC+ (Weighted Runs Created Plus)
```
wRC+ = (((wRAA/PA + league_runs_per_PA) + (league_runs_per_PA - park_factor × league_runs_per_PA)) / (league_wRC/PA)) × 100
```
- 100 = league average
- 150+ = elite
- College: park factors vary significantly — use with context

### BABIP (Batting Average on Balls in Play)
```
BABIP = (H - HR) / (AB - K - HR + SF)
```
- League average: ~.300
- Significant deviation may indicate luck, defense quality, or batted-ball skill

### ISO (Isolated Power)
```
ISO = SLG - AVG
```
- Or equivalently: (2B + 2×3B + 3×HR) / AB

### Barrel Rate
```
Barrel% = Barrels / Batted Ball Events × 100
```
- A barrel: exit velocity ≥ 98 mph and optimal launch angle (26-30° at 98 mph, wider range at higher velo)

### CSW% (Called Strike + Whiff %)
```
CSW% = (Called Strikes + Whiffs) / Total Pitches × 100
```
- Average: ~28-29%
- Elite: >32%

## Instructions

When this skill is invoked:

1. Identify which metric(s) the user is asking about
2. Provide the formula with clear variable definitions
3. If raw stats are given, compute the result
4. Contextualize the result (what's good, average, elite in college baseball)
5. Note any college-specific adjustments vs. MLB formulas

## College Baseball Context

- College baseball uses aluminum bats (BBCOR since 2011) — higher BABIP and offensive levels than MLB
- Smaller sample sizes per season (~56 games vs. 162) — more variance in rate stats
- Park factors vary wildly between programs
- Pitcher workload limits differ from pro ball
- wOBA weights should be recalibrated for the college run environment
