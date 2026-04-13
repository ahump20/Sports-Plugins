import { describe, it, expect } from 'vitest';
import {
  normalizeIP,
  toISODate,
  isGameHourUTC,
  normalizeTeamName,
  applyBatterDefaults,
  gameDedupKey,
  round,
} from './normalization.js';

describe('normalizeIP', () => {
  it('converts "6.0" → 6.0', () => {
    expect(normalizeIP('6.0')).toBeCloseTo(6.0, 4);
  });
  it('converts "6.1" → 6.333', () => {
    expect(normalizeIP('6.1')).toBeCloseTo(6.333, 2);
  });
  it('converts "6.2" → 6.667', () => {
    expect(normalizeIP('6.2')).toBeCloseTo(6.667, 2);
  });
  it('handles integer input', () => {
    expect(normalizeIP(7)).toBe(7);
  });
  it('handles "0.1" → 0.333', () => {
    expect(normalizeIP('0.1')).toBeCloseTo(0.333, 2);
  });
});

describe('toISODate', () => {
  it('formats a Date to YYYY-MM-DD', () => {
    expect(toISODate(new Date('2025-04-05T12:00:00Z'))).toBe('2025-04-05');
  });
});

describe('isGameHourUTC', () => {
  it('returns true for 15:00 UTC (11 AM ET)', () => {
    expect(isGameHourUTC(15)).toBe(true);
  });
  it('returns true for 2:00 UTC (10 PM ET)', () => {
    expect(isGameHourUTC(2)).toBe(true);
  });
  it('returns false for 10:00 UTC (6 AM ET)', () => {
    expect(isGameHourUTC(10)).toBe(false);
  });
});

describe('normalizeTeamName', () => {
  it('resolves "Texas" to canonical name', () => {
    expect(normalizeTeamName('Texas')).toBe('Texas Longhorns');
  });
  it('resolves "UT" to canonical name', () => {
    expect(normalizeTeamName('UT')).toBe('Texas Longhorns');
  });
  it('returns input unchanged for unknown teams', () => {
    expect(normalizeTeamName('Unknown U')).toBe('Unknown U');
  });
});

describe('applyBatterDefaults', () => {
  it('fills missing sf and hbp with 0', () => {
    const raw = { ab: 100, h: 30 };
    const result = applyBatterDefaults(raw);
    expect(result.sf).toBe(0);
    expect(result.hbp).toBe(0);
  });
  it('preserves existing values', () => {
    const raw = { ab: 100, h: 30, sf: 5, hbp: 3 };
    const result = applyBatterDefaults(raw);
    expect(result.sf).toBe(5);
    expect(result.hbp).toBe(3);
  });
});

describe('gameDedupKey', () => {
  it('produces a consistent key regardless of team order', () => {
    const a = gameDedupKey('texas', '2025-04-05', 'tcu');
    const b = gameDedupKey('tcu', '2025-04-05', 'texas');
    expect(a).toBe(b);
  });
});

describe('round', () => {
  it('rounds ERA to 2 decimal places', () => {
    expect(round(3.1415, 2)).toBe(3.14);
  });
  it('rounds wOBA to 3 decimal places', () => {
    expect(round(0.34567, 3)).toBe(0.346);
  });
});
