# College Baseball Sabermetrics

Advanced sabermetrics and analytics plugin for college baseball — with primary coverage depth for Texas Longhorns and the Big 12. Tuned for NCAA data sources, undercovered program tracking, and the analytical gaps ESPN leaves open.

## Coverage

- Pitcher evaluation: ERA+, FIP, xFIP, K/9, BB/9, WHIP, BABIP, strand rate, pitch-mix analysis
- Hitting: wOBA, wRC+, ISO, OBP, SLG, barrel rate, exit velocity (where available), sprint speed
- Lineup construction and batting-order optimization
- Game data ingestion from NCAA stats, Baseball Reference college pages, and BSI's own pipeline
- Weekend series preview and post-series verdict generation
- Texas Longhorns deep-dive mode: roster tracking, transfer portal impact, midweek starts

## Included Skills

- `sabermetrics-analysis` — core metric computation and interpretation layer
- `pitcher-analytics` — pitcher-specific evaluation, pitch mix, and sequencing
- `lineup-optimizer` — batting-order strategy and lineup construction
- `game-data-pipeline` — data ingestion, normalization, and storage patterns for NCAA game data

## MCP Servers

This plugin ships a plugin-local `.mcp.json` pointing Claude Code at the BSI MCP endpoint:

- `https://blazesportsintel.com/mcp` — Blaze Sports Intel live data (college baseball box scores, standings, rankings)

Use `/mcp` in Claude Code to confirm the server is connected after enabling the plugin.

## Representative Prompts

- `Evaluate the Texas Longhorns rotation using FIP and xFIP through the first 8 weeks of the season.`
- `Build a weekend series preview for UT vs. Oklahoma State with pitcher matchups and lineup tendencies.`
- `Rank the Big 12 bullpens by inherited-runner strand rate and K/9.`
- `Optimize the Longhorns batting order using wOBA and contact rate splits against left-handed starters.`
- `Ingest this NCAA box score JSON and compute game-level FIP and wRC+ for both teams.`
- `Write a post-series verdict for the Texas vs. UCLA series based on this weekend's box scores.`
