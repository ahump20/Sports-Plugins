import { describe, it, expect } from 'vitest';
import { marcelProjection, winProbability } from './models.js';
import { formatERA, formatWoba, formatPercent, tierLabel } from './format.js';
import { createProviderClient } from './provider.js';

// ---------------------------------------------------------------------------
// Marcel Projection
// ---------------------------------------------------------------------------

describe('marcelProjection', () => {
  it('returns league-average when all seasons equal league-average', () => {
    const result = marcelProjection({
      yr1: 0.320, yr2: 0.320, yr3: 0.320,
      pa1: 200, pa2: 200, pa3: 200,
      lgAvg: 0.320,
    });
    expect(result.projected).toBeCloseTo(0.320, 3);
    expect(result.confidence).toBe('high');
  });

  it('regresses toward mean for low-PA player', () => {
    const result = marcelProjection({
      yr1: 0.400, yr2: 0, yr3: 0,
      pa1: 50, pa2: 0, pa3: 0,
      lgAvg: 0.320,
    });
    // Should regress toward 0.320
    expect(result.projected).toBeLessThan(0.400);
    expect(result.projected).toBeGreaterThan(0.320);
    expect(result.confidence).toBe('low');
  });

  it('assigns medium confidence for 1-2 seasons with 200 PA', () => {
    const result = marcelProjection({
      yr1: 0.350, yr2: 0.330, yr3: 0,
      pa1: 150, pa2: 100, pa3: 0,
      lgAvg: 0.320,
    });
    expect(result.confidence).toBe('medium');
  });
});

// ---------------------------------------------------------------------------
// Win Probability
// ---------------------------------------------------------------------------

describe('winProbability', () => {
  it('returns > 0.5 when home team is ahead', () => {
    const p = winProbability({
      inning: 7, isTopHalf: false, outs: 1,
      runnersOn: 0, homeScore: 5, awayScore: 2,
    });
    expect(p).toBeGreaterThan(0.5);
  });

  it('returns < 0.5 when home team is behind', () => {
    const p = winProbability({
      inning: 7, isTopHalf: true, outs: 0,
      runnersOn: 0, homeScore: 1, awayScore: 5,
    });
    expect(p).toBeLessThan(0.5);
  });

  it('returns ~0.5 for a tied game in the 1st inning', () => {
    const p = winProbability({
      inning: 1, isTopHalf: true, outs: 0,
      runnersOn: 0, homeScore: 0, awayScore: 0,
    });
    expect(p).toBeGreaterThan(0.45);
    expect(p).toBeLessThan(0.65);
  });

  it('returns value between 0 and 1', () => {
    const p = winProbability({
      inning: 9, isTopHalf: false, outs: 2,
      runnersOn: 0, homeScore: 10, awayScore: 0,
    });
    expect(p).toBeGreaterThan(0);
    expect(p).toBeLessThan(1);
  });
});

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

describe('formatERA', () => {
  it('formats to 2 decimal places', () => {
    expect(formatERA(3.1)).toBe('3.10');
    expect(formatERA(3.456)).toBe('3.46');
  });
});

describe('formatWoba', () => {
  it('formats to 3 decimal places', () => {
    expect(formatWoba(0.34567)).toBe('0.346');
  });
});

describe('formatPercent', () => {
  it('formats with 1 decimal and % suffix', () => {
    expect(formatPercent(22.55)).toBe('22.6%');
  });
});

// ---------------------------------------------------------------------------
// Tier Labels
// ---------------------------------------------------------------------------

describe('tierLabel', () => {
  it('classifies elite ERA', () => {
    expect(tierLabel('era', 2.20)).toBe('elite');
  });
  it('classifies above-avg ERA', () => {
    expect(tierLabel('era', 3.00)).toBe('above-avg');
  });
  it('classifies average ERA', () => {
    expect(tierLabel('era', 4.00)).toBe('average');
  });
  it('classifies below-avg ERA', () => {
    expect(tierLabel('era', 5.50)).toBe('below-avg');
  });

  it('classifies elite wRC+', () => {
    expect(tierLabel('wrcPlus', 155)).toBe('elite');
  });
  it('classifies below-avg wRC+', () => {
    expect(tierLabel('wrcPlus', 70)).toBe('below-avg');
  });

  it('returns average for unknown stat', () => {
    expect(tierLabel('unknownStat', 42)).toBe('average');
  });
});

// ---------------------------------------------------------------------------
// Provider Client
// ---------------------------------------------------------------------------

describe('createProviderClient', () => {
  it('creates an MLB Stats API client without auth', () => {
    const client = createProviderClient('mlb-stats-api');
    expect(client.provider).toBe('mlb-stats-api');
    expect(client.source).toBe('mlb-stats-api');
  });

  it('throws when API key is missing for authenticated provider', () => {
    expect(() => createProviderClient('sportsdata-io', {})).toThrow(
      'Missing environment variable',
    );
  });

  it('creates a SportsDataIO client when key is provided', () => {
    const client = createProviderClient('sportsdata-io', {
      SPORTS_DATA_IO_API_KEY: 'test-key-123',
    });
    expect(client.provider).toBe('sportsdata-io');
  });
});
