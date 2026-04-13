# Single Game Focus

Deep tracking of one specific game. This is the mode when Austin says
"follow the Texas game" or "what's happening in the LSU-Tennessee game."

---

## Workflow

1. Call `bsi_get_scoreboard` to find the game and get its `matchId`
2. Call `bsi_get_match_detail` with the matchId for play-by-play
3. Optionally call `bsi_get_team_sabermetrics` for both teams (pre-game context)
4. Format using `assets/game-focus-template.md`
5. Include source and timestamp

## Finding the matchId

The scoreboard returns game objects. Each has an ID field (Highlightly ID).
Search the results by team name to find the right game. If the game isn't
in today's scoreboard, try passing a specific `date` parameter.

## Update cycle

Each update request:
1. Re-call `bsi_get_match_detail` (2-min cache)
2. Compare to previous state — report what changed
3. Flag pitching changes, scoring plays, leverage shifts
4. If game goes final mid-tracking, switch to post-game-recap workflow

## Enrichment (don't delay the score)

After the core score/situation is reported, layer in:
- **Standings implications**: "A Texas win would move them to 2nd in the SEC"
- **Pitcher context**: "Starter has thrown 95 pitches through 6 — bullpen territory"
- **Historical pattern**: From training data, flagged as such
- **Win probability**: From `predict_game_outcome` (Blaze Intelligence)

## Play-by-play notes

- Match detail caps play-by-play at 50 events
- Events are ordered chronologically
- Focus on scoring plays, pitching changes, and high-leverage at-bats
- Don't narrate every play — summarize between key moments
