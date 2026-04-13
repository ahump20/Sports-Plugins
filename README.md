# Sports-Plugins

A curated marketplace of high-quality sports plugins for **Claude Code**, **OpenAI Codex**, and AI coding assistants. Covers college baseball sabermetrics, live scores, sports analytics, and fantasy sports — built on the foundational plugin structures from [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) and [OpenAI Codex use cases](https://developers.openai.com/codex/use-cases).

Core data foundation: [Blaze Sports Intel (BSI)](https://blazesportsintel.com) — with primary depth on college baseball, Texas Longhorns, and the Big 12.

---

## Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [`college-baseball-sabermetrics`](./plugins/college-baseball-sabermetrics) | Sports Analytics | Deep sabermetrics for NCAA — pitcher FIP/xFIP, lineup optimizer, game data pipelines. Primary depth: Texas Longhorns + Big 12. |
| [`sports-analytics`](./plugins/sports-analytics) | Sports Analytics | Multi-sport data pipelines, Recharts stat visualizations, and predictive modeling across MLB, NFL, NBA, CFB, and college baseball. |
| [`live-scores`](./plugins/live-scores) | Sports Data | Real-time scoreboard components and Cloudflare Worker polling patterns for live game scores. |
| [`fantasy-sports`](./plugins/fantasy-sports) | Fantasy | AI-assisted draft strategy, trade analysis, and waiver wire recommendations for NFL, MLB, and NBA fantasy. |

---

## Plugin Structure

Each plugin follows the Claude Code plugin format, with Codex environment compatibility:

```
plugins/<plugin-name>/
  .claude-plugin/
    plugin.json          ← Claude Code plugin manifest
  .mcp.json              ← MCP server connections for this plugin
  README.md              ← Plugin overview and representative prompts
  skills/
    <skill-name>/
      SKILL.md           ← Skill instructions loaded by Claude Code
```

Top-level marketplace:

```
.claude-plugin/
  marketplace.json       ← Marketplace manifest listing all plugins
.codex/
  environments/
    environment.toml     ← OpenAI Codex environment config
```

---

## MCP Servers

The college baseball sabermetrics and sports analytics plugins connect to:

| Server | URL | Purpose |
|--------|-----|---------|
| BSI | `https://blazesportsintel.com/mcp` | Live college baseball scores, standings, box scores, and player stats |

Use `/mcp` in Claude Code after enabling a plugin to confirm server connections.

---

## College Baseball Coverage

The flagship plugin is **college-baseball-sabermetrics**, built to fill the ESPN coverage gap for NCAA baseball:

### Skills

| Skill | Purpose |
|-------|---------|
| `sabermetrics-analysis` | ERA, FIP, xFIP, wOBA, wRC+, BABIP, ISO — with NCAA baselines and Texas-specific context |
| `pitcher-analytics` | Pitch-mix, sequencing, platoon splits, role recommendations, and series preview cards |
| `lineup-optimizer` | Batting order construction, wOBA-based slot assignment, platoon adjustments |
| `game-data-pipeline` | NCAA box score ingestion, IP normalization, player ID cross-reference, Cloudflare D1/KV/R2 storage |

### Representative Prompts

```
Evaluate the Texas Longhorns rotation using FIP and xFIP through the first 8 weeks of the season.

Build a weekend series preview for UT vs. Oklahoma State with pitcher matchups and lineup tendencies.

Rank the Big 12 bullpens by inherited-runner strand rate and K/9.

Optimize the Longhorns batting order using wOBA and contact rate splits against left-handed starters.

Ingest this NCAA box score JSON and compute game-level FIP and wRC+ for both teams.
```

---

## Using a Plugin in Claude Code

1. Open Claude Code in this repository.
2. Run `/plugins` to view available plugins.
3. Enable a plugin (e.g. `college-baseball-sabermetrics`).
4. Run `/mcp` to confirm MCP server connections.
5. Use the representative prompts from the plugin README to get started.

---

## Using with OpenAI Codex

The `.codex/environments/environment.toml` file configures the Codex sandbox environment for this repo. Skills in each plugin are written as plain Markdown instruction files — compatible with Codex's context injection model.

---

## Contributing

1. Fork this repo.
2. Create a new plugin directory under `plugins/`.
3. Add `.claude-plugin/plugin.json`, `README.md`, and at least one `skills/<name>/SKILL.md`.
4. Add your plugin entry to `.claude-plugin/marketplace.json`.
5. Open a pull request.

Plugin quality bar: skills must contain specific, actionable guidance — not generic descriptions. See the `college-baseball-sabermetrics` skills for the content standard.

---

## License

All rights reserved. Proprietary content from Blaze Sports Intel.
