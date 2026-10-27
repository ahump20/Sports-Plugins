# cbb-sabermetrics

**Live college baseball data and sabermetrics for every NCAA DI program: 330 teams, 32 conferences, 7 tools.**

Wraps the [Blaze Sports Intel MCP](https://blazesportsintel.com/mcp) server at `https://sabermetrics.blazesportsintel.com/mcp` so any developer using Claude Code or OpenAI Codex can query live college baseball intelligence through natural language.

> **Note on scope:** The BSI MCP exposes 7 read-only college baseball tools and nothing else. There are no MLB, NFL, NBA or college football tools. For MLB, football and basketball fundamentals, see [`baseball`](../baseball/), [`football`](../football/) and [`basketball`](../basketball/). `https://blazesportsintel.com/mcp` in a browser is a marketing page; the connector URL is `https://sabermetrics.blazesportsintel.com/mcp`.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install cbb-sabermetrics@Sports-Plugins
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install cbb-sabermetrics
```

After install, the MCP server auto-registers and 7 tools become available in your session. No API key required.

## What You Get

### 7 MCP Tools

| Tool | What it does |
|---|---|
| `bsi_get_scoreboard` | DI scores with venue and status (`date` YYYY-MM-DD and `conference` optional) |
| `bsi_get_standings` | W, L, win pct, runs scored, runs allowed, run differential, streak, games back (`conference` optional) |
| `bsi_get_rankings` | National Top 25 with rank, record and movement |
| `bsi_get_player_stats` | Player identity, team, position, and traditional batting or pitching stats when the source has them (`player` required, `team` optional) |
| `bsi_get_team_schedule` | Past results and upcoming games (`team` name or slug, like `texas` or `lsu`) |
| `bsi_get_match_detail` | Venue, weather, win predictions, play-by-play, team stats (`matchId` from the scoreboard) |
| `bsi_search_intel` | Web search of trusted college-baseball sources for news and scouting context (`query`, `limit` 1-10, `domains` optional) |

Advanced metrics (wOBA, FIP, BABIP, ISO and the like) are not returned by any tool. The BSI team sabermetrics, leaderboard and conference power index routes are paused until their source, method, sample boundaries and update metadata are documented. The agent and skills compute advanced metrics from the counting stats `bsi_get_player_stats` returns, using the formulas in [`college-baseball-sabermetrics`](../college-baseball-sabermetrics/), and label them as computed.

### 1 Agent

- **`college-baseball-intelligence`** — general-purpose analyst agent that handles research, analytics, scouting, editorial, and ranking tasks across all 330 DI programs.

### 2 Skills

- **`interpreting-advanced-metrics`** — computes wOBA/FIP/BABIP/ISO from returned counting stats and turns them into reads. Includes templates for hitter, pitcher, and team profiles. Season-state aware (don't read April with February caution).
- **`conference-strength`** — builds a conference strength read from standings and the Top 25. Teaches when record is misleading, when RPI overstates mid-major champions, and how to do real cross-conference comparisons.

### 3 Slash Commands

- **`/cbb-scout <team>`** — full scouting report on any DI program. Add `opponent={team}` for matchup preview.
- **`/cbb-leaderboard metric=<m> type=<t>`** — ranks the players or teams it pulls by a computed metric, filterable by conference. Covers only those players or teams, not all of DI.
- **`/cbb-power-index`** — conference strength rankings computed from standings and the Top 25. Add `conference=<c>` for deep dive.

## Data Sources

The BSI MCP fans out to these primary sources:

| Source | Primary For | Notes |
|---|---|---|
| **Highlightly** (partner feed) | Live scores, standings, match detail | Fastest, deepest coverage |
| **ESPN Site API** | Rankings, schedules | Fallback when Highlightly returns empty |

Every response includes a `meta` envelope with `source`, `fetched_at`, `timezone: "America/Chicago"`.

## Free Tier

- **Rate limit:** 30 requests/minute per IP
- **Auth:** none required
- **Caching:** 15–30s for live scores, 60s for standings, 5min for final games, 1hr for rosters

For higher limits or enterprise SLA, contact [john.humphrey@blazesportsintel.com](mailto:john.humphrey@blazesportsintel.com).

## Example Queries

Once installed, try these in your Claude Code or Codex session:

```
Rank these SEC hitters by wOBA: [names]
```
→ The agent pulls each with `bsi_get_player_stats`, computes wOBA from the counting stats (formula and PA shown), applies the `interpreting-advanced-metrics` skill, and returns a table labeled as covering only those hitters.

```
Which conferences are strongest right now, and where does the SEC stand?
```
→ The agent calls `bsi_get_standings` and `bsi_get_rankings`, applies the `conference-strength` skill, and returns conference rankings computed from standings with analytical reads.

```
Scout Oregon State for me.
```
→ `/cbb-scout oregon-state` — returns full scouting profile using standings, recent form, key player stats, conference position, next opponent.

```
How does LSU's offense compare to Tennessee's?
```
→ The agent chains `bsi_get_standings` and `bsi_get_team_schedule` for both (runs scored, run differential, results), adds computed metrics for key hitters from `bsi_get_player_stats`, and returns a structured comparison.

## Data Integrity

This plugin enforces the BSI data integrity standard:

- **No fabrication.** If a tool returns empty, the agent says so. It does not invent stats.
- **Source attribution on every claim.** Every statistical assertion cites `meta.source` and `meta.fetched_at`.
- **Season-state aware.** Early February numbers get different confidence than May numbers.
- **Computed, not invented.** Advanced metrics are computed from returned counting stats with formula and sample size shown. If an input is missing, the metric is named as not computable.

## Dependencies

None. This is the anchor plugin in the Sports-Plugins marketplace. Other plugins (like `texas-longhorns-intel`) depend on this.

## Related Plugins

- [`texas-longhorns-intel`](../texas-longhorns-intel/) — Texas-specific intelligence layer built on top of `cbb-sabermetrics`.
- More coming — `cardinals-intel`, `sports-storytelling`, `sports-viz`, `sports-arcade-dev`.

## Troubleshooting

**MCP server doesn't connect:**
- Check `.mcp.json` was loaded by your Claude Code or Codex session.
- Verify `https://sabermetrics.blazesportsintel.com/mcp` is reachable.
- Check your session logs for connection errors.

**Tool calls return empty:**
- The season may be in an off-window (e.g., mid-June through mid-January for college baseball).
- The upstream data source (Highlightly/ESPN) may be temporarily degraded — check `meta.degraded` in the response.
- Rate limit: confirm you're under 30 requests/minute.

**Need higher rate limits or paid tier:**
- Contact [john.humphrey@blazesportsintel.com](mailto:john.humphrey@blazesportsintel.com).

## License

[MIT](../../LICENSE) — use, fork, adapt, ship.

## Credit

Built by [Austin Humphrey](https://blazesportsintel.com) / Blaze Sports Intel. The MCP server covering all 330 NCAA DI baseball programs is at `https://sabermetrics.blazesportsintel.com/mcp`; [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp) is its marketing page.
