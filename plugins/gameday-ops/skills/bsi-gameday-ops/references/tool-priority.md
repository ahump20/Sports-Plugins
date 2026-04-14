# Tool Priority — Speed-Optimized

During live coverage, tool selection optimizes for latency, not depth.

---

## MCP Tool Name Mapping

Tools use `bsi_` prefixed names. Search available tools for that prefix.
The Blaze Intelligence tools have their own namespace.

---

## Tier 1 — Real-Time (use first, always)

| Tool | MCP Suffix | Purpose | TTL |
|------|------------|---------|-----|
| Live scoreboard | `bsi_get_scoreboard` | Current scores, game status | 60s |
| Live games | `get_live_games` (Blaze Intelligence) | What's in progress right now | Real-time |
| Match detail | `bsi_get_match_detail` | Play-by-play, leverage, weather | 2min |

**Scoreboard inputs**: `date` (YYYY-MM-DD, optional, defaults today CT), `conference` (optional filter).

**Match detail inputs**: `matchId` (Highlightly ID — get this from scoreboard results first).

---

## Tier 2 — Context (enrich, don't delay)

| Tool | MCP Suffix | Purpose | TTL |
|------|------------|---------|-----|
| Team sabermetrics | `bsi_get_team_sabermetrics` | Pre-game baseline | 6hr |
| Standings | `bsi_get_standings` | Conference race implications | 1hr |
| Rankings | `bsi_get_rankings` | National ranking context | 1hr |
| Game analysis | `analyze_game` (Blaze Intelligence) | AI analytical layer | Varies |
| Predictions | `predict_game_outcome` (Blaze Intelligence) | Win probability model | Varies |

Use Tier 2 tools to **enrich** a report. Never let them **delay** a score report.

---

## Tier 3 — Post-Game (use after final)

| Tool | MCP Suffix | Purpose |
|------|------------|---------|
| Team schedule | `bsi_get_team_schedule` | Updated record, recent results |
| Leaderboard | `bsi_get_leaderboard` | Did any player move on national boards? |
| Player stats | `bsi_get_player_stats` | Individual stat lines for featured players |
| Conference power | `bsi_get_conference_power_index` | Updated conference strength |

---

## Failure Protocol

Live coverage failure is more urgent than research failure. Handle fast:

### Scoreboard down
1. Fall back to `get_live_games` (Blaze Intelligence)
2. If both fail: "Live scores temporarily unavailable. Checking alternative sources."
3. Last resort: web search for the specific game score

### Match detail unavailable
1. Report the score from scoreboard — skip play-by-play
2. State: "Detailed play data temporarily unavailable — score confirmed via [source]."

### Multiple tools down
1. Check `get_system_status` (Blaze Intelligence)
2. Report the system state
3. Suggest checking blazesportsintel.com directly

### Data source hierarchy
```
1. College Baseball Sabermetrics MCP (primary)
        ↓
2. Blaze Intelligence MCP (secondary)
        ↓
3. BSI Website API (blazesportsintel.com/api/*)
        ↓
4. ESPN (fallback)
```

`meta.source` in every tool response identifies the serving layer.
`meta.fetched_at` is the ISO timestamp for verified claims.
