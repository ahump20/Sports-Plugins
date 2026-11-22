# League snapshot

Supply one UTF-8 JSON object. Every field below is required. Unknown fields, duplicate keys, nonfinite numbers, numeric strings and booleans in integer fields produce an error. The [synthetic example](../examples/league.json) is a complete input.

## Scope and coverage

| Field | Value |
|---|---|
| `league`, `season` | Nonempty, single-line strings identifying one league and one regular season. |
| `source` | Single-line source attribution, such as the export URL or a dated commissioner-provided standings and schedule file. |
| `as_of` | Observation timestamp with seconds and UTC offset, such as `2026-11-01T12:00:00Z` or `2026-11-01T06:00:00-06:00`. Up to six fractional second digits are supported. |
| `completed_week` | Integer from zero through `regular_season_weeks`. Records include only games through this fully completed week. Zero denotes preseason. |
| `regular_season_weeks` | Positive integer giving the final regular-season week, counting from week 1. |
| `remaining_schedule_complete` | Boolean `true`, explicitly attesting that the supplied games cover every remaining matchup in this league and season. |
| `teams`, `remaining_games`, `settings` | Arrays of team and game objects, and the settings object below. |

Use one appearance per team per week. Byes and different season game totals are supported. For a week in progress, use standings through the preceding week and include every matchup in the current week. A completed matchup in that week can be fixed with a winner constraint if it has a winner. Use a later snapshot for weeks containing an already-final tie. Include only regular-season games that contribute to this standings table.

## Teams and games

Each team supplies `id`, `name`, integer `wins`, `losses`, `ties` and positive integer `season_games`. Use a stable unique ID. Display names may repeat. Records are nonnegative. `season_games` is the team's scheduled game total from the season schedule, including played and remaining games. Supply the actual season total independently of the list being checked. A season with zero games for a team has an undefined final win percentage.

Each remaining game supplies a unique `id`, integer `week` and two distinct team IDs in `home` and `away`. Those labels identify participants and have no effect on ranking. Include an empty array after the final game. All IDs are case-sensitive and match `[A-Za-z0-9][A-Za-z0-9_.:-]*`.

The calculator checks reciprocal league win/loss totals, paired ties and each team's record plus remaining appearances against its season total. For all completed games, decisive games and tied games, it checks whether groups of teams had enough weeks to play the games their records require against one another. It cannot independently verify provider completeness or reconstruct played matchups from aggregate records.

## Qualification rules

| Settings field | Accepted value |
|---|---|
| `playoff_slots` | Integer from 1 through the number of teams, awarding places to the highest seeds. |
| `standings` | `"overall"` for one table with no divisions, group berths or wild-card exceptions. |
| `ranking` | `"win_percentage"`, computed exactly as `(2 × wins + ties) / (2 × games)`. |
| `existing_ties` | `"half_win"` for ties already in the standings. |
| `future_ties` | `"excluded"`, an explicit scenario assumption that each remaining matchup has one winner. |
| `median_games` | `false`, with no extra results against a league median. |
| `tiebreak` | `{"mode":"unresolved"}`, or `{"mode":"fixed_order","order":["TEAM1","TEAM2", ...]}` listing each team exactly once in descending priority. |

Unresolved equal percentages share a rank interval. A group covering seeds 2–4 with two playoff places can send any one member. Each member can qualify, and none has a guaranteed place in that outcome. A declared fixed order settles only equal percentages. Treat that order as a scenario assumption. Dynamic points-for projections, head-to-head tiebreak rules, protected division winners, consolation and bracket reseeding are outside the model.

## Output and constraints

Pass repeatable `--winner GAME=TEAM` arguments to condition the report on named winners. Unknown games, nonparticipants and conflicting winners fail. Each remaining unforced game has two branches. The cap is 16 unforced games, including after winner constraints. Zero unforced games yields one outcome.

JSON retains league, season, source, as-of time, scope and settings. It includes remaining and unforced game counts, a `forced_winners` map and a `scenarios` denominator. Each team row reports its ID, name, best/worst seed and both qualification counts. Guaranteed counts outcomes in which the team earns a place under every permitted tiebreak. Possible counts those in which at least one permitted tiebreak grants it a place. The possible count includes the guaranteed count. Neither count weights a matchup or treats tiebreak orders as additional scenarios.

A team is `clinched` when its guaranteed count equals the denominator, `eliminated` when its possible count is zero and `alive` otherwise. Status applies only to this input and its declared assumptions. Write `--output PATH` to save the selected format. Successful output replaces an existing regular report file atomically. Input aliases, output symlinks and non-regular output paths are rejected. Exit 0 indicates success and exit 2 indicates invalid input, options or a file error.
