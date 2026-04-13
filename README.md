<div align="center">

# 🏟️ Sports-Plugins

**Curated sports plugins for Claude Code, OpenAI Codex, and AI coding assistants.**

[![CI](https://github.com/ahump20/Sports-Plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/ahump20/Sports-Plugins/actions/workflows/ci.yml)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue?logo=typescript&logoColor=white)
![Plugins](https://img.shields.io/badge/plugins-4-orange)
![Skills](https://img.shields.io/badge/skills-12-green)
![Tests](https://img.shields.io/badge/tests-103%20passing-brightgreen)

College baseball sabermetrics · Live scores · Sports analytics · Fantasy sports

Built on the foundational structures from [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) and [OpenAI Codex use cases](https://developers.openai.com/codex/use-cases).

Core data foundation: **[Blaze Sports Intel](https://blazesportsintel.com)** — with primary depth on college baseball, Texas Longhorns, and the Big 12.

</div>

---

## Plugins

| Plugin | Skills | Category | Description |
|--------|:------:|----------|-------------|
| [`college-baseball-sabermetrics`](./plugins/college-baseball-sabermetrics) | 4 | Sports Analytics | Deep sabermetrics for NCAA — FIP/xFIP, wOBA, wRC+, lineup optimizer, game data pipelines. Primary depth: **Texas Longhorns** + Big 12. |
| [`sports-analytics`](./plugins/sports-analytics) | 3 | Sports Analytics | Multi-sport data pipelines, Recharts stat visualizations, and predictive modeling (Marcel projections, win probability). |
| [`live-scores`](./plugins/live-scores) | 2 | Sports Data | Real-time scoreboard components, Cloudflare Worker polling, KV cache, and live-update UI patterns. |
| [`fantasy-sports`](./plugins/fantasy-sports) | 3 | Fantasy | AI-assisted draft strategy, trade analysis, and waiver wire recommendations for NFL, MLB, and NBA. |

---

## Quick Start

```bash
git clone https://github.com/ahump20/Sports-Plugins.git
cd Sports-Plugins
npm install
npm run check   # typecheck + lint + test + validate
```

### Use in Claude Code

1. Open Claude Code in this repository.
2. Run `/plugins` → enable a plugin (e.g. `college-baseball-sabermetrics`).
3. Run `/mcp` to confirm MCP server connections.
4. Use the representative prompts from the plugin README.

### Use with OpenAI Codex

The `.codex/environments/environment.toml` configures the Codex sandbox. Skills are plain Markdown — compatible with Codex's context injection model.

---

## Architecture

```
Sports-Plugins/
├── .claude-plugin/
│   └── marketplace.json           ← Marketplace manifest (all plugins)
├── .codex/
│   └── environments/
│       └── environment.toml       ← OpenAI Codex environment config
├── .github/
│   ├── workflows/ci.yml           ← CI: typecheck, lint, test, validate
│   └── PULL_REQUEST_TEMPLATE.md
├── src/                           ← Shared library
│   ├── types/index.ts             ← Canonical data types (Sport, GameBoxScore, etc.)
│   └── utils/
│       ├── sabermetrics.ts        ← ERA, FIP, xFIP, wOBA, wRC+, BABIP, ISO, ...
│       └── normalization.ts       ← IP normalization, team names, data defaults
├── plugins/
│   ├── college-baseball-sabermetrics/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .mcp.json
│   │   ├── README.md
│   │   ├── skills/                ← 4 SKILL.md files
│   │   └── src/                   ← metrics, pitcher-eval, lineup, ingest
│   ├── sports-analytics/
│   │   ├── src/                   ← provider client, models, format helpers
│   │   └── skills/                ← 3 SKILL.md files
│   ├── live-scores/
│   │   ├── src/                   ← game-card state, cache, display helpers
│   │   └── skills/                ← 2 SKILL.md files
│   └── fantasy-sports/
│       ├── src/                   ← trade analyzer, waiver ranker, draft planner
│       └── skills/                ← 3 SKILL.md files
├── scripts/
│   └── validate-plugins.js        ← Plugin structure validator
├── package.json
├── tsconfig.json
├── vitest.config.ts
└── eslint.config.mjs
```

### Plugin Structure

Every plugin follows the same layout:

```
plugins/<plugin-name>/
  .claude-plugin/
    plugin.json          ← Claude Code plugin manifest
  .mcp.json              ← MCP server connections (optional)
  README.md              ← Overview, coverage, representative prompts
  skills/
    <skill-name>/
      SKILL.md           ← Skill instructions loaded by Claude Code
  src/
    index.ts             ← TypeScript entry point and exports
    *.ts                 ← Implementation modules
    *.test.ts            ← Tests
```

---

## MCP Servers

Plugins that connect to live data use the BSI MCP endpoint:

| Server | URL | Purpose |
|--------|-----|---------|
| BSI | `https://blazesportsintel.com/mcp` | Live college baseball scores, standings, box scores, and player stats |

Run `/mcp` in Claude Code after enabling a plugin to confirm the connection.

---

## College Baseball Coverage

The flagship plugin — **college-baseball-sabermetrics** — fills the ESPN coverage gap for NCAA baseball:

| Skill | What It Does |
|-------|-------------|
| `sabermetrics-analysis` | ERA, FIP, xFIP, wOBA, wRC+, BABIP, ISO — with NCAA baselines and Texas-specific context |
| `pitcher-analytics` | Pitch-mix analysis, sequencing, platoon splits, role recommendations, series preview cards |
| `lineup-optimizer` | wOBA-based batting order construction, slot philosophy, platoon adjustments |
| `game-data-pipeline` | NCAA box score ingestion, IP normalization, player ID cross-reference, storage patterns |

### Source Code Highlights

```typescript
import { computeBatterMetrics, computePitcherMetrics } from './plugins/college-baseball-sabermetrics/src/metrics.js';
import { evaluatePitcher } from './plugins/college-baseball-sabermetrics/src/pitcher-eval.js';
import { optimizeLineup } from './plugins/college-baseball-sabermetrics/src/lineup.js';
import { ingestBoxScore } from './plugins/college-baseball-sabermetrics/src/ingest.js';
```

### Example Prompts

```
Evaluate the Texas Longhorns rotation using FIP and xFIP through the first 8 weeks.

Build a weekend series preview for UT vs. Oklahoma State with pitcher matchups.

Rank the Big 12 bullpens by inherited-runner strand rate and K/9.

Optimize the Longhorns batting order using wOBA splits against left-handed starters.

Ingest this NCAA box score JSON and compute game-level FIP and wRC+ for both teams.
```

---

## Development

| Command | Description |
|---------|-------------|
| `npm run typecheck` | TypeScript type checking (strict mode) |
| `npm run lint` | ESLint with TypeScript rules |
| `npm test` | Run all tests with Vitest |
| `npm run validate` | Validate plugin manifest structure |
| `npm run check` | All of the above in sequence |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for full guidelines. The short version:

1. Fork → create a plugin directory under `plugins/`.
2. Add `plugin.json`, `README.md`, at least one `SKILL.md`, and TypeScript source.
3. Register in `.claude-plugin/marketplace.json`.
4. Run `npm run check` → open a PR.

**Quality bar:** Skills must contain specific, actionable guidance — not generic descriptions. See the `college-baseball-sabermetrics` skills for the standard.

---

## License

All rights reserved. Proprietary content from [Blaze Sports Intel](https://blazesportsintel.com). See [LICENSE](./LICENSE).
