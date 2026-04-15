---
name: card-valuations
description: This skill should be used when the user asks about MLB The Show card prices, Diamond Dynasty market, card values, "how much is", card investments, or attribute upgrades. Provides real-time card pricing and market intelligence for Diamond Dynasty.
version: 1.0.0
---

# Card Valuations

Real-time card pricing, market trends, and investment intelligence for MLB The Show Diamond Dynasty.

## When This Skill Applies

This skill activates when the user:
- Asks how much a specific card costs
- Wants to know best investment picks
- Discusses Diamond Dynasty card market trends
- Asks about upcoming roster updates or attribute changes
- Wants to find undervalued cards

## Instructions

When this skill is invoked:

1. Identify the card(s) or market query
2. Retrieve current pricing data
3. Present structured market intelligence:

### Single Card Valuation
```
💎 Mike Trout — Live Series (97 OVR)

  Buy Now:    125,400 stubs
  Sell Now:    118,200 stubs
  Quicksell:   5,000 stubs

  30-Day Trend: ↗️ +12,500 (+10.5%)
  Supply:       Low (under 50 active sells)

  Key Attributes:
    Contact R: 98  |  Contact L: 95
    Power R:   112 |  Power L:   108
    Speed:     72  |  Fielding:  85

  Investment Rating: ⭐⭐⭐ (Hold)
  — Already near ceiling; sell into hype if 99 OVR confirmed
```

### Market Overview
```
📊 Diamond Dynasty Market — April 2026

  Category         Avg Price   Trend    Hot Cards
  ──────────────   ─────────   ──────   ──────────────
  Live Series 💎   82,500      ↗️ +5%   Ohtani, Judge
  Flashbacks 💎    45,200      ↘️ -3%   —
  Awards 💎        38,100      → Flat   —
  Prospects 🥇     12,400      ↗️ +8%   [Name], [Name]
```

### Investment Picks
```
📈 Top Investment Picks — April Update

  Player          Series    OVR   Price    Projected   ROI
  ──────────────  ────────  ────  ───────  ──────────  ────
  [Player]        Live      84🥇  3,200    → 85💎      +56%
  [Player]        Live      79🥈  1,100    → 80🥇      +354%
  [Player]        Prospect  82🥇  8,500    → 85💎      +488%

  Reasoning: Based on real-world performance trends (wOBA, FIP)
  correlated with historical attribute upgrade patterns.
```

4. Add analytical context:
   - Real-world performance driving potential upgrades (link to sabermetric data)
   - Historical price patterns around roster updates
   - Supply/demand dynamics
   - Collection impact (gate cards vs. non-gate)

## Correlation with Real-World Stats

The most valuable insight this plugin provides is connecting real-world
sabermetric performance to in-game card upgrades. A player whose real FIP
has dropped 0.5+ points since the last update is a strong upgrade candidate.

## Roster Update Schedule

- **Fridays** — Weekly roster updates (attributes, overalls)
- **Monthly** — Major content drops (new programs, flashbacks)
- Attribute changes correlate with 2-week rolling real-world performance
