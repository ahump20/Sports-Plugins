---
name: roster-optimizer
description: This skill should be used when the user asks about fantasy sports lineups, "should I start", "who should I sit", roster decisions, start/sit advice, lineup optimization, or fantasy player rankings. Provides data-driven roster recommendations.
version: 1.0.0
---

# Roster Optimizer

Provides start/sit recommendations and lineup optimization for fantasy sports.

## When This Skill Applies

This skill activates when the user:
- Asks "should I start X or Y?"
- Needs help setting their fantasy lineup
- Wants start/sit advice for a specific player
- Asks about player rankings for the week
- Discusses fantasy sports roster decisions

## Instructions

When this skill is invoked:

1. Identify the sport (baseball, football, basketball)
2. Identify the scoring format if mentioned (PPR, roto, H2H, etc.)
3. Evaluate the players in question using:

### Evaluation Factors

**Fantasy Baseball**
- Recent performance (last 14 days batting avg, HR, RBI pace)
- Opposing pitcher quality (ERA, FIP, WHIP, handedness)
- Park factor for the game venue
- Platoon splits (batter hand vs. pitcher hand)
- Batting order position and lineup confirmation

**Fantasy Football**
- Target share / snap count trends
- Opposing defense rank vs. position
- Red zone usage and opportunities
- Weather conditions for outdoor games
- Injury report status

**Fantasy Basketball**
- Minutes trend (last 5 games)
- Usage rate and pace of play
- Back-to-back schedule considerations
- Injury report and rest days

4. Present a clear recommendation with reasoning:

```
Start/Sit: [Player Name] — [Team] vs [Opponent]

  Recommendation: ✅ START (Confidence: High)

  Reasons:
  • Hitting .340 over last 14 days with 4 HR
  • Faces a left-handed pitcher (career .380 wOBA vs LHP)
  • Playing at Coors Field (park factor: 1.15)

  Risk Factors:
  • Small sample vs. this specific pitcher (2-for-6)
```

5. When comparing two players, present both profiles side-by-side

## Limitations

- Fantasy advice is probabilistic, not guaranteed
- Always note relevant uncertainty (injury risk, weather, lineup changes)
- Recommend checking final lineup confirmations before game time
