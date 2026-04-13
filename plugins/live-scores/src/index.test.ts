import { describe, it, expect, beforeEach } from 'vitest';
import { GameCardState, resolveGameCardState } from './game-card.js';
import { ScoreCache } from './cache.js';
import { formatPeriod, formatClock, SPORT_BADGE_COLORS } from './display.js';
import type { LiveGameState } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeGame(overrides: Partial<LiveGameState> = {}): LiveGameState {
  return {
    gameId: 'test-001',
    sport: 'college-baseball',
    status: 'in-progress',
    homeTeam: { teamId: 'texas', name: 'Texas Longhorns', abbreviation: 'TEX', score: 5 },
    awayTeam: { teamId: 'tcu', name: 'TCU Horned Frogs', abbreviation: 'TCU', score: 3 },
    period: 'Top 7th',
    startTime: '2025-04-05T19:00:00Z',
    lastUpdated: new Date().toISOString(),
    source: 'bsi-mcp',
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// GameCard state resolution
// ---------------------------------------------------------------------------

describe('resolveGameCardState', () => {
  it('shows live dot only for in-progress games', () => {
    const result = resolveGameCardState(makeGame({ status: 'in-progress' }));
    expect(result.showLiveDot).toBe(true);
    expect(result.state).toBe(GameCardState.InProgress);
  });

  it('does NOT show live dot for final games', () => {
    const result = resolveGameCardState(makeGame({ status: 'final' }));
    expect(result.showLiveDot).toBe(false);
    expect(result.badgeText).toBe('Final');
  });

  it('does NOT show score for scheduled games', () => {
    const result = resolveGameCardState(makeGame({ status: 'scheduled' }));
    expect(result.showScore).toBe(false);
    expect(result.badgeText).toBeNull();
  });

  it('shows PPD badge for postponed games', () => {
    const result = resolveGameCardState(makeGame({ status: 'postponed' }));
    expect(result.badgeText).toBe('PPD');
  });

  it('shows Cancelled badge for cancelled games', () => {
    const result = resolveGameCardState(makeGame({ status: 'cancelled' }));
    expect(result.badgeText).toBe('Cancelled');
  });
});

// ---------------------------------------------------------------------------
// Score cache
// ---------------------------------------------------------------------------

describe('ScoreCache', () => {
  let cache: ScoreCache;

  beforeEach(() => {
    cache = new ScoreCache();
  });

  it('stores and retrieves a game', () => {
    const game = makeGame();
    cache.put('test-001', game, 60);
    expect(cache.get('test-001')).toEqual(game);
  });

  it('returns null for missing game', () => {
    expect(cache.get('nonexistent')).toBeNull();
  });

  it('returns null for expired entries', () => {
    const game = makeGame();
    cache.put('test-001', game, 0); // 0-second TTL = already expired
    expect(cache.get('test-001')).toBeNull();
  });

  it('tracks size', () => {
    cache.put('a', makeGame(), 60);
    cache.put('b', makeGame(), 60);
    expect(cache.size).toBe(2);
  });

  it('clears all entries', () => {
    cache.put('a', makeGame(), 60);
    cache.clear();
    expect(cache.size).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

describe('formatPeriod', () => {
  it('formats top of 1st', () => {
    expect(formatPeriod(1, true)).toBe('Top 1st');
  });
  it('formats bottom of 7th', () => {
    expect(formatPeriod(7, false)).toBe('Bot 7th');
  });
  it('formats 2nd correctly', () => {
    expect(formatPeriod(2, true)).toBe('Top 2nd');
  });
  it('formats 3rd correctly', () => {
    expect(formatPeriod(3, false)).toBe('Bot 3rd');
  });
  it('formats 11th correctly', () => {
    expect(formatPeriod(11, true)).toBe('Top 11th');
  });
});

describe('formatClock', () => {
  it('passes through already-formatted time', () => {
    expect(formatClock('12:34')).toBe('12:34');
  });
  it('converts raw seconds to mm:ss', () => {
    expect(formatClock('125')).toBe('2:05');
  });
  it('passes through non-numeric strings', () => {
    expect(formatClock('Halftime')).toBe('Halftime');
  });
});

describe('SPORT_BADGE_COLORS', () => {
  it('has colors for all five sports', () => {
    expect(Object.keys(SPORT_BADGE_COLORS)).toHaveLength(5);
    expect(SPORT_BADGE_COLORS['college-baseball'].bg).toBe('bg-orange-600');
  });
});
