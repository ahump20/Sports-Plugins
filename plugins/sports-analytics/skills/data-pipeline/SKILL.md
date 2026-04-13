---
name: data-pipeline
description: Use when the task involves building or auditing a sports data ingestion pipeline — including API clients for SportsDataIO, MLB Stats API, NCAA stats, or BSI's MCP endpoint; data normalization; Cloudflare KV/D1/R2 storage patterns; caching strategy; and error handling for live game feeds.
---

# Data Pipeline

Use this skill when quality depends on structuring a reliable, maintainable sports data pipeline rather than just fetching and displaying raw API responses. The goal is a clean data layer that the rest of the application can depend on.

## Working Model

Before building any pipeline component, establish:

- **Source(s)**: Which APIs or feeds? SportsDataIO, MLB Stats API, NCAA, ESPN, BSI MCP, manual?
- **Sport and data type**: Scores, standings, player stats, play-by-play, or projections?
- **Update frequency**: One-time, daily batch, hourly, or real-time (< 60 seconds)?
- **Consumer**: Next.js page (SSG/ISR), Cloudflare Worker API route, or in-browser component?
- **Storage**: Cloudflare KV (low-latency reads), D1 (SQL queries), R2 (blobs), or in-memory?

## Provider Reference

| Provider | Best For | Auth |
|----------|----------|------|
| SportsDataIO | NFL, NBA, CFB live scores and stats | API key header |
| MLB Stats API | MLB schedules, box scores, player data | Public (no key required) |
| NCAA Stats | College baseball, football, basketball | Public HTML scrape |
| BSI MCP | College baseball, cross-sport scores, BSI-specific data | MCP session token |
| ESPN public API | Scores, standings (unofficial — may break) | Public |

Never embed API keys in client-side code. All provider keys must go through environment variables or Cloudflare Worker secrets.

## API Client Pattern

```typescript
// lib/providers/sportsdata-client.ts
const BASE = 'https://api.sportsdata.io/v3';

async function sdFetch<T>(path: string): Promise<T> {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Ocp-Apim-Subscription-Key': process.env.SPORTS_DATA_IO_API_KEY! },
    next: { revalidate: 60 }, // Next.js ISR cache
  });
  if (!res.ok) throw new Error(`SportsDataIO ${res.status} for ${path}`);
  return res.json() as Promise<T>;
}
```

Apply the same wrapper pattern for each provider. Never scatter bare `fetch` calls across components.

## Caching Strategy

| Data type | Staleness tolerance | Recommended TTL |
|-----------|---------------------|----------------|
| Live game score | 30–60 seconds | KV with 30s TTL |
| Today's schedule | 5 minutes | KV or ISR 300s |
| Season standings | 1 hour | ISR 3600s |
| Player season stats | 1 day | D1 + daily batch |
| Historical archives | Permanent | R2 blob + D1 |

### Cloudflare KV live score pattern

```typescript
// workers/scores-worker.ts
export async function getLiveScore(env: Env, gameId: string) {
  const cached = await env.SCORES_KV.get(`score:${gameId}`, 'json');
  if (cached) return cached;

  const fresh = await fetchFromProvider(gameId);
  await env.SCORES_KV.put(`score:${gameId}`, JSON.stringify(fresh), {
    expirationTtl: 30,
  });
  return fresh;
}
```

## Normalization Conventions

### Score and game state

```typescript
interface LiveGameState {
  gameId: string;
  sport: 'mlb' | 'nfl' | 'nba' | 'cfb' | 'college-baseball';
  status: 'scheduled' | 'in-progress' | 'final' | 'postponed' | 'cancelled';
  homeTeam: TeamScore;
  awayTeam: TeamScore;
  period: string;          // "Top 7th", "Q3", "2nd Half"
  clock?: string;          // For timed sports
  startTime: string;       // ISO 8601
  lastUpdated: string;     // ISO 8601
  source: string;
}

interface TeamScore {
  teamId: string;
  name: string;
  abbreviation: string;
  score: number;
  record?: string;         // "24-8"
}
```

Normalize all team names to a canonical form. Do not pass provider-specific team abbreviations directly to the UI layer.

## Error Handling

- **Provider timeout (>5s)**: Return stale cached data if available; otherwise return null and let the UI handle gracefully.
- **Provider 429 (rate limited)**: Implement exponential backoff with jitter. Log the retry attempt.
- **Provider 5xx**: Retry once after 2 seconds. If second attempt fails, surface an error state.
- **Unexpected schema**: Log the raw response to R2 for debugging. Return null rather than throwing to the UI.
- **Stale KV data during a game**: Always include `lastUpdated` in the response so the UI can show a staleness indicator.

## Cloudflare Worker Scheduled Refresh

```typescript
// workers/stats-refresh/index.ts — triggered by Cron Trigger
export default {
  async scheduled(event: ScheduledEvent, env: Env) {
    const games = await fetchTodaysSchedule(env);
    for (const game of games.filter(g => g.status === 'in-progress')) {
      await refreshGameScore(env, game.gameId);
    }
  },
};
```

Schedule: `*/1 * * * *` for live game hours; `0 * * * *` for off-hours standings refresh.

## Hard Rules

- Never expose raw provider API keys in Next.js page props, client components, or public routes.
- Never fetch live data directly from a client component during a game — always go through a Worker or API route.
- Always validate that the response schema matches your TypeScript interface before storing.
- Always include a `lastUpdated` field in every stored or returned data object.
- Never cache a failed (null/error) response. Only cache successful responses.
- Log every ingest run with: source, game/resource count fetched, duration, and any errors.
