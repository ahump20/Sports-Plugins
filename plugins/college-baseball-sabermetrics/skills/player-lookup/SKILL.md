---
name: player-lookup
description: This skill should be used when the user asks about a specific college baseball player's stats, performance, scouting report, or draft profile. Retrieves advanced sabermetric data for NCAA Division I baseball players.
version: 1.0.0
---

# Player Lookup

Retrieves and presents advanced sabermetric profiles for NCAA Division I college baseball players.

## When This Skill Applies

This skill activates when the user:
- Names a specific college baseball player
- Asks for a player's stats, numbers, or performance
- Wants a scouting report or player evaluation
- Asks about a team's roster or lineup
- Inquires about draft prospects from college baseball

## Instructions

When this skill is invoked:

1. Identify the player name and team (if provided)
2. Query the college baseball stats MCP endpoint
3. Present a comprehensive player profile including:

### For Position Players
```
Player Profile: [Name] — [Team] ([Conference])
Position: [POS] | Class: [Fr/So/Jr/Sr] | B/T: [L/R]/[L/R]

Traditional Stats
  AVG    OBP    SLG    OPS    HR    RBI    SB
  .312   .405   .521   .926   12    45     8

Advanced Metrics
  wOBA   wRC+   BABIP   ISO    BB%    K%    Barrel%
  .392   142    .335    .209   12.3   18.7  11.2

Batted Ball Profile
  GB%    FB%    LD%    Pull%   Cent%   Oppo%
  42.1   35.8   22.1   38.5    34.2    27.3
```

### For Pitchers
```
Player Profile: [Name] — [Team] ([Conference])
Position: [SP/RP] | Class: [Fr/So/Jr/Sr] | T/B: [L/R]/[L/R]

Traditional Stats
  W-L    ERA    IP      H     BB    K     SV
  8-2    2.85   94.2    72    28    112   0

Advanced Metrics
  FIP    xFIP   WHIP   K/9    BB/9   K/BB   HR/9
  3.12   3.28   1.06   10.7   2.7    4.0    0.76

Pitch Mix & Command
  CSW%   Whiff%   Zone%   1st-Strike%
  31.2   27.8     48.5    62.3

Pitch Arsenal
  Fastball  92-95 mph   45%   28% Whiff
  Slider    83-86 mph   30%   35% Whiff
  Changeup  84-86 mph   25%   22% Whiff
```

4. Add contextual notes:
   - Conference strength context
   - Sample size caveats for early-season data
   - Comparison to conference and national averages
   - Notable trends (hot/cold streaks, platoon splits)

## Player Search

If the exact player cannot be found:
- Suggest closest name matches
- Ask the user to clarify the team or conference
- Check common name variations and nicknames

## Data Sources

Player data is sourced from the college-baseball-stats MCP endpoint backed by Blaze Sports Intel analytics.
