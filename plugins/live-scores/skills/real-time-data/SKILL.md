---
name: real-time-data
description: Use when the task involves building live data polling, Cloudflare Worker scheduled refresh, KV cache management, or React hooks for real-time score updates. Covers interval management, stale-data handling, WebSocket alternatives, and graceful degradation when the data source is unavailable.
---

# Real-Time Data

Use this skill when quality depends on getting live sports data to a UI surface with acceptable latency, without overloading the data provider, and without leaving users staring at stale scores. Real-time sports data is polling-first in most cases — true WebSocket streams are the exception, not the rule.

## Working Model

Before building any live data layer, answer:

- **Latency requirement**: Can scores be 60 seconds stale? 30? 10? Live pitch-by-pitch?
- **Provider**: BSI MCP, SportsDataIO, MLB Stats API, or custom scrape?
- **Active game window**: When are games actually in progress? Avoid 30-second polls at 3 AM.
- **Failure behavior**: If the provider is down, should the UI show last known data or an error state?

Most sports apps only need a 30–60 second poll during live game hours. Anything more aggressive will exceed rate limits or increase costs without visible benefit to users.

## Polling Architecture

### Cloudflare Worker as polling proxy

The recommended architecture for the BSI stack:

```
Browser → Cloudflare Worker API route → Cloudflare KV (cache)
                                       ↑
                     Cloudflare Cron Worker (scheduled refresh)
                                       ↑
                              Data provider (BSI MCP / SportsDataIO)
```

The browser never hits the data provider directly. The Worker serves from KV. The Cron Worker refreshes KV on a schedule.

### Cron Worker (scheduled refresh)

```typescript
// workers/scores-cron/index.ts
export default {
  async scheduled(_event: ScheduledEvent, env: Env, _ctx: ExecutionContext) {
    const now = new Date();
    const hour = now.getUTCHours();

    // Only poll aggressively during game hours (11am–midnight ET = 15:00–04:00 UTC)
    const isGameHour = hour >= 15 || hour < 4;
    if (!isGameHour) return;

    const games = await fetchLiveGames(env);
    await Promise.allSettled(
      games.map(game => refreshAndStoreGame(env, game))
    );
  },
};

async function refreshAndStoreGame(env: Env, game: LiveGame) {
  const fresh = await fetchGameState(env, game.gameId);
  await env.SCORES_KV.put(
    `game:${game.gameId}`,
    JSON.stringify({ ...fresh, lastUpdated: new Date().toISOString() }),
    { expirationTtl: 300 }  // 5 min TTL — cron will refresh before expiry
  );
}
```

Cron schedule: `*/1 * * * *` during season (every minute). Adjust to `*/5 * * * *` during off-season.

### API route (serves browser)

```typescript
// app/api/scores/[sport]/route.ts (Next.js App Router)
export async function GET(req: Request, { params }: { params: { sport: string } }) {
  const kv = getKVBinding();  // Cloudflare binding injected by Workers integration
  const games = await kv.list({ prefix: `game:${params.sport}:` });

  const results = await Promise.all(
    games.keys.map(({ name }) => kv.get(name, 'json'))
  );

  return Response.json({
    games: results.filter(Boolean),
    generatedAt: new Date().toISOString(),
  });
}
```

## React Polling Hook

```typescript
// hooks/useLiveScores.ts
import { useEffect, useRef, useState } from 'react';

interface UseLiveScoresOptions {
  sport: string;
  intervalMs?: number;      // Default: 60000 (60 seconds)
  activeOnly?: boolean;     // Only poll when tab is visible
}

export function useLiveScores({ sport, intervalMs = 60_000, activeOnly = true }: UseLiveScoresOptions) {
  const [data, setData] = useState<GameScore[] | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isStale, setIsStale] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchScores = async () => {
    try {
      const res = await fetch(`/api/scores/${sport}`);
      if (!res.ok) return;  // Keep existing data on error
      const json = await res.json();
      setData(json.games);
      setLastUpdated(new Date());
      setIsStale(false);
    } catch {
      // Network error — mark stale but keep existing data
      setIsStale(true);
    }
  };

  useEffect(() => {
    fetchScores();  // Initial fetch

    const startPolling = () => {
      intervalRef.current = setInterval(fetchScores, intervalMs);
    };

    const stopPolling = () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };

    if (activeOnly) {
      const handleVisibility = () => {
        if (document.hidden) stopPolling();
        else { fetchScores(); startPolling(); }
      };
      document.addEventListener('visibilitychange', handleVisibility);
      startPolling();
      return () => {
        stopPolling();
        document.removeEventListener('visibilitychange', handleVisibility);
      };
    } else {
      startPolling();
      return stopPolling;
    }
  }, [sport, intervalMs]);

  return { data, lastUpdated, isStale };
}
```

Key behaviors:
- Pauses polling when the browser tab is hidden (`activeOnly: true` by default).
- Keeps existing data on error — never replaces good data with nothing.
- Returns `isStale` flag for the UI to show a staleness indicator.

## Stale Data Handling

```tsx
function StaleIndicator({ lastUpdated, isStale }: { lastUpdated: Date | null; isStale: boolean }) {
  if (!lastUpdated) return null;
  const ageSeconds = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);

  if (isStale || ageSeconds > 180) {
    return <span className="text-xs text-amber-500">⚠ Data may be delayed</span>;
  }
  return <span className="text-xs text-muted-foreground">Updated {ageSeconds}s ago</span>;
}
```

Show a yellow warning badge if:
- The last successful fetch was more than 3 minutes ago.
- The `isStale` flag is set (network error).

Never remove existing score data because the provider is temporarily unavailable.

## BSI MCP Integration

The BSI MCP endpoint at `https://blazesportsintel.com/mcp` supports live college baseball game state queries.

```typescript
// Use the MCP client (Claude Code session) to call:
// Tool: get_live_games
// Tool: get_game_state { gameId }
// Tool: get_team_scores { sport, date }
```

MCP tools are consumed server-side in Workers only — never from a browser client. The Worker fetches from MCP, stores in KV, and serves the browser from KV.

## Rate Limit Budgets

| Provider | Typical limit | Recommended poll interval |
|----------|--------------|--------------------------|
| SportsDataIO (paid) | 1,000 req/day or per minute tier | 30s–60s during games |
| MLB Stats API | Public, generous | 30s–60s |
| BSI MCP | Session-based | 60s |
| NCAA Stats HTML | Public, fragile | 300s (5 min) — batch only |

Never poll a public HTML endpoint more than once every 5 minutes. HTML scrapes are not intended as real-time APIs and will be blocked.

## Hard Rules

- Never initiate live polling from a React Server Component or SSG build step.
- Never poll at intervals shorter than 30 seconds without explicit provider approval.
- Always pause polling when the browser tab is not visible.
- Always retain the last known good data on provider error — never show an empty state just because one poll failed.
- Always include a `lastUpdated` timestamp in every KV-stored score entry.
- Log every failed provider fetch with: provider name, endpoint, HTTP status, and timestamp.
