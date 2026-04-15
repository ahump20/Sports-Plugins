---
name: squad
description: Build and optimize a Diamond Dynasty squad within a budget, position requirements, and collection goals
argument-hint: <budget> [position|theme]
allowed-tools: [Read, Bash, Grep]
---

# Squad Builder

Builds and optimizes Diamond Dynasty lineups within budget and positional constraints.

## Arguments

The user invoked this with: $ARGUMENTS

Expected format: `/squad <budget> [position|theme]`

- `budget` — Required. Budget in stubs, e.g. `100k`, `500000`, `1m`
- `position|theme` — Optional. Filter by position (`SP`, `C`, `OF`) or theme (`power`, `speed`, `budget`, `meta`)

## Instructions

When this command is invoked:

1. Parse the budget (convert `k` = ×1,000, `m` = ×1,000,000)
2. Parse the optional filter (position group or build theme)
3. Generate an optimized lineup maximizing overall value within budget

## Output Format

```
💎 Diamond Dynasty Squad — 100k Budget

  Pos  Player              OVR   Series      Price    Value*
  ───  ──────────────────  ────  ──────────  ───────  ──────
  C    [Player]            92💎  Flashback   15,200   A
  1B   [Player]            89💎  Live        22,100   A+
  2B   [Player]            87💎  Awards      8,500    S
  SS   [Player]            91💎  Live        18,900   A
  3B   [Player]            85💎  Prospect    5,200    S
  LF   [Player]            88💎  Live        12,400   A
  CF   [Player]            86💎  Program     Free     S+
  RF   [Player]            84🥇  Live        2,800    S
  DH   [Player]            90💎  Milestone   14,200   A

  ──────────────────────────────────────────────────
  Total:   99,300 / 100,000 stubs
  Avg OVR: 88.0
  Remaining: 700 stubs

  *Value Rating: S+ (elite value), S (great), A+ (good), A (fair)

  Bench:
  • [Player] — 83🥇 Utility, Free (program reward)
  • [Player] — 82🥇 OF/1B, 1,500 stubs

  Starting Rotation:
  SP1  [Player]  94💎  Free (program)
  SP2  [Player]  89💎  18,000
  SP3  [Player]  87💎  8,200
  SP4  [Player]  85💎  4,100
  SP5  [Player]  84🥇  2,500

  Bullpen:
  CP   [Player]  91💎  Free (collection)
  SU   [Player]  87💎  6,500
```

## Build Themes

| Theme | Strategy |
|-------|----------|
| `meta` | Best competitive cards regardless of price distribution |
| `budget` | Maximum value from low-cost cards; prioritise free program rewards |
| `power` | Maximise HR potential; high Power R/L attributes |
| `speed` | Fast lineup; high Speed + Stealing attributes |
| `contact` | High Contact R/L for consistent hitting |

## Example Usage

```
/squad 100k
/squad 500k meta
/squad 50k budget
/squad 1m best-available SP
```
