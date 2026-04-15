---
name: matchup
description: Analyze a fantasy sports head-to-head matchup with category breakdowns and win probability
argument-hint: <team-a> vs <team-b> [week]
allowed-tools: [Read, Bash, Grep]
---

# Matchup Analysis

Analyzes fantasy sports head-to-head matchups with detailed category breakdowns.

## Arguments

The user invoked this with: $ARGUMENTS

Expected format: `/matchup <team-a> vs <team-b> [week]`

## Instructions

When this command is invoked:

1. Parse the team names and optional week
2. Analyze the matchup across scoring categories
3. Present a comprehensive breakdown

## Output Format

```
🏆 Fantasy Baseball Matchup — Week 12

  Team A  vs  Team B

  Category     Team A    Team B    Edge
  ─────────    ──────    ──────    ────
  AVG          .272      .258      → A
  HR           8         11        → B
  RBI          34        29        → A
  SB           5         3         → A
  K (pitching) 62        58        → A
  ERA          3.42      3.85      → A
  WHIP         1.18      1.25      → A
  W            3         4         → B
  SV           2         3         → B
  ─────────    ──────    ──────    ────
  Projected:   6-3-1     3-6-1

  Win Probability: Team A 68% | Team B 32%

  Key Matchups to Watch:
  • Team A has 3 two-start pitchers this week
  • Team B's OF has favorable park factors (2 games at Coors)
```

## Example Usage

```
/matchup My Team vs Rival
/matchup week 15
```
