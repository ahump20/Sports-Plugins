# Sports-Plugins

A curated marketplace of high-quality community sports plugins for [Claude Code](https://code.claude.com), [OpenAI Codex](https://developers.openai.com/codex/use-cases), and AI coding assistants. Covers live scores, sabermetrics, fantasy sports, and sports data analytics.

> **Foundation:** Built on the plugin architecture from [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) with MCP (Model Context Protocol) endpoints designed for dual compatibility with Claude Code and OpenAI Codex tool-use patterns.

## Plugins

### Core Plugins (`/plugins`)

| Plugin | Description |
|--------|-------------|
| **[live-scores](plugins/live-scores/)** | Real-time scores, schedules, and game updates for MLB, NFL, NBA, and college sports |
| **[college-baseball-sabermetrics](plugins/college-baseball-sabermetrics/)** | Advanced college baseball sabermetrics — wOBA, FIP, wRC+, barrel rates, pitch analytics |
| **[fantasy-sports](plugins/fantasy-sports/)** | Fantasy roster optimization, matchup analysis, trade evaluation, and waiver wire picks |
| **[sports-data-explorer](plugins/sports-data-explorer/)** | Query stats, compare players, and explore data across all major sports |

### External Plugins (`/external_plugins`)

| Plugin | Description |
|--------|-------------|
| **[blaze-sports-intel](external_plugins/blaze-sports-intel/)** | [BSI](https://blazesportsintel.com) integration — college baseball box scores, Texas Longhorns intel, and advanced analytics via [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp) |

## Installation

Install any plugin directly via Claude Code:

```
/plugin install <plugin-name>@Sports-Plugins
```

Or browse available plugins:

```
/plugin > Discover
```

## Plugin Structure

Every plugin follows the standard [Claude Code plugin structure](https://github.com/anthropics/claude-plugins-official):

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── skills/              # Skill definitions (preferred)
│   ├── skill-name/
│   │   └── SKILL.md     # Model-invoked skill
│   └── command-name/
│       └── SKILL.md     # User-invoked slash command
└── README.md            # Documentation (required)
```

### Dual Compatibility: Claude Code + OpenAI Codex

Plugins in this marketplace are designed for **both** Claude Code and OpenAI Codex:

- **Claude Code** — Native plugin support via `.claude-plugin/` metadata and `skills/` definitions
- **OpenAI Codex** — MCP server endpoints (`.mcp.json`) provide tool-use access compatible with Codex's function-calling patterns

The [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) serves as the bridge — any plugin with an `.mcp.json` endpoint works seamlessly with any MCP-compatible AI coding assistant.

## Validation

```bash
node scripts/validate-plugins.mjs
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting new sports plugins.

## Related Projects

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — The official Claude Code plugins directory
- [ahump20/BSI](https://github.com/ahump20/BSI) — Blaze Sports Intel — the sports platform powering the BSI external plugin
- [OpenAI Codex Use Cases](https://developers.openai.com/codex/use-cases) — Codex agent patterns for tool use

## License

[MIT](LICENSE)
