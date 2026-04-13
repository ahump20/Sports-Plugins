# College Baseball Sabermetrics Plugin

Advanced sabermetrics and analytics for NCAA Division I college baseball. Built on the same analytical foundations that power [Blaze Sports Intel](https://blazesportsintel.com).

## Features

- **Sabermetric calculations** — wOBA, FIP, wRC+, K%, BB%, BABIP, barrel rate, and more
- **Player lookup** — Search and retrieve advanced stats for any D1 college baseball player
- **Team rankings** — Conference standings with advanced metrics, RPI, and strength of schedule
- **Pitch-level analytics** — Pitch mix breakdowns, whiff rates, zone charts
- **Texas Longhorns intel** — Deep coverage of UT Austin baseball with historical context

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `sabermetrics-calc` | Model-invoked | Calculates or explains sabermetric formulas and metrics |
| `player-lookup` | Model-invoked | Retrieves advanced stats for a specific college baseball player |
| `team-rankings` | User-invoked | `/rankings` command for conference and national rankings |

## Key Metrics

### Hitting
| Metric | Description |
|--------|-------------|
| **wOBA** | Weighted On-Base Average — values each method of reaching base by actual run value |
| **wRC+** | Weighted Runs Created Plus — league-adjusted overall offensive value (100 = average) |
| **BABIP** | Batting Average on Balls in Play — measures batted-ball luck vs. skill |
| **ISO** | Isolated Power — raw power metric (SLG minus AVG) |
| **BB%** | Walk rate |
| **K%** | Strikeout rate |
| **Barrel%** | Percentage of batted balls with optimal exit velocity and launch angle |

### Pitching
| Metric | Description |
|--------|-------------|
| **FIP** | Fielding Independent Pitching — ERA estimator based on strikeouts, walks, and home runs |
| **xFIP** | Expected FIP — normalizes home run rate to league average |
| **WHIP** | Walks + Hits per Inning Pitched |
| **K/9** | Strikeouts per nine innings |
| **Whiff%** | Swing-and-miss rate on all swings |
| **CSW%** | Called strikes + whiffs as percentage of total pitches |

## Installation

```
/plugin install college-baseball-sabermetrics@Sports-Plugins
```

## Usage

The sabermetrics skills activate automatically when you discuss college baseball stats, analytics, or player evaluation.

```
# Slash command for rankings
/rankings big-12
/rankings national top-25
/rankings sec pitching
```

## MCP Integration

This plugin connects to the Blaze Sports Intel MCP endpoint at `https://blazesportsintel.com/mcp` for real-time college baseball data. For Codex or other MCP-compatible assistants, the `.mcp.json` configuration provides direct tool-use access.

## Data Sources

- NCAA official statistics
- Blaze Sports Intel (BSI) analytics engine
- Public box score data
