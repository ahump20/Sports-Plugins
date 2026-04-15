---
name: recruiting
description: This skill should be used when the user asks about college football recruiting, "top recruits", recruiting class rankings, commitment lists, 5-star prospects, or recruiting grades. Provides NCAA football recruiting intelligence.
version: 1.0.0
---

# Recruiting Intel

Provides college football recruiting intelligence — class rankings, top prospects, commitment tracking, and program evaluation.

## When This Skill Applies

This skill activates when the user:
- Asks about recruiting class rankings
- Wants to know a team's commits or targets
- Asks about specific recruits (star ratings, position, school)
- Discusses recruiting strategy or class composition
- Mentions "5-star", "blue-chip", or "signing day"

## Instructions

When this skill is invoked:

1. Identify the scope — specific team, class year, position, or national overview
2. Retrieve recruiting data
3. Present structured recruiting intelligence:

### Class Rankings
```
🏈 2027 Recruiting Class Rankings — Top 10

 Rk  School              Commits   ★★★★★  ★★★★  Avg★   Points
 ──  ──────────────────  ────────  ─────  ────  ─────  ──────
  1  Texas Longhorns     22        5      12    94.2   312.5
  2  Ohio State          24        4      14    93.8   308.1
  3  Georgia             21        4      11    93.5   295.2
  4  Alabama             23        3      13    93.1   290.8
  ...
```

### Team Commit List
```
🏈 Texas Longhorns — 2027 Class (22 commits)

  Player              Pos   Ht/Wt        Stars  Hometown
  ──────────────────  ────  ───────────  ─────  ──────────────────
  [Name]              QB    6'3" / 215   ★★★★★  Austin, TX
  [Name]              WR    6'1" / 190   ★★★★★  Dallas, TX
  [Name]              EDGE  6'4" / 245   ★★★★★  Houston, TX
  [Name]              OT    6'6" / 305   ★★★★   San Antonio, TX
  ...

  Class Strengths: QB, WR, EDGE
  Remaining Needs: CB, Safety, Interior OL
  Signing Day: December 2026 (early), February 2027
```

4. Include context:
   - National rank trajectory (moving up/down)
   - Position group analysis
   - In-state vs. out-of-state recruiting balance
   - Comparison to rivals' classes
   - Program development impact

## Star Rating Scale

| Rating | Description |
|--------|-------------|
| ★★★★★ | Elite national prospect (top ~30 nationally) |
| ★★★★ | High-level Power 5 starter potential |
| ★★★ | Solid Power 5 contributor / top Group of 5 prospect |
| ★★ | Project / developmental prospect |

## Data Sources

Recruiting data sourced from public recruiting databases and analytics platforms.
