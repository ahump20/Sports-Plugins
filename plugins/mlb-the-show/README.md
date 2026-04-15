# MLB The Show Plugin

Diamond Dynasty card analytics for MLB The Show — card valuations, market trends, squad building, and investment intelligence.

## Features

- **Card valuations** — Real-time card prices, quicksell values, and market trends
- **Squad builder** — Optimize your Diamond Dynasty lineup with budget constraints
- **Investment picks** — Identify undervalued cards likely to get attribute upgrades
- **Program tracking** — Track XP, collections, and program completions

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `card-valuations` | Model-invoked | Card pricing, market trends, and value analysis |
| `squad` | User-invoked | `/squad` command for team building recommendations |

## Card Tiers

| Tier | OVR | Color |
|------|-----|-------|
| Diamond | 85+ | 💎 |
| Gold | 80-84 | 🥇 |
| Silver | 75-79 | 🥈 |
| Bronze | 65-74 | 🥉 |
| Common | <65 | ⚪ |

## Installation

```
/plugin install mlb-the-show@Sports-Plugins
```

## Usage

Card valuation skills activate automatically when discussing MLB The Show, Diamond Dynasty, or card values.

```
/squad 100k budget
/squad best-available SP
```

## Alignment with BSI

This plugin complements the BSI platform's `mlb-the-show` module, which tracks card data and market analytics. The real-world sabermetric data from the college-baseball-sabermetrics plugin can inform investment decisions — players performing well in real life are more likely to receive attribute upgrades in-game.

## Data Sources

- MLB The Show marketplace API
- Community price tracking databases
- BSI real-world performance correlation engine
