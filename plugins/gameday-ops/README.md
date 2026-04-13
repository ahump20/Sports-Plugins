# gameday-ops

**Live game coverage desk for sports intelligence.** When games are happening now, this plugin runs the show.

Built on the production `bsi-gameday-ops` skill used by Blaze Sports Intel editorial — the same workflows that cover college baseball (Tue–Sun game hours), MLB, NFL, NBA, and CFB gamedays. Speed and accuracy are co-equal. Zero fabricated scores, zero "last updated just now" filler, real data from the live MCP.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install gameday-ops
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install gameday-ops
```

## What You Get

### 1 Skill (production-grade)

- **`bsi-gameday-ops`** — live coverage dispatcher with 6 reference workflows and 4 output templates.
  - `references/live-monitoring.md` — polling cadence, source priority, freshness stamps
  - `references/leverage-situations.md` — leverage index reads, WPA swings, high-leverage flags
  - `references/single-game-focus.md` — when to zoom on one game vs. the slate
  - `references/post-game-recap.md` — rapid-fire recap template (30 min from final out)
  - `references/handoff-protocol.md` — routing from college-baseball and team-specific plugins
  - `references/tool-priority.md` — Highlightly → SportsDataIO → ESPN fallback chain
  - `assets/scoreboard-template.md`, `leverage-template.md`, `game-focus-template.md`, `recap-template.md`

### 2 Commands

- **`/gameday-watch`** — start live monitoring on the current slate. Flags close games, high-leverage situations, and upset alerts.
- **`/gameday-recap <game-id>`** — rapid post-game recap using the recap template. Enforces anti-fabrication — no made-up quotes, no invented win probabilities.

### MCP Server

This plugin bundles `.mcp.json` pointing at the live **Blaze Sports Intel MCP** at `https://blazesportsintel.com/mcp` — 31 tools across 5 sports. Free tier, 30 req/min, no API key.

## Routing

`gameday-ops` is the destination skill during game hours. Other sports-plugins (like `cbb-sabermetrics` and `texas-longhorns-intel`) route live-game queries here:

```
User asks "any Texas game tonight?"
  ├─ During game hours (2 PM – 11 PM CT, Tue–Sun) → gameday-ops
  └─ Otherwise → texas-longhorns-intel for schedule lookup
```

## Non-Negotiable Rules

- **Anti-fabrication**: every score, inning, and stat comes from the MCP or says "I don't know." No guesses.
- **Freshness comes from metadata**: every tool response includes `meta.fetched_at`. Never hardcode "live" or "just now" in output.
- **Four data states**: every game surface must handle loading, error, empty, and populated. No undefined or blank output.

## Origin

Ported from `~/.claude/skills/bsi-gameday-ops/` — the production skill driving Blaze Sports Intel's live coverage desk. Same content, same discipline.
