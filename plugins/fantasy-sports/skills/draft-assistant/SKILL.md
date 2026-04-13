---
name: draft-assistant
description: Use when the task involves planning a fantasy sports draft, analyzing draft position strategy, identifying sleepers, or evaluating ADP vs. projected value discrepancies across NFL, MLB, NBA, or DFS formats.
---

# Draft Assistant

Use this skill when quality depends on giving a fantasy player an analytically grounded draft strategy that goes beyond "draft the best player available." Good draft advice is specific to the user's position, scoring format, roster requirements, and risk tolerance.

## Working Model

Before building a draft plan, establish:

- **Sport and format**: NFL, MLB, NBA? Snake, auction, or DFS?
- **Scoring format**: Standard, PPR, half-PPR, or custom?
- **League size**: 8, 10, 12, 14 teams?
- **Roster requirements**: How many RB/WR/TE/flex spots? Any superflex?
- **Draft position**: Early (1–3), middle (4–8), or late (9–12)?
- **Strategy orientation**: Win-now or rebuild?

Strategy is dependent on all six. A 12-team PPR superflex late-pick plan is entirely different from a 10-team standard early-pick plan.

## Positional Scarcity Framework

Scarcity drives draft value. Rank positions by depth falloff:

### NFL (PPR, 12-team)

```
Round 1:     Elite RB1 or WR1 (top ~8 exist; scarcity is real)
Rounds 2–3:  Fill second elite RB/WR; address TE1 if elite TE is available
Rounds 4–5:  QB1 (unless superflex — QB goes earlier); RB2/WR2
Rounds 6–8:  WR depth, flex options, handcuffs for elite RBs
Rounds 9–11: Streaming DST, K, TE2 — positional value exhausted here
```

Positional tiers (PPR, standard league):
- **QB**: Positional advantage narrows after top 3; don't reach before round 6 in 1-QB formats.
- **RB**: Deepest positional scarcity at the top. Top 8 RBs have a major advantage over the next 8.
- **WR**: Deepest pool — good WR3/WR4 options available in rounds 8–10. Don't overweight early.
- **TE**: Top 2 TEs (TE1 elite) are weekly advantages; after them, streaming is viable. Target round 4–5 or round 10+.

### MLB (roto, 12-team, 5×5)

```
Category coverage by round:
  R1–R2:   SP aces (ERA, WHIP, K leaders)
  R3–R4:   Corner power bats (HR, RBI)
  R5–R6:   Second elite SP; middle infield (SB if available)
  R7–R10:  Balance remaining categories; fill SB, AVG, Saves
  R11+:    Upside plays, closer handcuffs, platoon bats
```

5×5 roto tip: Saves are the hardest category to buy late in a draft. If you miss the elite closers, you'll be streaming or trading all season. Target one in the first 8 rounds or go punt-saves and make it up in ratios.

## ADP vs. Value Analysis

ADP (average draft position) represents consensus value. Beat consensus by finding:

1. **Positive variance plays**: Players with better projected outlooks than their ADP reflects.
2. **Negative variance plays to avoid**: Players being drafted higher than their true ceiling.
3. **Schedule-based value**: Players with easy early schedules tend to outperform in weeks 1–6.

When comparing a player to ADP:
- Calculate expected value over their likely replacement at that pick position.
- Use position rank delta: "If Smith goes 24th overall as a WR11, the next WR at comparable ADP is a WR15 at pick 36 — that's a 12-pick value gap."
- Never cite just raw ADP without the positional rank translation.

## Sleeper Identification

Sleeper criteria (all three must apply):

1. **Situation change**: New team, depth chart promotion, injury to starter, scheme change, or offensive line upgrade.
2. **Opportunity signal**: Snap share, target share, or touch data showing path to starter-level work.
3. **ADP undervalue**: Currently being drafted later than their projected opportunity warrants.

```
Output format for a sleeper recommendation:
[Name], [POS], [Team] — ADP: Round X
Why sleeper: [One sentence on the situation change]
Opportunity: [One sentence on the volume path]
Risk: [One sentence on what could prevent the opportunity]
Best-case: [One sentence on the ceiling]
```

A player with a good story but no opportunity signal is a narrative play, not a sleeper. Label them accordingly.

## Draft Position Strategy Templates

### Early pick (1–3, 12-team PPR)

1. Take the best RB or WR available — no reaching for positional need.
2. Your second pick (late round 2 on the turn) fills the other elite slot.
3. Plan to miss QB entirely in rounds 1–4 and target value in round 5–6.
4. Build RB depth aggressively in rounds 3–5 — the position thins fastest.

### Middle pick (5–8, 12-team PPR)

1. Avoid the RB rush — if top 6 RBs are gone, shift to WR and accumulate at RB later.
2. The "zero-RB" strategy is viable here: load WRs through round 4, then target high-upside RBs in rounds 5–7.
3. Target an elite TE in rounds 3–4 if available — positional advantage compounds.

### Late pick (9–12, 12-team PPR)

1. Positional runs will happen before your picks — plan around them.
2. Take advantage of the turn (two picks in a row) to roster positions that are thinning.
3. Late picks often produce deep-value WRs and handcuffs — prioritize upside over floor.
4. Target a top-5 QB in round 4–5 if superflex — the value window is short.

## Hard Rules

- Never recommend drafting a player without stating their ADP and position rank.
- Never give a sleeper recommendation without an explicit opportunity signal.
- Never give generic "best player available" advice without positional context.
- Always state the scoring format and league size the strategy applies to.
- When recommending a pick over an alternative, always state what the user is giving up at the next pick.
- Do not recommend a kicker, DST, or bench stash before round 9 in standard formats.
