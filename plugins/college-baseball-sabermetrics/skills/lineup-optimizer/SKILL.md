---
name: lineup-optimizer
description: Use when the task involves constructing or optimizing a college baseball batting order, evaluating lineup balance, building platoon splits for lineup decisions, or generating a lineup card with sabermetric rationale.
---

# Lineup Optimizer

Use this skill when the goal is to produce an analytically grounded batting order recommendation or evaluate an existing lineup's structural strengths and weaknesses. The output should be directly useful to a coaching staff or a content team building a pre-series analysis piece.

## Working Model

Before building or evaluating a lineup, establish:

- **Roster context**: Who is available? Injury, eligibility, or academic status?
- **Opponent starter**: LHP or RHP? Pitch mix tendencies?
- **Home or away**: Does park factor or conditions affect the approach?
- **Game importance**: Regular season midweek, Big 12 weekend series, regional/super regional, or CWS?

Lineup decisions are context-specific. The optimal order for Friday's lights-out RHP is not the same as for Sunday's lefty with a low K rate.

## Lineup Construction Framework

### Role-Based Slot Philosophy

| Slot | Primary Job | Desired Profile |
|------|------------|-----------------|
| 1 | Get on base, set the table | High OBP (.380+), K rate < 20%, speed |
| 2 | Advance runners, make contact | Best bat control, OBP + contact; can have power |
| 3 | Drive in runs, best overall hitter | Highest wRC+, solid OBP, gap-to-gap power |
| 4 | Drive in runs, most power | ISO > .200, walks, does not need speed |
| 5 | Secondary run producer | ISO > .160, walks, protects the 4-hole |
| 6 | Contact, depth | OBP-oriented, low strikeout rate |
| 7 | Balance or platoon advantage | Matchup-dependent |
| 8 | Weakest bat on the day | Minimize exposure, get on base to lead off next inning |
| 9 | Varies by philosophy | Traditional: weakest bat. Modern: second leadoff type with OBP |

### Slot 9 Philosophy Choice

- **Traditional**: Pitcher hits ninth (JUCO/NAIA rules), or weakest bat ninth to keep the bottom of the order from clogging bases in front of the top.
- **Modern/Sabermetric**: High-OBP bat ninth so the lineup cycles — 9 gets on, 1 and 2 drive him in to open the next frame.

Recommend the modern approach when the team has a capable OBP bat with modest power stuck outside the top 6. Flag if the coach has historically preferred traditional construction.

## wOBA-Based Slot Assignment

When wOBA data is available, sort players by wOBA descending. Then apply these adjustments:

1. Move your highest OBP + speed player to the leadoff slot regardless of raw wOBA rank.
2. Move your highest ISO player to 3-4 unless contact rate is extremely low (K% > 30%).
3. Protect your best hitter (slot 3) with the second-best offensive player (slot 4).
4. Do not bury a high-OBP, low-power player lower than slot 6 — wasted table-setting.

## Platoon Splits and Lineup Adjustments

When facing a LHP starter:

- Prefer right-handed hitters in slots 1–5 where possible.
- Look for RHH with a strong platoon split (wOBA vs. LHP > .020 above overall wOBA).
- Consider sitting left-handed hitters with poor LHP splits (.240 wOBA vs. LHP) in favor of RHH backups.

When facing a RHP starter:

- Left-handed hitters with strong platoon splits move up.
- Evaluate whether any platoon-specific bats justify a start over everyday players.

Minimum threshold to make a platoon start decision: 50 career PA vs. that handedness, or a clear historical trend across two seasons.

## Lineup Card Output Format

When generating a lineup card recommendation, use this structure:

```
Lineup vs. [Opponent], [Date], [LHP/RHP: Starter Name]

1. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
2. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
3. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
4. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
5. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
6. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
7. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
8. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note
9. [Name], [POS], [B/T]  |  OBP .XXX  |  wRC+ XXX  |  Note

SP: [Name], ERA X.XX / FIP X.XX

Rationale: [2–3 sentence explanation of the key slot decisions]
```

Keep the rationale focused on the non-obvious choices — the slot 2 selection, a platoon start, or a modern slot 9 choice. Do not explain every slot.

## Texas Longhorns Lineup Notes

When building or evaluating a UT Austin lineup specifically:

- UT has historically leaned toward contact-oriented leadoff bats rather than pure OBP maximizers — acknowledge if the recommendation diverges from historical tendencies.
- Disch-Falk Field slightly favors hitters; do not over-penalize a slugger for a low walk rate if he is producing consistent hard contact.
- Transfer portal adds in any given season may shift the offensive floor dramatically — verify the current roster before any projection.
- Big 12 weekend competition level requires a full 9-player contribution; avoid single-slot reliance.
- When UT has a clear 3-4 protection pairing, their middle-of-the-order production drives the offensive floor for the season.

## Hard Rules

- Never recommend a lineup without stating the opponent starter's handedness.
- Never build a lineup card from incomplete roster data without flagging the gap.
- Never move a player up in the order based on narrative momentum ("he's been hot") without a supporting wOBA or OBP trend of at least 15 PA.
- Always explain the slot 2 and slot 9 philosophy choices — these are the most debated and require explicit rationale.
- Do not present a lineup as "optimal" — use "recommended given available data" to acknowledge roster and sample limits.
- Always pair lineup recommendations with at least one sentence on expected run-production ceiling and floor for the game.
