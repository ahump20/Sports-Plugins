---
name: playoff-scenarios
description: Calculate playoff paths from a supplied single-table head-to-head league snapshot. Use for clinch and elimination questions, attainable seed ranges, cutoff ties, or testing what changes if a particular team wins.
---

# Playoff scenarios

1. Take standings, remaining regular-season matchups, calendar, league rules and attribution from the user's snapshot or authorized export. Use the same league, season and completed-week boundary throughout. Keep the observation time and source attached.
2. Build the input using the [contract](references/input-contract.md). Confirm how slots are awarded, how records are ranked and that each team has all its remaining games. Ask for missing facts. If divisions, median games or another unsupported rule changes qualification, explain which rule prevents the calculation.
3. Use unresolved ties when the league's final equal-percentage ordering is undetermined. A fixed order requires the user's complete, explicitly hypothetical priority list. Current points for and provider defaults cannot supply that order. Declare the win/loss-only assumption for future games.
4. From this skill directory run `python3 scripts/playoff_scenarios.py --input league.json --format markdown`. Use `--format json` for structured results. Apply `--winner GAME=TEAM` for each requested condition. Run the unconstrained and conditioned cases separately when comparing paths. If more than 16 games remain open, ask which outcomes the user wants to condition on.
5. Give the best and worst regular-season seeds, both qualification counts and the denominator. Explain any gap using the cutoff tie. State the source, as-of time, forced winners and tiebreak assumption alongside any clinch claim. Count every distinct outcome once. Use “in 3 of 4 schedules” when describing the share.

Try the [synthetic league](examples/league.json) locally. Replace it with attributed observations for any real standings report.
