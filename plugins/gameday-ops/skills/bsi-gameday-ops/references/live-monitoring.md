# Live Monitoring — National Slate

Monitor scores and status across the full national slate. This is the default
mode when Austin says "what's happening tonight" or "check the scores."

---

## Workflow

1. Call `bsi_get_scoreboard` (no conference filter → full national view)
2. Categorize games by status: `pre`, `in`, `post`
3. Flag: ranked matchups, conference race implications, upset alerts, no-hitters
4. Format using `assets/scoreboard-template.md`
5. Include source and timestamp from `meta.fetched_at`

## Conference filter

If the ask is conference-specific ("SEC scores", "ACC games tonight"):
- Add `conference` parameter to scoreboard call
- Pull `bsi_get_standings` for that conference to add race context

## What to flag

- **Ranked matchups**: Any game with a Top 25 team
- **Upset alerts**: Unranked team leading a ranked team in late innings
- **Conference race**: Game between teams separated by ≤2 games in standings
- **Milestones**: No-hitters in progress, record-breaking performances
- **BSI editorial hooks**: Mid-major program making noise (this IS the BSI differentiator)

## Refresh cadence

- Don't proactively refresh unless in a DSWT sprint
- On request, re-call scoreboard (60s cache means data is always near-fresh)
- If multiple requests within 60s, report cached status and note the TTL

## Multi-sport awareness

If games from multiple sports are live simultaneously, use `get_live_games`
(Blaze Intelligence) for the cross-sport view, then drill into college baseball
via `bsi_get_scoreboard` for detail.
