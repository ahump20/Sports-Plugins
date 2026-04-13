---
name: waiver-wire
description: Use when the task involves ranking waiver wire pickups, recommending streaming options, advising add/drop decisions, or building a weekly priority list for a fantasy sports league.
---

# Waiver Wire

Use this skill when quality depends on giving specific, ranked pickup recommendations with clear rationale — not a list of names copied from a consensus ranking. The user needs to know who to add, who to drop, and why, for their specific roster situation.

## Working Model

Before building any waiver recommendation, establish:

- **Sport and week**: NFL week 9? MLB final stretch? NBA mid-December?
- **Scoring format**: Standard, PPR, roto, H2H categories?
- **Waiver type**: Rolling, FAAB (budget), or priority-based?
- **User's roster**: What positions are they stacked at? Where is the hole?
- **Available players**: What is actually on the waiver wire? (Context matters — do not recommend players who are rostered in standard leagues.)
- **Opponent this week**: Does a streaming matchup matter for this week specifically?

Never give generic "top waiver adds" without the user's roster situation. A wide receiver add is wrong if they already have five WRs and no RB depth.

## Waiver Priority Framework

Rank available players by:

1. **Opportunity score**: Projected snaps / targets / touches / plate appearances based on current depth chart.
2. **Productivity trend**: Last 4-week average vs. season average — is it trending up or down?
3. **Matchup this week**: Favorable or unfavorable opponent?
4. **Injury buffer**: Does adding this player hedge against a current injury risk on the user's roster?
5. **Roster fit**: Does the player fill a need or add to a surplus?

Weight opportunity score highest. A player with 8 targets per game on a bad offense is more valuable than a player with 4 targets per game on a great offense.

## Output Format

```
Waiver Wire Recommendations — Week [X] | [Scoring Format]

Priority 1: [Name], [POS], [Team]
  Opportunity: [One sentence on target/touch/snap share]
  Matchup: [One sentence on this week's opponent]
  Drop: [Name, POS] — [One sentence why they're the drop]

Priority 2: [Name], [POS], [Team]
  Opportunity: [One sentence]
  Matchup: [One sentence]
  Drop: [Name, POS] — [One sentence]

Priority 3 (if FAAB): Spend $X / $[total budget] — [reason for bid amount]

Streaming adds (1-week play):
  [Name], [POS] vs. [Opp] — [One sentence on why this week only]
```

Keep each recommendation to four lines max. Do not pad with generic scouting commentary.

## NFL Waiver Specifics

### RB add triggers
- Starter injury or suspension: Add the handcuff immediately, regardless of season-long upside.
- Usage spike (15+ touches) in last two weeks with no clear reason to regress: add.
- Backfield committee breakup: one back emerging with 60%+ snap share.

### WR add triggers
- Target share spike (25%+ of team targets for 2+ weeks) without clear explanation.
- WR1 injury: slot/possession receiver moves into WR2 role with increased snap share.
- Return from injury by a WR who was a WR1 before going down.

### TE streaming
- Target in favorable matchups: teams allowing top-5 TE numbers in yardage and TD rate.
- Red zone target share: TEs with 2+ red zone targets per game are streaming-viable regardless of overall target share.

## MLB Waiver Specifics

### Streaming SP triggers
- Favorable matchup (opponent K rate > 22%, wRC+ < 90) + SP with K% > 22%.
- Pitcher recently activated from IL with intact skills (K%, BB%, HR% within career range).
- Spot start against a bottom-5 offense in runs scored.

### Hitting add triggers
- Promotion from minors with minor-league OPS > .850 and confirmed everyday role.
- Platoon breakout: one side of a platoon getting the bulk of reps due to injury.
- Batting order promotion to top 3 for a player with power (ISO > .180).

## FAAB Bidding Strategy

FAAB (Free Agent Acquisition Budget) tips:

- **Normal week**: Spend proportionally. If a player has 10% of season value remaining, bid up to 10% of remaining FAAB.
- **Injury replacement for a star**: Bid aggressively (30–50% of remaining budget) on the clear handcuff.
- **Speculative add**: Never bid more than 5% on a "wait and see" situation.
- **End of season**: Loosen the budget — FAAB doesn't carry over; spend it on playoff weeks.

### Bid estimation formula

```
Bid = (Player's projected remaining fantasy points / Average points per roster spot) × Remaining FAAB
```

Simplification: if a player projects to be in the top 12 at their position for the rest of the season, bid 15–25% of remaining budget in a competitive league.

## Hard Rules

- Never recommend adding a player without specifying who to drop.
- Never give waiver recommendations without knowing the scoring format.
- Never rank a player in the top 3 adds based on one week of data — require a 2-week trend minimum for non-injury situations.
- Always note when a recommendation is a 1-week streaming play vs. a season-long add.
- Always state the remaining FAAB budget (if known) before giving bid recommendations.
- Do not recommend an add if the player is rostered in more than 50% of standard leagues — they are not a waiver pickup.
