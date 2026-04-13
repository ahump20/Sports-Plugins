---
name: conference-strength
description: >
  Read the BSI Conference Power Index correctly. Interpret strength-of-schedule
  adjusted conference rankings, cross-conference comparisons, and how SOS
  adjustments change the story. Use when comparing programs across different
  conferences, explaining why a team's record alone doesn't tell the full story,
  or when doing postseason bracket projection. Pairs with
  bsi_get_conference_power_index from the cbb-sabermetrics plugin.
---

# Conference Strength Index

Not all wins are equal. A 20-5 record in one conference can be a lesser accomplishment than an 18-7 record in another. This skill reads the BSI Conference Power Index correctly so cross-conference comparisons mean something.

## What the Power Index Is

The BSI Conference Power Index ranks the 32 DI conferences by **strength-of-schedule-adjusted performance**. It's not based on RPI (which has known biases) and it's not pure record (which ignores opponent quality).

Inputs:
- Conference-wide cumulative win percentage in non-conference play
- Average opponent quality per conference
- Conference champion postseason performance (multi-year weighted)
- Conference tournament depth (multiple programs advancing)

Output: a ranked list with `power_index` scores and `rank` position (1-32).

## How To Read It

Call `bsi_get_conference_power_index`. Response shape:

```json
{
  "meta": {
    "source": "BSI Savant",
    "fetched_at": "2026-04-12T14:30:00Z",
    "timezone": "America/Chicago"
  },
  "data": [
    {
      "rank": 1,
      "conference": "SEC",
      "power_index": 104.3,
      "programs": 16,
      "tournament_teams_projected": 11
    },
    ...
  ]
}
```

### Reading the Score

- **Power index > 100:** above-average conference. Top 5 usually.
- **Power index 90–100:** strong conference, sends 4–6 tournament teams
- **Power index 80–90:** mid-tier, 2–4 tournament teams
- **Power index < 80:** conference champion likely the only team in the field

## Cross-Conference Comparisons

This is where the power index earns its keep.

### Example: "Is 18-6 in the SEC better than 23-4 in the Sun Belt?"

Without SOS adjustment: 23-4 wins the .852 vs .750 win percentage comparison.

With SOS adjustment using power index:
- SEC (rank 1, PI 104.3) — every game played against DI top-tier opponents
- Sun Belt (rank 11, PI 87.2) — mixed opponent quality

The 18-6 SEC record represents more adjusted wins than the 23-4 Sun Belt record. The power index quantifies *how much* more.

Rule of thumb: a team's **SOS-adjusted wins** ≈ `record_wins × (opponent_avg_PI / 100)`.

## Postseason Bracket Application

NCAA Tournament selection uses RPI + committee judgment. RPI over-rewards mid-major conference champions and under-rewards second-place teams in elite conferences. The BSI Power Index gives a corrective lens:

- If a team finishes 4th in a PI > 100 conference with a strong record, they're a real bubble case.
- If a team finishes 1st in a PI < 85 conference with a great record, they should be the conference's auto-bid but not an at-large consideration.

**Use for:** modeling realistic bracket scenarios that account for conference depth, not RPI surface reads.

## SOS Discipline

When writing about a program's record:

1. Always state the conference PI rank when making cross-conference claims.
2. Never say "they've got the best record in college baseball" without adjusting for opponent quality.
3. A Pac-12 leftover program with a 22-3 record against the Patriot League is not elite. A 16-9 SEC program might be.

## Common Mistakes to Avoid

### The "Top Record" Trap
"Team X is 28-3, best in the country!" → Always check the PI rank of their conference. If the conference is PI < 85, the record is inflated.

### The "Conference Record" Trap
"Texas is 12-5 in SEC play, that's just middle-of-the-pack" → Middle of the SEC (PI 104.3) is more impressive than leading a mid-major. The team's national ranking should reflect SEC depth, not just SEC position.

### The "Mid-Major Champion" Trap
A mid-major champion going 22-1 in conference is *not* strong evidence of elite quality — they're going to play most of their games against limited competition. Watch their non-conference performance against PI > 95 opponents for a better signal.

## Quality Gates

- Every cross-conference claim cites the power index rank of both conferences.
- SOS-adjustment applied before declaring a program "better" than another from a different conference.
- PI data comes from `bsi_get_conference_power_index` with full meta envelope (source, fetched_at).
- Never use RPI as the primary adjustment tool — RPI has documented biases the power index corrects.

## Example Invocations

A user asks: "Is the ACC or the Big 12 stronger this year?"
1. Call `bsi_get_conference_power_index`
2. Find ACC and Big 12 entries
3. Compare PI scores AND tournament teams projected
4. Return a direct read with both numbers and a one-line analytical call

A user asks: "Where does Texas rank in real terms given the SEC?"
1. Call `bsi_get_conference_power_index` → confirm SEC PI and rank
2. Call `bsi_get_standings conference=SEC` → find Texas's position
3. Combine: "Texas sits Xth in the deepest conference (PI 104.3, 11 projected tournament teams), meaning their SOS-adjusted quality reads as [...]."
