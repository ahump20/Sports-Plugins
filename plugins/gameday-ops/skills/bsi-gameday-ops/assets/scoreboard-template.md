# Scoreboard Output Template

```
[TIME CT] LIVE SCOREBOARD — [N] games in progress

LIVE  [Away] @ [Home] — [Score] | [Inning/Status]
      [One-line context: ranked matchup, conference implications, notable streak]

LIVE  [Away] @ [Home] — [Score] | [Inning/Status]
      [Context]

[Repeat for all in-progress games]

SUMMARY  [N] games final | [N] games upcoming today
Data via BSI scoreboard as of [HH:MM CT]
```

## Rules
- Status prefix: `LIVE` = in progress, `FINAL` = game ended, `SCHED` = upcoming today
- Flag ranked teams with their rank: "#4 Tennessee"
- One-line context per game — not a paragraph
- Group by conference if conference filter was applied
- Always end with source + timestamp from meta.fetched_at
- No emoji — text status prefixes only
