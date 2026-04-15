# Contributing to Sports-Plugins

Thank you for your interest in contributing sports plugins to this marketplace!

## Plugin Structure

Every plugin follows the standard Claude Code plugin structure:

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
├── commands/            # Legacy slash commands (optional)
└── README.md            # Documentation (required)
```

## Submitting a Plugin

### Internal Plugins (`/plugins`)

Internal plugins cover core sports functionality maintained by the Sports-Plugins team:

1. Fork this repository
2. Create your plugin under `plugins/your-plugin-name/`
3. Include all required files (see structure above)
4. Submit a pull request

### External Plugins (`/external_plugins`)

Third-party sports integrations from partners and the community:

1. Fork this repository
2. Create your plugin under `external_plugins/your-plugin-name/`
3. Include all required files
4. Submit a pull request

## Plugin Requirements

### Required Files

- **`.claude-plugin/plugin.json`** — Must include `name`, `description`, and `author`
- **`README.md`** — Clear documentation explaining what the plugin does

### Quality Standards

- Plugins must focus on sports-related functionality
- All MCP server URLs must be valid and accessible
- Skills must have clear, specific trigger descriptions
- No hardcoded API keys or secrets

### Codex Compatibility

Plugins in this marketplace are designed for dual compatibility:

- **Claude Code** — Native plugin support via `.claude-plugin/` and `skills/`
- **OpenAI Codex** — MCP server endpoints work with Codex tool-use patterns

When building MCP integrations, ensure your server endpoints follow the [Model Context Protocol specification](https://modelcontextprotocol.io/).

## Code of Conduct

Be respectful, collaborative, and constructive. We're all here to make sports data more accessible to AI coding assistants.
