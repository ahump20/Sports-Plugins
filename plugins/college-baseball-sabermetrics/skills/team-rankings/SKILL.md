---
name: rankings
description: Display college baseball rankings with advanced metrics — national Top 25, conference standings, and category leaders
argument-hint: <conference|national> [category]
allowed-tools: [Read, Bash, Grep]
---

# College Baseball Rankings

Displays college baseball rankings with advanced sabermetric context.

## Arguments

The user invoked this with: $ARGUMENTS

Expected format: `/rankings <scope> [category]`

- `scope` — Required. A conference name (`big-12`, `sec`, `acc`, `pac-12`, `big-ten`) or `national` / `top-25`
- `category` — Optional. Filter by: `hitting`, `pitching`, `overall`, `rpi`

## Instructions

When this command is invoked:

1. Parse the scope (conference or national)
2. Parse the optional category filter
3. Retrieve rankings data from the Blaze Sports Intel MCP server: `bsi_get_rankings` for the national Top 25, `bsi_get_standings conference={conference}` for conference tables. No tool returns category leaderboards; for a category filter, rank only what can be computed from the returned standings or pulled player stats, and say so
4. Format as a readable rankings table

## Output Format

### National Top 25
```
⚾ NCAA Baseball Top 25 — Week 12

 Rk  Team                  Record   Conf     wOBA    FIP    RPI
 ──  ────────────────────  ───────  ───────  ─────  ─────  ─────
  1  Texas Longhorns       38-8     18-3     .371   3.12   .628
  2  LSU Tigers            36-10    16-5     .365   3.28   .621
  3  Wake Forest Deacons   37-9     18-3     .358   2.95   .615
  4  Tennessee Volunteers  35-11    14-7     .362   3.05   .612
  5  Stanford Cardinal     34-10    17-4     .355   3.18   .608
  ...
```

### Conference Standings
```
⚾ Big 12 Baseball Standings — 2026

 Rk  Team                  Conf     Overall  wOBA    FIP    SOS
 ──  ────────────────────  ───────  ───────  ─────  ─────  ─────
  1  Texas Longhorns       18-3     38-8     .371   3.12   .582
  2  Oklahoma State        15-6     32-14    .348   3.45   .568
  3  TCU Horned Frogs      14-7     30-16    .342   3.52   .571
  4  Texas Tech            13-8     29-17    .338   3.61   .559
  ...
```

## Conference Aliases

| Input | Conference |
|-------|-----------|
| `big-12`, `big12`, `xii` | Big 12 |
| `sec` | SEC |
| `acc` | ACC |
| `pac-12`, `pac12` | Pac-12 |
| `big-ten`, `big10`, `b1g` | Big Ten |
| `national`, `top-25`, `top25`, `d1` | National rankings |

## Example Usage

```
/rankings national
/rankings big-12
/rankings sec pitching
/rankings top-25 hitting
```
