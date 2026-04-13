# Post-Game Rapid Recap

Game just ended. Turn it around fast. This is NOT an editorial piece — it's a
rapid-fire factual summary with implications. Deep analysis routes back to
the intelligence skills.

---

## Workflow

1. Pull final score from `bsi_get_scoreboard`
2. Pull match detail from `bsi_get_match_detail` for key plays
3. Pull standings from `bsi_get_standings` to show updated conference position
4. Format using `assets/recap-template.md`
5. If it was a ranked matchup, note ranking implications

## What to include

- **The headline**: One sentence — the story of this game, not the score
- **Three facts**: Key stat, pitching line, standings/postseason implication
- **What's next**: Next game in series or next opponent

## What NOT to include

- Deep analytical breakdowns (route to intelligence skills)
- Player profiles or scouting assessments
- Historical comparisons beyond one line of context
- Hot takes or editorial opinions

## Speed target

One tool chain: scoreboard → match detail → standings → output.
Three tool calls maximum for a standard recap. Don't over-research it.

## Special cases

### Ranked team loses
- Note current rank and whether they'll likely drop
- Note the winning team's record and whether they enter the rankings conversation

### Conference race impact
- Show updated standings after the result
- Note games back changes

### Walk-off or dramatic finish
- Lead with the moment, not the final line score
- Include the specific play from match detail
- This is where one line of narrative is allowed before returning to facts

## Handoff

If Austin asks "write a feature about this game" or "deep dive on [player]
from tonight," hand off to:
- `college-baseball-intelligence` (Mode 3: Editorial) for feature writing
- `college-baseball-intelligence` (Mode 2: Analytics) for player analysis
- `texas-longhorns-baseball-intelligence` (Game Breakdown) for Texas depth
