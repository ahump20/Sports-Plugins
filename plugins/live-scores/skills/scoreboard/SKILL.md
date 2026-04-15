---
name: scoreboard
description: Display a formatted multi-game scoreboard for a specified sport or league
argument-hint: <sport> [date]
allowed-tools: [Read, Bash, Grep]
---

# Scoreboard Command

Displays a formatted scoreboard showing all games for a specified sport.

## Arguments

The user invoked this with: $ARGUMENTS

Expected format: `/scoreboard <sport> [date]`

- `sport` — Required. One of: `mlb`, `nfl`, `nba`, `college-baseball`, `college-football`
- `date` — Optional. Date string like `today`, `yesterday`, `2026-04-13`

## Instructions

When this command is invoked:

1. Parse the sport argument to determine which league to query
2. Parse the optional date argument (default to today)
3. Retrieve all games for that sport on the specified date
4. Format as a clean, readable scoreboard

## Output Format

```
╔══════════════════════════════════════╗
║     ⚾ College Baseball — Apr 13     ║
╠══════════════════════════════════════╣
║  #1 Texas        7   Final          ║
║     Oklahoma St  3                  ║
║──────────────────────────────────────║
║  #5 LSU          4   Bot 8th        ║
║  #12 Vanderbilt  6                  ║
║──────────────────────────────────────║
║     Baylor       2   7:00 PM CT     ║
║     TCU          -   Scheduled      ║
╚══════════════════════════════════════╝
```

## Sport Aliases

Accept common abbreviations:
- `mlb`, `baseball` → Major League Baseball
- `nfl`, `football` → National Football League
- `nba`, `basketball` → National Basketball Association
- `cbb`, `college-baseball` → NCAA Baseball
- `cfb`, `college-football` → NCAA Football

## Example Usage

```
/scoreboard mlb
/scoreboard college-baseball yesterday
/scoreboard nfl 2026-10-15
```
