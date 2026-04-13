# Leverage Situations

High-stakes in-game moments requiring analytical context. Late innings,
tying run in scoring position, closer entering, conference race on the line.

---

## When this activates

- Late innings (7th+) with a 1-2 run margin
- Tying or go-ahead run in scoring position
- Closer or high-leverage reliever entering
- Conference standings implications on a single outcome
- Postseason bubble team in a must-win

## Workflow

1. Pull current game state from `bsi_get_match_detail`
2. Pull team sabermetrics for both teams (if not already loaded)
3. Optionally pull `predict_game_outcome` for win probability shift
4. Format using `assets/leverage-template.md`

## Context layers

### Situation (from match detail)
- Score, inning, outs, runners (if available in play-by-play)
- Current batter and pitcher (if available)

### Stakes (from standings + rankings)
- What happens to the conference race if Team A wins vs. Team B
- Ranking implications for either team
- Postseason bubble implications

### Historical pattern (from training data — flag as such)
- Base rate: "Teams trailing by 2+ in the 8th win ~18% of the time in D1"
- Bullpen usage: "Team X has used 3 relievers in the last 48 hours"
- Matchup tendency: platoon splits, pitch-type weaknesses (if known)

### What to watch
- Specific: matchup advantage, bullpen availability, platoon split
- Actionable: what the manager's decision reveals about their read

## Speed constraint

This mode lives in the moment. Get the situation out first, then layer context.
Don't hold the report while waiting for the perfect enrichment data.
