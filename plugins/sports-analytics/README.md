# Sports Analytics

General-purpose sports analytics plugin for building cross-sport data pipelines, interactive visualization components, and predictive models. Covers MLB, NFL, NBA, college football, college baseball, and NIL valuation tools.

## Coverage

- Multi-sport data pipeline patterns: API clients, normalization, caching, error handling
- Interactive stat visualization with Recharts and Framer Motion
- Predictive modeling: regression, win probability, player projection frameworks
- Performance benchmarking and percentile ranking across leagues
- NIL valuation tooling: follower reach, brand fit scoring, deal structure guidance

## Included Skills

- `data-pipeline` — multi-source ingestion, normalization, caching, and storage patterns
- `stats-visualization` — Recharts-based chart components, table layouts, and dashboard patterns for sports data
- `predictive-modeling` — regression, win probability estimation, and player projection frameworks

## MCP Servers

This plugin ships a plugin-local `.mcp.json` pointing Claude Code at the BSI MCP endpoint:

- `https://blazesportsintel.com/mcp` — Blaze Sports Intel live data across college baseball, MLB, NFL, NBA, and CFB

Use `/mcp` in Claude Code to confirm the server is connected after enabling the plugin.

## Representative Prompts

- `Build a Recharts scatter plot of FIP vs. ERA for every Big 12 pitcher with 30+ IP this season.`
- `Create a data pipeline that fetches live NFL scores from SportsDataIO every 30 seconds and stores them in Cloudflare KV.`
- `Build a simple win probability model for college baseball using run differential and inning.`
- `Generate a player projection system for next season using three-year weighted averages.`
- `Build a NIL valuation dashboard component that scores players on social reach, conference, and position.`
