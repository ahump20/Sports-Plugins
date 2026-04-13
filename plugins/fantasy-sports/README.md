# Fantasy Sports Plugin

AI-powered fantasy sports assistant for roster decisions, matchup analysis, and trade evaluation.

## Features

- **Roster optimization** — Start/sit recommendations based on matchups, trends, and projections
- **Matchup analysis** — Head-to-head matchup breakdowns with win probability estimates
- **Trade evaluator** — Analyze trade fairness using rest-of-season projections
- **Waiver wire** — Surface high-upside adds based on recent performance and usage trends

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `roster-optimizer` | Model-invoked | Provides start/sit and lineup optimization advice |
| `matchup` | User-invoked | `/matchup` command for head-to-head analysis |

## Supported Formats

- **Fantasy Baseball** — Rotisserie, H2H Categories, H2H Points
- **Fantasy Football** — PPR, Half-PPR, Standard
- **Fantasy Basketball** — 9-Category, Points

## Installation

```
/plugin install fantasy-sports@Sports-Plugins
```

## Usage

The roster optimizer activates automatically when you discuss fantasy lineups, start/sit decisions, or player values.

```
/matchup Team A vs Team B
/matchup week 12
```

## Methodology

Recommendations are based on:
- Recent performance trends (last 14/30 days)
- Matchup quality (opposing pitcher/defense strength)
- Platoon splits and handedness advantages
- Park factors and venue effects
- Injury reports and lineup status
- Usage and snap/pitch count trends
