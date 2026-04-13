# Contributing to Sports-Plugins

Thank you for your interest in contributing to the Sports-Plugins marketplace.

## Getting Started

```bash
git clone https://github.com/ahump20/Sports-Plugins.git
cd Sports-Plugins
npm install
npm run check   # typecheck + lint + test + validate
```

## Creating a New Plugin

1. Create a directory under `plugins/<your-plugin-name>/`.

2. Add the required files:

   ```
   plugins/<your-plugin-name>/
     .claude-plugin/
       plugin.json          ← Plugin manifest (see existing plugins for schema)
     README.md              ← Overview, coverage, included skills, representative prompts
     skills/
       <skill-name>/
         SKILL.md           ← Skill instructions loaded by Claude Code
     src/
       index.ts             ← TypeScript entry point
   ```

3. Add an `.mcp.json` if your plugin uses MCP servers.

4. Register your plugin in `.claude-plugin/marketplace.json`.

5. Add TypeScript source under `plugins/<your-plugin-name>/src/` — at minimum, export the types and core logic your skill documents describe.

6. Write tests alongside your source code (`*.test.ts`).

## Quality Bar

- **Skills must be specific and actionable.** Generic descriptions ("this plugin does analytics") will be rejected. See `college-baseball-sabermetrics` for the content standard.
- **TypeScript source must compile cleanly.** Run `npm run typecheck` before submitting.
- **Tests must pass.** Run `npm test` before submitting.
- **Plugin validation must pass.** Run `npm run validate` to check manifest integrity.

## Code Style

- TypeScript strict mode is enabled.
- Use the project ESLint config — `npm run lint` to check.
- Two-space indentation, LF line endings (enforced by `.editorconfig`).
- Prefer explicit types over `any`. Use `unknown` when the type is genuinely unknown.

## Pull Request Process

1. Fork the repo and create a feature branch.
2. Make your changes.
3. Run `npm run check` to validate everything.
4. Open a PR against `main` with a clear description of what the plugin covers and why.
5. A maintainer will review for quality, accuracy, and structural compliance.

## Reporting Issues

Open a GitHub issue with:
- Which plugin is affected
- Expected behavior vs. actual behavior
- Steps to reproduce (if applicable)
- Any relevant data samples or error messages
