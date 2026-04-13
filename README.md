# Sports-Plugins

A curated marketplace of sports intelligence plugins for **Claude Code**, **OpenAI Codex**, and other AI coding assistants. Every plugin ships with both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` — one folder, both platforms.

Built on top of the live **Blaze Sports Intel** data engine at [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp) — real 330-team NCAA DI college baseball coverage, sabermetrics, standings, matchup detail.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install cbb-sabermetrics
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install cbb-sabermetrics
```

## Available Now

| Plugin | What it does |
|---|---|
| [`cbb-sabermetrics`](./plugins/cbb-sabermetrics/) | Live college baseball sabermetrics — 10 tools covering scores, standings, rankings, team + player advanced stats, leaderboards, conference power index, matchup detail. Wraps the live BSI MCP. Free tier, 30 req/min, no API key. |
| [`texas-longhorns-intel`](./plugins/texas-longhorns-intel/) | Texas Longhorns baseball intelligence — program doctrine + live MCP data. Scouting reports, SEC matchup previews, roster evaluation, NIL efficiency. Depends on `cbb-sabermetrics`. |
| [`gameday-ops`](./plugins/gameday-ops/) | Live game coverage desk — real-time monitoring, leverage tracking, 30-minute post-game recaps. Imports the production `bsi-gameday-ops` skill with 6 reference workflows and 4 output templates. |
| [`editorial-desk`](./plugins/editorial-desk/) | Editorial voice + anti-fabrication discipline for sports journalism. Three skills — BSI voice guide, anti-fabrication protocol, and source-validated research workflow — plus commands for brief + long-form draft generation. |
| [`site-ops`](./plugins/site-ops/) | Heritage v2.1 visual compliance, Chrome-devtools in-session screenshots after UI edits, and skill-package curation. Bundles `visual-audit` skill plus `build-verify` and `skill-package-curator` agents. |
| [`champion-enigma-engine`](./plugins/champion-enigma-engine/) | Biometric-visual AI framework for quantifying athlete intangibles — VCA / PD / PP / NQE components, feasibility-rated per 2025 research. Scaffolds the framework; pairs with `huggingface-skills` for ML pipelines. |

## Coming Soon

- `cardinals-intel` — St. Louis Cardinals baseball intelligence
- `mlb-sabermetrics` · `nfl-analytics` · `nba-analytics` · `cfb-analytics` — sport-specific sabermetric/analytics plugins wrapping the remaining BSI MCP tools
- `sports-viz` — data visualization patterns (Savant-style charts, biomechanics)
- `sports-arcade-dev` — browser sports game development

## Foundations

This marketplace is built on three official reference patterns:

1. **[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)** — Claude Code plugin layout, manifest schema, marketplace catalog pattern.
2. **[openai/plugins](https://github.com/openai/plugins)** — Codex plugin layout, `.codex-plugin/plugin.json` schema with rich `interface` metadata, dual-platform compatibility.
3. **[developers.openai.com/codex/use-cases](https://developers.openai.com/codex/use-cases)** — taxonomy of automation, data, engineering, front-end, integrations, knowledge work, workflow. Applied to sports domain in [`docs/USE-CASES.md`](./docs/USE-CASES.md).

Anthropic and OpenAI plugin folders are structural mirrors. Same subdirectories (`agents/`, `skills/`, `commands/`, `.mcp.json`) load identically on both. Ship one plugin folder, reach both platforms.

## Quality Bar

Every plugin in this marketplace meets the following bar before acceptance:

- **Real data only.** No mock arrays, no `Math.random()`, no placeholder tables. Every data surface wires to a live endpoint or a real computation.
- **Dual-platform.** Both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` present.
- **Agents have proper frontmatter** — `name`, `description`, tool whitelist, when-to-use examples.
- **Skills have invocation triggers** and explicit tool contracts.
- **Commands have parameters documented** and example usage.
- **README explains** install, data sources, free/paid tier boundaries, free-tier limits, source attribution.
- **No fabrication** — if a plugin can't reach its data source, it says so.

Full contributor bar in [`docs/CONTRIBUTING.md`](./docs/CONTRIBUTING.md).

## Structure

```
Sports-Plugins/
├── .claude-plugin/marketplace.json   # catalog — what's here, where to install from
├── plugins/{name}/                   # first-party plugins
│   ├── .claude-plugin/plugin.json    # Claude Code manifest
│   ├── .codex-plugin/plugin.json     # Codex manifest
│   ├── .mcp.json                     # MCP server config (if bundled)
│   ├── agents/*.md                   # agent definitions
│   ├── skills/{name}/SKILL.md        # skill definitions
│   ├── commands/*.md                 # slash commands
│   └── README.md                     # per-plugin docs
├── external_plugins/                 # community submissions (empty, contribution slot)
├── docs/                             # marketplace-wide documentation
│   ├── USE-CASES.md                  # Codex taxonomy applied to sports
│   ├── CONTRIBUTING.md               # quality bar + submission process
│   └── MCP-INTEGRATION.md            # how plugins consume the BSI MCP
└── .github/workflows/validate.yml    # CI: JSON schema check, markdown lint
```

## Contributing

See [`docs/CONTRIBUTING.md`](./docs/CONTRIBUTING.md). Community plugins land in `external_plugins/` after review. Plugin submissions must clear the quality bar, include both Claude and Codex manifests, and wire to real data.

## License

[MIT](./LICENSE) — use, fork, adapt, ship. Attribution appreciated.

## Origin

Austin Humphrey built this marketplace to put the sports intelligence infrastructure behind Blaze Sports Intel into every developer's hands. The sabermetrics engine covering all 330 NCAA DI baseball programs was already live at [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp). These plugins are the doors a developer walks through to use it.

Born to blaze the path beaten less.

