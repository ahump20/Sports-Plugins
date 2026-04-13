---
name: gameday-watch
description: Start live monitoring on the current sports slate. Flags close games, high-leverage situations, and upset alerts.
---

# /gameday-watch

Start the live coverage monitor.

## Usage

```
/gameday-watch                    # all sports in season
/gameday-watch sport=college-baseball
/gameday-watch sport=mlb team=STL
/gameday-watch leverage=high      # only flag high-leverage situations
```

## What it does

1. Calls `bsi_get_scoreboard` (or sport-specific equivalent) via the Blaze Sports Intel MCP.
2. Filters for games currently in progress.
3. For each live game, reads leverage state using the `leverage-situations.md` reference.
4. Returns a formatted board: score, inning/quarter, win probability, leverage flag.
5. Every entry stamped with `meta.fetched_at`.

## Output

Uses `assets/scoreboard-template.md` from the bsi-gameday-ops skill. Close games (score diff ≤ 3 in baseball, ≤ 7 in football, ≤ 5 in basketball) get 🔥. High-leverage late-inning situations get ⚡.

## Refresh cadence

The scoreboard is polled on a 15–30 second loop when invoked without a team filter. Filtered queries (single team) poll every 10 seconds. Matches the KV TTL convention on the BSI backend.

## Rules

- No fabricated scores. If the MCP returns nothing, return "No live games at this time" — never invent filler.
- No editorializing before the game ends. Leverage calls are data, not opinion.
