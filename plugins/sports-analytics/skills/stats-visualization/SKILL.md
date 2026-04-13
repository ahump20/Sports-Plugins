---
name: stats-visualization
description: Use when the task involves building chart components, stat tables, dashboards, or data display surfaces for sports statistics. Covers Recharts patterns, responsive table layouts, spark charts, leaderboards, and scoreboard UI for college and professional sports.
---

# Stats Visualization

Use this skill when the task requires building a clear, readable, and sports-appropriate data display. Good sports visualization surfaces the right number at the right size, earns trust with correct labeling, and loads fast even on mobile.

## Working Model

Before building any visualization, establish:

- **Audience**: Fan (storytelling), analyst (dense precision), or coach (actionable, minimal)?
- **Device**: Mobile-first scoreboard, desktop dashboard, or both?
- **Data volume**: Single game, season aggregate, or multi-season trend?
- **Primary question**: What is the user trying to answer by looking at this?

Design the chart to answer the primary question in one glance. If it requires study to decode, simplify.

## Chart Type Selection

| Data situation | Recommended chart |
|---------------|------------------|
| Comparing players on one metric | Horizontal bar chart |
| Tracking one metric over time | Line chart |
| Two correlated metrics (e.g. FIP vs ERA) | Scatter plot |
| Composition (pitch mix %) | Donut or stacked bar |
| Ranked leaderboard | Sorted table with sparklines |
| Win probability over game time | Area chart |
| Spray chart / field diagram | SVG custom overlay |

Default to the simplest chart that answers the question. Never use a 3D chart.

## Recharts Patterns

### Responsive container (always wrap)

```tsx
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
    <XAxis type="number" domain={[0, 'dataMax']} />
    <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 13 }} />
    <Tooltip formatter={(value: number) => value.toFixed(3)} />
    <Bar dataKey="woba" fill="#BF5700" radius={[0, 4, 4, 0]} />
  </BarChart>
</ResponsiveContainer>
```

### Color conventions for sports data

- Texas Longhorns: `#BF5700` (burnt orange), `#FFFFFF` (white)
- Above-average / positive: `#22c55e` (green-500)
- Below-average / negative: `#ef4444` (red-500)
- Neutral / baseline: `#94a3b8` (slate-400)
- Accent: use one primary accent per chart only

Do not use red/green for non-performance contexts — reserve them for "good vs. bad" comparisons only.

### Custom tooltip

```tsx
function StatTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-white shadow-lg">
      <p className="font-semibold mb-1">{label}</p>
      {payload.map((entry) => (
        <p key={entry.name} style={{ color: entry.color }}>
          {entry.name}: <span className="font-mono">{Number(entry.value).toFixed(3)}</span>
        </p>
      ))}
    </div>
  );
}
```

## Stat Tables

### Leaderboard table pattern

```tsx
// components/LeaderboardTable.tsx
interface Column<T> {
  key: keyof T;
  label: string;
  format?: (v: unknown) => string;
  sortable?: boolean;
}

// Rules:
// - Sticky first column (player name)
// - Right-align all numeric columns
// - Mono font for numbers: font-mono text-sm tabular-nums
// - Highlight the column being sorted
// - Color-code values above/below league average
```

Table rules:
- Use `tabular-nums` for all numeric cells to prevent column-width shifting.
- Truncate names longer than 20 characters with an ellipsis tooltip.
- Show rank number in the first column for leaderboards.
- Mobile: reduce to 3–4 columns max. Let users tap to expand a row.

### Percentile bar (inline with a stat)

```tsx
function PercentileBar({ value, max = 100 }: { value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = pct >= 75 ? '#22c55e' : pct >= 40 ? '#94a3b8' : '#ef4444';
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-mono text-slate-400">{Math.round(pct)}th</span>
    </div>
  );
}
```

## Dashboard Layout Principles

- **Header**: Team name, season, last-updated timestamp. Always show data freshness.
- **KPI strip**: 4–6 key numbers at the top. No more than one line each. Font size 24px+.
- **Primary chart**: The most decision-relevant visualization. Full width or 2/3 width.
- **Secondary charts**: Supporting context. Half-width grid.
- **Table**: Detail layer. Below the fold is fine.

Never open a sports dashboard with a table. Lead with a chart or KPI strip.

### Grid pattern (Tailwind)

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* KPI cards */}
</div>
<div className="mt-6">
  {/* Primary chart — full width */}
</div>
<div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
  {/* Secondary charts */}
</div>
```

## Scoreboard Components

Live scoreboard UI rules:
- Score must be the largest number on the component (font size 48px+ on desktop).
- Status (inning, quarter, time) must be visible without scrolling.
- Team abbreviations over team logos when logos are unavailable — never show broken images.
- Use a pulsing indicator (`animate-pulse`) only for live/in-progress games, not final scores.
- Neutral gray background for final scores; slightly elevated surface for in-progress games.

## Loading and Empty States

- Use a skeleton loader that mirrors the exact shape of the chart or table it replaces.
- Empty state: one short sentence explaining why there is no data (e.g. "No games played yet this week."). Never show a blank component.
- Error state: show the last known data with a staleness badge rather than replacing it with an error message if data is < 5 minutes old.

## Hard Rules

- Never use a pie chart for more than 5 segments — use a bar chart instead.
- Never show more than 8 columns in a mobile table.
- Never label a bar chart axis without units (e.g. "wRC+ (100 = avg)" not just "wRC+").
- Always round displayed values to the appropriate precision: ERA to 2 decimal places, wOBA to 3, K% to 1 decimal with a % sign.
- Never show a chart without a title and an axis label on at least one axis.
- Always test chart components with the minimum data case (1 data point) and maximum data case (30+ data points).
