---
name: trade-analyzer
description: Use when the task involves analyzing a fantasy sports trade offer, comparing player values, recommending a counter-offer, or building a trade proposal to target a specific player. Covers NFL, MLB, NBA, dynasty, and redraft formats.
---

# Trade Analyzer

Use this skill when quality depends on giving the user a specific, honest read on whether a trade is fair, who wins it, and what to do next. Vague "it depends" analysis is not useful. The user needs a clear recommendation with reasoning.

## Working Model

Before analyzing any trade, establish:

- **Format**: Redraft, keeper, or dynasty? This changes value dramatically.
- **Scoring**: PPR, standard, half-PPR? Custom scoring changes positional values.
- **Week / timing**: How far into the season? Playoff implications?
- **Your roster**: What positions are you stacked at? Where do you need help?
- **Your record**: Win-now (4-1, playoff lock) vs. rebuild (1-5, season over)?
- **The full trade**: All players going both ways — don't analyze partial trades.

A trade that is even in raw player value can still be wrong for a specific team at a specific time.

## Trade Value Framework

### Player value components

| Component | Weight | Notes |
|-----------|--------|-------|
| Current production | 40% | Recent performance over last 4 weeks |
| Projected remaining value | 35% | Target share, snap %, usage trends |
| Schedule | 15% | Remaining opponent strength |
| Injury/risk | 10% | Availability and durability concerns |

For dynasty: shift weight toward age and long-term projected value. Discount for players over 28 in skill positions.

### Position value tiers (NFL PPR, redraft)

Tier system for quick comparison:
- **Tier 1**: Elite starters, top-6 overall production
- **Tier 2**: Solid starters, top 12–18 at position
- **Tier 3**: Streamable starters, positional matchup plays
- **Tier 4**: Handcuffs, fliers, depth pieces

A Tier 1 for a Tier 2 + Tier 3 is approximately even in raw player value. A Tier 1 for two Tier 3s likely favors the Tier 1 side in redraft, but may favor the other side in dynasty.

## Trade Analysis Output Format

```
Trade Analysis: [Your Name]

GIVING UP: [Player(s)] — [Value tier, recent stats, position rank]
GETTING:   [Player(s)] — [Value tier, recent stats, position rank]

RAW VALUE: [Slight edge to you / Even / Slight edge to them / Clear winner]

CONTEXT:
- Your roster need: [One sentence]
- Their roster need: [One sentence]
- Schedule: [Any relevant schedule consideration]

VERDICT: [Accept / Counter / Decline]

REASONING: [2–3 sentences explaining the verdict]

COUNTER (if applicable): [Specific counter-offer suggestion]
```

Never use "it depends" as the verdict. Always reach a conclusion.

## Win-Now vs. Rebuild Framing

When the user is 4-1 and competing for a playoff spot:
- Prioritize floor and availability over ceiling.
- A reliable Tier 2 starter is better than an injured Tier 1.
- Avoid trading away depth — injuries happen in playoff runs.

When the user is 1-5 and out of playoff contention:
- Maximize future value (dynasty) or target breakout candidates with high upside.
- Sell aging veterans who are Tier 1 now but declining.
- Accept a talent downgrade in the short term for a roster upgrade in draft capital or youth.

State the win-now or rebuild framing explicitly at the top of any analysis.

## Dynasty Trade Considerations

Additional factors for dynasty leagues:

- **Age curve**: WR peaks 24–28; RB peaks 22–26; QB peaks 26–32.
- **Draft capital value**: A first-round pick is worth a Tier 2 player expected to finish in the top 12.
- **Positional age premiums**: A 24-year-old RB is worth significantly more than the same talent at 29.
- **Contract years**: In keeper leagues, track how many years remain on each player's deal.

Dynasty aging adjustment: reduce value of players 28+ at RB and WR by one tier per season beyond 28.

## Veto and Fair Trade Standards

When asked if a trade will be vetoed in a league:
- Most leagues do not allow vetoes for lopsided trades — only collusion.
- A trade is "lopsided" if the value difference exceeds two full tiers at multiple positions.
- Do not recommend vetoing a trade just because one manager made a bad deal — that's their right.

When asked if a trade is "fair":
- Fair means within one tier of equivalent value adjusted for context.
- Label trades honestly: "This trade favors the other manager slightly" is useful; "This trade is fine" is not.

## Hard Rules

- Never give a verdict without seeing the full trade (all players on both sides).
- Never analyze a trade without knowing the scoring format.
- Never recommend accepting a trade that significantly weakens the user's weakest roster position.
- Always state the week and playoff implications — they change the calculus.
- Always provide a counter-offer if the verdict is "Counter" — a counter without a specific suggestion is not useful.
- Do not use "block-buster" or "steal" language unless the trade is genuinely extreme — calibrate language to the actual value gap.
