---
name: cfb-rankings
description: Display college football rankings — AP Top 25, CFP rankings, conference standings, and advanced metrics (SP+, FPI)
argument-hint: <conference|ap|cfp> [metric]
allowed-tools: [Read, Bash, Grep]
---

# College Football Rankings

Displays college football rankings with advanced metrics.

## Arguments

The user invoked this with: $ARGUMENTS

Expected format: `/cfb-rankings <scope> [metric]`

- `scope` — Required. One of: `ap`, `cfp`, `big-12`, `sec`, `big-ten`, `acc`, `pac-12`
- `metric` — Optional. One of: `sp+`, `fpi`, `sos`, `overall`

## Instructions

When this command is invoked:

1. Parse the scope and optional metric filter
2. Retrieve rankings data
3. Format as a readable standings table with advanced metrics

## Output Format

### AP Top 25
```
🏈 AP Top 25 — Week 10, 2026

 Rk  Team                  Record   Conf     SP+    FPI    SOS
 ──  ────────────────────  ───────  ───────  ─────  ─────  ─────
  1  Texas Longhorns       9-0      6-0      32.5   28.1   .612
  2  Ohio State Buckeyes   9-0      6-0      31.8   27.5   .598
  3  Georgia Bulldogs      8-1      6-1      30.2   26.8   .625
  4  Oregon Ducks          8-1      6-0      29.5   25.9   .585
  5  Alabama Crimson Tide  8-1      5-1      28.8   25.2   .618
  ...
```

### Conference Standings
```
🏈 Big 12 Standings — 2026

 Rk  Team                  Conf     Overall  SP+    Off    Def
 ──  ────────────────────  ───────  ───────  ─────  ─────  ─────
  1  Texas Longhorns       6-0      9-0      32.5   35.2   -2.8
  2  Oklahoma State        5-1      7-2      18.4   22.1   -3.7
  3  Kansas State          4-2      7-2      15.8   20.3   -4.5
  ...
```

## Conference Aliases

| Input | Conference |
|-------|-----------|
| `big-12`, `big12`, `xii` | Big 12 |
| `sec` | SEC |
| `big-ten`, `big10`, `b1g` | Big Ten |
| `acc` | ACC |
| `pac-12`, `pac12` | Pac-12 |
| `ap`, `ap-top-25` | AP Poll |
| `cfp`, `playoff` | CFP Rankings |

## Example Usage

```
/cfb-rankings ap
/cfb-rankings big-12
/cfb-rankings sec sp+
/cfb-rankings cfp
```
