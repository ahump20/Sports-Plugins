# College Football Intel Plugin

College football intelligence for AI coding assistants — transfer portal tracking, recruiting rankings, conference standings, and Big 12 analytics.

## Features

- **Transfer portal tracking** — Real-time portal entries, commitments, and impact ratings
- **Recruiting rankings** — Class rankings, top prospects, and commitment tracking
- **Conference standings** — Big 12, SEC, ACC, Big Ten with advanced metrics (SP+, FPI, SOS)
- **Game previews & recaps** — Matchup analysis with win probability and key stat edges

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `transfer-portal` | Model-invoked | Track transfer portal activity, impact transfers, and team needs |
| `cfb-rankings` | User-invoked | `/cfb-rankings` command for AP, CFP, and conference standings |
| `recruiting` | Model-invoked | Recruiting class rankings, top prospects, and commitment intel |

## Supported Conferences

- **Big 12** — Primary focus (aligned with Texas Longhorns coverage in BSI)
- **SEC** — Full coverage
- **Big Ten** — Full coverage
- **ACC** — Full coverage
- **Pac-12** — Coverage (ongoing realignment tracked)
- **Group of 5** — AAC, Sun Belt, MW, MAC, C-USA

## Installation

```
/plugin install college-football-intel@Sports-Plugins
```

## Usage

Skills activate automatically when discussing college football topics.

```
/cfb-rankings big-12
/cfb-rankings ap-top-25
/cfb-rankings sec sp+
```

## Data Sources

- Public APIs for scores and schedules
- Blaze Sports Intel for Big 12 analytics and Texas Longhorns deep coverage
