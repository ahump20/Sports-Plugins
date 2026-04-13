---
name: gameday-recap
description: Rapid post-game recap for any finished game. 30-minute turnaround from final score to publishable draft.
---

# /gameday-recap

Generate a post-game recap using the production BSI recap template.

## Usage

```
/gameday-recap game=<game-id>
/gameday-recap team=TEX date=2026-04-12
/gameday-recap last                # most recent finished game
```

## What it does

1. Calls `bsi_get_match_detail` (or sport-specific equivalent) for the game.
2. Identifies the swing plays, the storyline player, the key inning/drive/possession.
3. Drafts using `assets/recap-template.md`:
   - Headline (no clickbait, no fabricated drama)
   - Lead graf: who won, how, what it means for standings/race
   - Three bullets: turning point, hero, goat-candidate
   - Pull quotes ONLY if the MCP returns real quoted text (never invented)
   - Stat block with `meta.source` and `meta.fetched_at`

## Non-negotiable

- **No invented quotes.** If `bsi_get_match_detail` doesn't return quoted text, the recap has no quotes.
- **No "sources say".** Every claim is either a data point with a source, or cut.
- **Anti-freshness-fabrication.** "Last updated X ago" comes from `meta.fetched_at` computation, never a hardcoded string.

## 30-minute discipline

Goal is a publishable draft within 30 minutes of the final score. Beyond 30 min, the recap window closes and the story becomes next-day analysis (different workflow).

## Escalation

For games with ≥ 5% upset factor or ≥ 0.40 WPA swing on a single play, route to a longer feature piece (handoff to `editorial-desk` plugin when available).
