# Contributing to Sports Plugins

Start with a sports task someone needs to finish. State the inputs, the useful output and how a reviewer can tell whether it is right. Extend an existing package when the workflow fits; propose a separate plugin when it has a distinct job.

## Required package

Every catalog entry must include:

| Location | Requirement |
|---|---|
| `plugin.json` | Portable manifest with the agent-plugins schema and the same name/version as compatibility manifests |
| `.claude-plugin/plugin.json` | Claude metadata |
| `.codex-plugin/plugin.json` | Codex metadata and explicit component paths |
| `skills/<name>/SKILL.md` | At least one discoverable skill with precise triggers, a frontmatter `name` matching its directory, and a nonempty `description`; other components may accompany it |
| `README.md` | Purpose, install instructions, exact input/output, example, source requirements and limitations |
| `LICENSE` | License covering the packaged source |
| `mcp.json` and `.mcp.json` | Both portable and compatibility configuration when a server is bundled |

Use the existing [Roster Watch](plugins/roster-watch/) or [Editorial Desk](plugins/editorial-desk/) package as a concrete reference. Keep supporting scripts, fixtures and references inside the package so it survives standalone extraction.

Register accepted packages in both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`. Keep names and source paths aligned. Do not register placeholders or advertise a dependency that has not been implemented.

## Evidence and calculations

Preserve source URLs or supplied-file attribution, source observation time, season, coverage and retrieval time where relevant. State unavailable fields; never replace them with plausible values. Resolve identities before joining data and require explicit league rules before applying them.

Synthetic fixtures are welcome in tests and clearly labeled examples. They must never be presented as live or historical observations. Source-backed fixtures must record their source and scope. A script must use real computation, not select a canned answer.

For a new behavior, include a small hand-verifiable case, an adverse input and the end-to-end command a user will run. Test errors as well as successful output. A simulation must state its assumptions and distinguish scenario shares from forecast probabilities.

Provider access, licensing and authentication belong in the package README. An unauthenticated endpoint does not imply permission for commercial redistribution. Never package credentials.

## Verification

Run from the repository root with Node 22.12+ and Python 3.9+:

```bash
npm ci
npm run check
npm run package:plugins
```

Run a documented example from an extracted archive outside the checkout. Check both JSON and human-readable output. If a host CLI is available, validate and install into an isolated test profile; record host/version and what was actually invoked.

Use [the project scorecard](docs/PROJECT_SCORECARD.md) for the complete gate. Report blocked external checks separately from passing offline checks. Never relax a test or remove an existing package to make a new addition pass.

## Pull requests

Describe the user problem, behavior added, source requirements, tests run and remaining limitations. Preserve unrelated work. Submit a branch and pull request; follow the repository's tagged release process after review. A source PR is not an account-plugin publication or a live-service deployment.
