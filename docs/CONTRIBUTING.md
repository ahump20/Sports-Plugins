# Contributing to Sports-Plugins

Sports-Plugins is a curated marketplace. Every plugin meets a quality bar before landing in `external_plugins/` or (for first-party plugins) `plugins/`.

This doc is the bar.

## What We Accept

**Sports domain only.** Plugins must serve a sports-specific use case — analytics, live data, scouting, editorial, visualization, game development, sports-specific tooling. Generic dev plugins belong in [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) or [openai/plugins](https://github.com/openai/plugins).

**Dual-platform.** Every plugin ships BOTH:
- `.claude-plugin/plugin.json` (Claude Code manifest)
- `.codex-plugin/plugin.json` (Codex manifest)

Single-platform plugins are rejected. The marketplace's reason for being is cross-platform sports infrastructure.

**Real data.** No mock arrays, no `Math.random()`, no hardcoded stat tables, no placeholder teams. Every data surface wires to a live endpoint or a real computation. If the source is free-tier, say so. If the source requires a paid API key, say so clearly in the README and expose the key variable.

## Required Structure

```
plugins/{your-plugin}/
├── .claude-plugin/plugin.json    # required
├── .codex-plugin/plugin.json     # required
├── .mcp.json                     # required if plugin bundles MCP servers
├── agents/*.md                   # at least one agent OR skill OR command
├── skills/{name}/SKILL.md        # if providing skills
├── commands/*.md                 # if providing slash commands
└── README.md                     # required
```

### `.claude-plugin/plugin.json` minimum

```json
{
  "name": "your-plugin-name",
  "description": "One-sentence summary of what it does and who uses it.",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://example.com"
  }
}
```

### `.codex-plugin/plugin.json` minimum

Richer than the Claude manifest. Mirrors OpenAI's canonical shape:

```json
{
  "name": "your-plugin-name",
  "version": "0.1.0",
  "description": "...",
  "author": {...},
  "homepage": "...",
  "repository": "https://github.com/your-org/your-repo",
  "license": "MIT",
  "keywords": [...],
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "Human Readable Name",
    "shortDescription": "5-10 word summary",
    "longDescription": "Full paragraph describing what it does.",
    "developerName": "Your Name",
    "category": "analytics | scouting | editorial | visualization | game-development",
    "capabilities": ["Read", "Write", "Interactive"],
    "websiteURL": "...",
    "defaultPrompt": "What a user might type to invoke this plugin.",
    "brandColor": "#BF5700",
    "composerIcon": "./assets/icon-small.svg",
    "logo": "./assets/icon.png"
  }
}
```

### Agents

Every agent file has frontmatter:

```markdown
---
name: agent-name
description: >
  When to use this agent. Include specific trigger phrases.
  Keep the description concrete — agents are dispatched from descriptions.
---

# Agent Body

Rest of the agent definition.
```

### Skills

Every skill has a SKILL.md with frontmatter and a body that documents:

- What the skill knows
- What tools it uses
- How to invoke it
- Quality gates

Same frontmatter pattern as agents.

### Commands

Slash commands are markdown files with frontmatter documenting parameters and usage.

## Quality Gate Checklist

Before submitting a plugin, confirm:

- [ ] Plugin has both `.claude-plugin/plugin.json` AND `.codex-plugin/plugin.json`
- [ ] Both manifests parse as valid JSON
- [ ] Every agent file has valid frontmatter (`name`, `description`)
- [ ] Every skill has `SKILL.md` with frontmatter
- [ ] README explains install, data sources, free/paid tier, free-tier limits
- [ ] No mock data anywhere (no `Math.random()`, no hardcoded stat arrays, no placeholder teams)
- [ ] No invented statistics, scores, rosters, or rankings
- [ ] Every live data claim in documentation includes source attribution
- [ ] If the plugin uses an MCP server, `.mcp.json` is valid and the server URL resolves
- [ ] If the plugin depends on another plugin, dependency is declared in marketplace.json
- [ ] LICENSE is included (MIT preferred)
- [ ] CI validation passes (see `.github/workflows/validate.yml`)

## Data Freshness Discipline

If your plugin serves live sports data:

- Every response includes a `meta` object with `source`, `fetched_at`, `timezone`.
- No hardcoded "updated X minutes ago" strings. Freshness comes from response metadata.
- If the underlying source returned empty, surface "No data" — never fabricate a plausible-looking response.
- Rate limits and cache TTLs are documented in the README.

## Submission Process

1. Fork this repo.
2. Add your plugin under `external_plugins/{your-plugin-name}/`.
3. Add an entry in `.claude-plugin/marketplace.json` with `status: "pending-review"`.
4. Open a PR with your plugin + marketplace entry.
5. CI validation runs automatically.
6. A maintainer reviews against this quality bar.
7. On acceptance, PR is merged and `status` flips to `available`.

## What Gets Rejected

- **Mock data anywhere.** Instant rejection.
- **Single-platform plugins.** Must ship both manifests.
- **Plugins that fabricate statistics, rosters, or scores.** Instant rejection, regardless of domain.
- **Plugins that scrape without authorization** or violate a source's ToS.
- **Plugins that require undocumented paid API keys** without disclosure.
- **Plugins outside the sports domain.**
- **Plugins that overlap with existing first-party plugins** unless they offer meaningfully different coverage or approach.

## Contact

Questions about contributing: open an issue or email john.humphrey@blazesportsintel.com.
