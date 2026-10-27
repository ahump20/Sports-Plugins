---
name: conference-strength
description: >
  Read conference strength correctly. Build a conference comparison from live
  BSI standings and the national Top 25, interpret cross-conference
  comparisons, and explain why a team's record alone doesn't tell the full
  story. Use when comparing programs across different conferences or when
  doing postseason bracket projection. Pairs with bsi_get_standings and
  bsi_get_rankings from the cbb-sabermetrics plugin.
---

# Conference Strength Index

Not all wins are equal. A 20-5 record in one conference can be a lesser accomplishment than an 18-7 record in another. This skill builds a conference strength read from live standings so cross-conference comparisons mean something.

## What This Index Is

The BSI MCP does not return a conference power index. That route is paused on the server until its source, method, sample boundaries and update metadata are documented. So this skill computes a conference strength read from two tools that do return data, and labels it as computed from standings, never as "the BSI Conference Power Index".

Inputs:
- `bsi_get_standings` (no conference filter): every team's W, L, win pct, runs scored, runs allowed, run differential, streak and games back
- `bsi_get_rankings`: the national Top 25 with rank, record and movement

Computed per conference:
- Combined W-L and win pct across all its teams
- Run differential, total and per game
- Number of teams in the Top 25, and their ranks

What it does not include: strength-of-schedule adjustment, opponent quality ratings, or multi-year postseason weighting. No tool returns those, so don't claim them.

## How To Build It

1. Call `bsi_get_standings` with no conference argument. Each response carries `meta.source`, `meta.fetched_at` and `meta.timezone` (America/Chicago).
2. Call `bsi_get_rankings`.
3. Group teams by conference and compute the three measures above.
4. Rank conferences, leading with ranked-team count and run differential per game, and using win pct as a tiebreaker.

### Reading the Numbers

- **Conference win pct:** in-conference games net to .500 for the conference as a whole, so anything above or below .500 comes from non-conference games. Early in the season (mostly non-conference) it's informative; late in the season it flattens toward .500.
- **Run differential per game:** a less noisy signal than record over small samples. A conference whose teams outscore opponents by more than a run per game is winning its non-conference games convincingly.
- **Top 25 count:** the most direct read of depth at the top. Several ranked teams usually means several tournament-caliber teams.

## Cross-Conference Comparisons

This is where the comparison earns its keep.

### Example: "Is 18-6 in the SEC better than 23-4 in the Sun Belt?"

On record alone: 23-4 wins the .852 vs .750 win percentage comparison.

With conference context from the standings and rankings:
- How many ranked teams each conference has, and whether the 18-6 team played them
- Each conference's run differential per game against the rest of DI
- The team's own run differential and position in its conference standings

If the SEC has many ranked teams and a strong run differential while the Sun Belt has few, the 18-6 record came against tougher opposition. State it that way, with the numbers, rather than converting it into "adjusted wins".

## Postseason Bracket Application

NCAA Tournament selection uses RPI + committee judgment. RPI over-rewards mid-major conference champions and under-rewards second-place teams in deep conferences. The standings-based read gives a corrective lens:

- If a team finishes 4th in a conference with several Top 25 teams and a strong record, they're a real bubble case.
- If a team finishes 1st in a conference with no other ranked teams, they should be the conference's auto-bid but not an at-large consideration.

**Use for:** modeling realistic bracket scenarios that account for conference depth, not RPI surface reads.

## Conference Context Discipline

When writing about a program's record:

1. State the conference's computed measures (ranked-team count, run differential per game) when making cross-conference claims.
2. Never say "they've got the best record in college baseball" without noting who they played.
3. A 22-3 record built against weak conference opponents is not proof of elite quality. A 16-9 record in a deep conference might be.

## Common Mistakes to Avoid

### The "Top Record" Trap
"Team X is 28-3, best in the country!" → Check how many ranked teams their conference has and its run differential per game. If neither is strong, the record may be inflated.

### The "Conference Record" Trap
"Texas is 12-5 in SEC play, that's just middle-of-the-pack" → Middle of a conference with many ranked teams can be more impressive than leading a conference with none. The team's national ranking should reflect conference depth, not just conference position.

### The "Mid-Major Champion" Trap
A mid-major champion going 22-1 in conference is *not* strong evidence of elite quality: they play most of their games against limited competition. Look at their results against ranked opponents in `bsi_get_team_schedule` for a better signal.

## Quality Gates

- Every cross-conference claim cites the computed measures for both conferences.
- Output is labeled as computed from `bsi_get_standings` and `bsi_get_rankings`, with full meta envelope (source, fetched_at).
- No strength-of-schedule adjustment, component score or power index value is claimed.
- Never use RPI as the primary adjustment tool, since RPI has documented biases.

## Example Invocations

A user asks: "Is the ACC or the Big 12 stronger this year?"
1. Call `bsi_get_standings` and `bsi_get_rankings`
2. Compute ACC and Big 12 win pct, run differential per game and Top 25 count
3. Compare all three
4. Return a direct read with the numbers and a one-line analytical call, labeled as computed from standings

A user asks: "Where does Texas rank in real terms given the SEC?"
1. Call `bsi_get_standings` and `bsi_get_rankings` → compute SEC measures and compare with other conferences
2. Call `bsi_get_standings conference=SEC` → find Texas's position
3. Combine: "Texas sits Xth in the SEC, a conference with N Top 25 teams and a +Y run differential per game, so their record reads as [...]."
