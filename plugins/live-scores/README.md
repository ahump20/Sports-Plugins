# Live Scores

Real-time scoreboard UI components and live data integration patterns for embedding live sports scores in Next.js web apps and React Native mobile clients. Covers college baseball, MLB, NFL, NBA, and college football.

## Coverage

- Scoreboard UI components: game cards, line scores, cross-sport unified views
- Live data integration: Cloudflare KV polling, SportsDataIO webhooks, BSI MCP real-time feeds
- Mobile-responsive scoreboard layouts with status indicators
- In-game state rendering: inning/quarter/period, count, runners on base (baseball)
- Score change animations and live-update indicators

## Included Skills

- `scoreboard-ui` — React scoreboard components, live status indicators, mobile-first layout patterns
- `real-time-data` — Cloudflare Worker polling, KV caching, polling interval management, and stale-data handling

## MCP Servers

This plugin ships a plugin-local `.mcp.json` pointing Claude Code at the BSI MCP endpoint:

- `https://blazesportsintel.com/mcp` — Blaze Sports Intel live scores across college baseball, MLB, NFL, NBA, and CFB

Use `/mcp` in Claude Code to confirm the server is connected after enabling the plugin.

## Representative Prompts

- `Build a college baseball scoreboard component that shows live inning-by-inning line scores for all Big 12 games today.`
- `Create a cross-sport unified scores page that shows MLB, college baseball, and NFL results for the current day.`
- `Add a Cloudflare Worker that fetches live SportsDataIO NFL scores every 30 seconds and stores them in KV.`
- `Build a live score card component with a pulsing indicator for in-progress games and a final badge for completed games.`
- `Implement a React hook that polls the BSI MCP endpoint for live college baseball scores every 60 seconds.`
