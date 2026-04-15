---
name: transfer-portal
description: This skill should be used when the user asks about the college football transfer portal, "who entered the portal", player transfers, portal rankings, team portal grades, or transfer impact ratings. Provides real-time transfer portal intelligence for NCAA football.
version: 1.0.0
---

# Transfer Portal Tracker

Tracks college football transfer portal activity — entries, commitments, impact ratings, and team-level portal analysis.

## When This Skill Applies

This skill activates when the user:
- Asks about transfer portal entries or commitments
- Wants to know which players a team gained or lost via portal
- Asks about portal rankings or impact ratings
- Discusses team needs and portal strategy
- Mentions "NIL" in the context of transfer decisions

## Instructions

When this skill is invoked:

1. Identify the scope — specific team, conference, position group, or overall portal
2. Retrieve current portal data
3. Present structured portal intelligence:

### Portal Entry Format
```
🔄 Transfer Portal — Recent Entries

  Player           Pos   From             Stars   Status
  ──────────────   ────  ───────────────  ─────   ─────────
  [Player Name]    QB    Oregon           ★★★★    Committed → Texas
  [Player Name]    WR    Alabama          ★★★★★   In Portal
  [Player Name]    EDGE  Ohio State       ★★★★    Committed → USC
```

### Team Portal Summary
```
🔄 Texas Longhorns — Portal Summary

  Incoming (8):
    QB  [Name] — from Oregon (★★★★, 3200 pass yds)
    WR  [Name] — from USC (★★★★★, 1100 rec yds)
    ...

  Outgoing (5):
    LB  [Name] — to Texas A&M
    ...

  Net Portal Grade: A-
  Biggest Need Filled: QB, WR
  Remaining Needs: CB, OL depth
```

4. Include context:
   - Player's production at previous school
   - Fit analysis for new team
   - NIL market implications (if known)
   - Impact on team's projected win total

## Portal Timeline

- **Portal Window 1:** December (post-season)
- **Portal Window 2:** April (spring portal)
- Outside windows: immediate eligibility waiver cases

## Note

Transfer portal data changes rapidly. Always include a timestamp context and note when data was last updated.
