---
name: recap-draft
description: Draft a long-form game recap (600–1200 words) using the BSI voice + anti-fabrication protocol. For deeper post-game treatment than the 30-minute /gameday-recap.
---

# /recap-draft

Long-form recap draft.

## Usage

```
/recap-draft game=<game-id>
/recap-draft team=TEX opponent=LSU date=2026-04-12
/recap-draft last-series team=DBU
```

## What it does

1. Pulls `bsi_get_match_detail` + historical context via `bsi_get_team_schedule`.
2. Applies the `bsi-voice-guide` tone: 1–3 sentence paragraphs, no hedging filler, specific details up top.
3. Runs the `anti-fabrication-protocol` pre-publish checklist on every draft claim.
4. Produces a draft with structure:
   - **Headline** — no clickbait, no invented drama.
   - **Cold-open scene** — specific detail from the game.
   - **Nut graf** — what the game means beyond itself.
   - **Turning point** — the single inning/drive/possession that decided it.
   - **Hero** — one player. With real stats, no fabricated narrative.
   - **Question** — what does this mean going forward?
   - **Stat block** — advanced metrics with sources + timestamps.

## Differs from `/gameday-recap`

| | `/gameday-recap` | `/recap-draft` |
|---|---|---|
| Word count | 150–300 | 600–1200 |
| Turnaround | 30 min | 2–4 hours |
| Depth | headline + bullets | full narrative |
| Plugin | gameday-ops | editorial-desk |

## Rules

- If the MCP doesn't return play-by-play rich enough to identify the turning point, the draft says so — does not invent.
- No quotes unless the source material contains the exact quoted text.
- Advanced metrics stabilize at different sample sizes — small samples flagged in prose.
- Opponent framing is honest — no homerism for the root team.
