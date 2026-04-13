# cbb-sabermetrics

**Live college baseball sabermetrics for every NCAA DI program — 330 teams, 32 conferences, 10 tools.**

Wraps the college-baseball tool family of the [Blaze Sports Intel MCP](https://blazesportsintel.com/mcp) so any developer using Claude Code or OpenAI Codex can query live college baseball intelligence through natural language.

> **Note on scope:** The BSI MCP actually exposes 31 tools across 5 sports (MLB, NFL, NBA, CFB, and NCAA DI college baseball). This plugin surfaces only the 10 college-baseball tools with CBB-specific agents, skills, and commands. For the other sports, see `mlb-sabermetrics`, `nfl-analytics`, `nba-analytics`, and `cfb-analytics` (coming soon).

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install cbb-sabermetrics
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install cbb-sabermetrics
```

After install, the MCP server auto-registers and 10 tools become available in your session. No API key required.

## What You Get

### 10 MCP Tools

| Tool | What it does |
|---|---|
| `bsi_get_scoreboard` | Today's DI scores with venue and status |
| `bsi_get_standings` | Conference standings with records and run differential |
| `bsi_get_rankings` | D1Baseball Top 25 national rankings |
| `bsi_get_team_sabermetrics` | Advanced team metrics (wOBA, wRC+, FIP, ERA−, BABIP, ISO) |
| `bsi_get_leaderboard` | Top hitters or pitchers by metric, filterable by conference |
| `bsi_get_conference_power_index` | SOS-adjusted conference strength rankings |
| `bsi_get_player_stats` | Player search with batting or pitching stats |
| `bsi_get_team_schedule` | Full season schedule (past and upcoming) |
| `bsi_get_match_detail` | Deep game data — venue, weather, predictions, play-by-play, team stats |
| `bsi_search_intel` | Cross-entity search across teams, players, games |

### 1 Agent

- **`college-baseball-intelligence`** — general-purpose analyst agent that handles research, analytics, scouting, editorial, and ranking tasks across all 330 DI programs.

### 2 Skills

- **`interpreting-advanced-metrics`** — turns raw wOBA/FIP/wRC+/BABIP/ISO numbers into reads. Includes templates for hitter, pitcher, and team profiles. Season-state aware (don't read April with February caution).
- **`conference-strength`** — reads the Power Index correctly. Teaches when record is misleading, when RPI overstates mid-major champions, and how to do real cross-conference comparisons.

### 3 Slash Commands

- **`/cbb-scout <team>`** — full scouting report on any DI program. Add `opponent={team}` for matchup preview.
- **`/cbb-leaderboard metric=<m> type=<t>`** — top N leaderboards by advanced metric, filterable by conference.
- **`/cbb-power-index`** — SOS-adjusted conference strength rankings. Add `conference=<c>` for deep dive.

## Data Sources

The BSI MCP fans out to three primary sources:

| Source | Primary For | Notes |
|---|---|---|
| **Highlightly** (partner feed) | Live scores, standings, match detail | Fastest, deepest coverage |
| **BSI Savant** (our compute layer) | Advanced metrics (wOBA, wRC+, FIP, etc.) | Recomputed every 6 hours from box-score data |
| **ESPN Site API** | Rankings, schedules | Fallback when Highlightly returns empty |

Every response includes a `meta` envelope with `source`, `fetched_at`, `timezone: "America/Chicago"`.

## Free Tier

- **Rate limit:** 30 requests/minute per caller
- **Auth:** none required
- **Caching:** 15–30s for live scores, 60s for standings, 5min for final games, 1hr for rosters

For higher limits or enterprise SLA, contact [john.humphrey@blazesportsintel.com](mailto:john.humphrey@blazesportsintel.com).

## Example Queries

Once installed, try these in your Claude Code or Codex session:

```
What are the top 10 SEC hitters by wRC+?
```
→ The agent picks `bsi_get_leaderboard`, applies the `interpreting-advanced-metrics` skill, returns a clean table with park-adjusted context.

```
Give me the current conference power index and explain where the SEC stands.
```
→ The agent picks `bsi_get_conference_power_index`, applies the `conference-strength` skill, returns rankings with analytical reads.

```
Scout Oregon State for me.
```
→ `/cbb-scout oregon-state` — returns full scouting profile using team sabermetrics, recent form, conference position, next opponent.

```
How does LSU's offense compare to Tennessee's?
```
→ The agent chains `bsi_get_team_sabermetrics` for both, applies park adjustments, returns a structured comparison.

## Data Integrity

This plugin enforces the BSI data integrity standard:

- **No fabrication.** If a tool returns empty, the agent says so. It does not invent stats.
- **Source attribution on every claim.** Every statistical assertion cites `meta.source` and `meta.fetched_at`.
- **Season-state aware.** Early February numbers get different confidence than May numbers.
- **Park-adjusted by default.** wRC+ preferred over raw wOBA for cross-program comparison.

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

Built by [Austin Humphrey](https://blazesportsintel.com) / Blaze Sports Intel. The MCP engine covering all 330 NCAA DI baseball programs lives at [blazesportsintel.com/mcp](https://blazesportsintel.com/mcp).
