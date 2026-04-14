---
name: bsi-gameday-ops
description: "Live game coverage operations for Blaze Sports Intel. Real-time game monitoring, in-game analysis, post-game rapid recaps, and leverage situation tracking. Speed and accuracy are co-equal — this skill runs when games are happening NOW. Triggers on: \"live game\", \"game thread\", \"score update\", \"in-game\", \"live coverage\", \"gameday\", \"game day\", \"watching the game\", \"current inning\", \"bullpen usage\", \"leverage situation\", \"win probability\", \"game just ended\", \"final score\", \"walk-off\", \"recap the game\", any request about a game currently in progress or finished within the last 2 hours. Also trigger during college baseball game hours (Tue-Sun, 2 PM - 11 PM CT) when someone asks \"what's happening\" or \"any good games\". When in doubt during game hours, trigger this."
---

# BSI Gameday Operations

Live coverage desk. Games are happening. Speed matters.

## Core Rule

SKILL.md is the dispatcher. Workflow details live in references/. Output templates live in assets/. Every tool call during live coverage optimizes for latency first, depth second.

## Routing

```
Where does this request come from?
├─ college-baseball-intelligence routes live game asks → HERE
├─ texas-longhorns-baseball-intelligence routes live Texas game asks → HERE
├─ Direct trigger: any "live game" or "what's happening" during game hours → HERE
└─ Post-game depth analysis (not rapid recap) → BACK to intelligence skills
```

**Game hours** (college baseball): Tue–Sun, ~2 PM – 11 PM CT. Fri–Sun = primary conference series.

## Workflow Decision Tree

```
What does the user need?
├─ National scoreboard / "what games are on" → references/live-monitoring.md
│  Output: assets/scoreboard-template.md
├─ Track one specific game in depth → references/single-game-focus.md
│  Output: assets/game-focus-template.md
├─ Game just ended / "recap that game" → references/post-game-recap.md
│  Output: assets/recap-template.md
├─ High-stakes moment / "bases loaded" → references/leverage-situations.md
│  Output: assets/leverage-template.md
└─ Deep post-game analysis → references/handoff-protocol.md (route back)
```

## Tool Priority (speed-optimized)

See `references/tool-priority.md` for the full tiered tool selection:

```
Tier 1 — Real-time (use first, always):
├─ bsi_get_scoreboard → live scores across all games
├─ get_live_games → currently in-progress games
└─ bsi_get_match_detail → box score for specific game

Tier 2 — Context (use to enrich, after Tier 1):
├─ bsi_get_team_sabermetrics → advanced stats for a team
├─ bsi_get_standings → conference standings
└─ bsi_get_rankings → national rankings

Tier 3 — Post-game (use after game ends):
├─ bsi_get_player_stats → individual lines
└─ analyze_game → AI-generated game analysis
```

## Handoff Protocol

See `references/handoff-protocol.md` — routing table for requests that need more depth than live coverage provides.

## Non-Negotiables

- Speed over depth. A fast verified score beats a slow analytical essay.
- Source every claim: "Per BSI scoreboard as of 8:42 PM CT" — always.
- Do not guess scores. If the tool call fails, say the score is unverified.
- No homerism. The mid-major upset is as important as the SEC showdown.
- Post-game rapid recap stays here. Deep analysis routes back to intelligence skills.
