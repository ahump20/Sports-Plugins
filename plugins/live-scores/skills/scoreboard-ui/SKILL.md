---
name: scoreboard-ui
description: Use when the task involves building scoreboard components, game cards, line score tables, or cross-sport score views. Covers React/Next.js component patterns, mobile-first layout, in-progress vs. final state rendering, and live-update visual indicators.
---

# Scoreboard UI

Use this skill when quality depends on building a clear, fast, and status-appropriate scoreboard surface. Score is the most-read number in sports — it must be large, correct, and instantly understandable on every screen size.

## Component Hierarchy

```
<ScoreboardPage>
  <ScoreboardHeader sport, date />
  <GameGrid>
    <GameCard game />      ← primary unit
      <TeamRow team, score, isWinning />
      <GameStatus status, period, clock />
      <LineScore innings/quarters />   ← expandable
  </GameGrid>
</ScoreboardPage>
```

## GameCard Component

### States

| State | Visual treatment |
|-------|----------------|
| `scheduled` | Neutral surface, start time centered, no score |
| `in-progress` | Elevated surface, pulsing live dot, bold score |
| `final` | Subdued surface, "Final" badge, winning team bold |
| `postponed` | Muted, "PPD" badge |
| `cancelled` | Muted, "Cancelled" badge |

### Score size rules

- Score: `text-4xl font-bold tabular-nums` on desktop
- Score: `text-3xl font-bold tabular-nums` on mobile
- Team name: `text-sm font-medium` (abbreviated on mobile)
- Status/inning: `text-xs text-muted-foreground`

Never let the score be smaller than the team name. If space is constrained, truncate the team name, not the score.

### Live indicator

```tsx
function LiveDot() {
  return (
    <span className="relative flex h-2 w-2">
      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75" />
      <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
    </span>
  );
}
// Show only for status === 'in-progress'. Never show for scheduled or final.
```

## Baseball-Specific Components

### Line score table

```tsx
interface LineScoreProps {
  homeTeam: string;
  awayTeam: string;
  innings: Array<{ home: number | null; away: number | null }>;
  totals: { home: [R: number, H: number, E: number]; away: [R: number, H: number, E: number] };
  currentInning?: number;
}
```

Display rules:
- Show innings 1–9 by default. Add columns for extras.
- Highlight the current half-inning being played.
- Use `—` for innings not yet played (null values).
- R/H/E totals in a separated final column group.
- Monospace font for all numbers.

```tsx
// Mobile: collapse to just the score and inning; expand on tap for full line score
```

### Baseball in-game state

```tsx
interface BaseballGameState {
  inning: number;
  isTopHalf: boolean;
  outs: number;
  balls: number;
  strikes: number;
  runnersOn: {
    first: boolean;
    second: boolean;
    third: boolean;
  };
}

function CountDisplay({ balls, strikes, outs }: Pick<BaseballGameState, 'balls' | 'strikes' | 'outs'>) {
  return (
    <span className="font-mono text-xs text-muted-foreground">
      {balls}-{strikes} | {outs} out{outs !== 1 ? 's' : ''}
    </span>
  );
}
```

Base diagram (SVG):
- Diamond orientation (rotated 45°)
- Filled base = runner on, unfilled = empty
- Size: 32×32px minimum tap target

## Cross-Sport Scoreboard

When displaying multiple sports on one page:

- Group by sport with a sticky sport label as a section separator.
- Order: In-progress games first (any sport), then scheduled, then final.
- Within each status group, sort by start time ascending.
- Use consistent card width across sports; do not vary card width by sport.

Sport badge colors:
- College Baseball: `bg-orange-600 text-white` (burnt orange)
- MLB: `bg-blue-700 text-white`
- NFL: `bg-slate-700 text-white`
- NBA: `bg-red-700 text-white`
- CFB: `bg-amber-700 text-white`

## Score Change Animation

When a score updates during a live poll:

```tsx
// Briefly flash the updated score with a yellow highlight, then fade to normal
// Use Framer Motion:
<motion.span
  key={score}  // remount on score change
  initial={{ backgroundColor: '#fef08a' }}
  animate={{ backgroundColor: 'transparent' }}
  transition={{ duration: 1.2 }}
  className="tabular-nums"
>
  {score}
</motion.span>
```

Only animate score changes, not full component remounts.

## Mobile Layout Rules

- Card width: full width on mobile (no side-by-side cards below 480px).
- Two columns at `sm:` breakpoint (480px+).
- Three columns at `lg:` breakpoint (1024px+).
- Minimum touch target: 44×44px for any interactive element on the card.
- The score must be readable at arm's length — do not go below `text-2xl` for scores on any screen.

## Hard Rules

- Never show a pulsing live dot for a final game.
- Never show a score for a scheduled (not-yet-started) game — show the start time instead.
- Never truncate a score value — only truncate team names.
- Always show both teams even if one team's data is not yet available — display `—` for the unknown score.
- Always test the card at min-width 320px (small phones) and max-width 1440px.
- Do not fetch live score data directly from a React component — use a Worker API route or polling hook.
