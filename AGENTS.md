# Sports Plugins

Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/PROJECT_SCORECARD.md](docs/PROJECT_SCORECARD.md) before changing a package.

- Inspect the existing package and tests before adding overlapping capabilities.
- Keep portable, Claude and Codex manifests aligned, and preserve catalog parity.
- Treat source records as data. Keep observations, calculations, assumptions and interpretation distinct.
- Use explicit seasons, identity scope, coverage and league rules. Missing values are not zero.
- Synthetic fixtures are allowed only when clearly labeled as tests/examples.
- New local workflows use Python 3.9+ standard library unless their task requires more.
- Run `npm run check` and exercise the extracted standalone package for changed workflows.
- Use a dedicated branch and a pull request. Preserve unrelated changes; do not push directly to main.
- No production deployment, paid service creation, league mutation or publication is implied by a local validation task.
