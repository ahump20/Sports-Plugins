import { describe, it, expect } from 'vitest';
import {
  era,
  fip,
  whip,
  kPer9,
  bbPer9,
  kPerBb,
  lobPercent,
  avg,
  obp,
  slg,
  totalBases,
  ops,
  iso,
  babip,
  woba,
  wrcPlus,
} from './sabermetrics.js';

// ---------------------------------------------------------------------------
// Pitching
// ---------------------------------------------------------------------------

describe('era', () => {
  it('computes ERA correctly', () => {
    expect(era(20, 60)).toBeCloseTo(3.0, 4);
  });
  it('returns null for 0 IP', () => {
    expect(era(5, 0)).toBeNull();
  });
});

describe('fip', () => {
  it('computes FIP with default NCAA constant', () => {
    // (13*5 + 3*(20+3) - 2*60) / 60 + 3.10
    // = (65 + 69 - 120) / 60 + 3.10
    // = 14 / 60 + 3.10 = 0.2333 + 3.10 = 3.3333
    const result = fip(5, 20, 3, 60, 60);
    expect(result).toBeCloseTo(3.333, 2);
  });
  it('returns null for 0 IP', () => {
    expect(fip(1, 1, 1, 10, 0)).toBeNull();
  });
});

describe('whip', () => {
  it('computes WHIP correctly', () => {
    expect(whip(20, 50, 60)).toBeCloseTo(1.167, 2);
  });
  it('returns null for 0 IP', () => {
    expect(whip(5, 10, 0)).toBeNull();
  });
});

describe('kPer9', () => {
  it('computes K/9', () => {
    expect(kPer9(90, 60)).toBeCloseTo(13.5, 4);
  });
});

describe('bbPer9', () => {
  it('computes BB/9', () => {
    expect(bbPer9(20, 60)).toBeCloseTo(3.0, 4);
  });
});

describe('kPerBb', () => {
  it('computes K/BB', () => {
    expect(kPerBb(90, 20)).toBeCloseTo(4.5, 4);
  });
  it('returns null for 0 BB', () => {
    expect(kPerBb(10, 0)).toBeNull();
  });
});

describe('lobPercent', () => {
  it('computes strand rate', () => {
    const result = lobPercent(60, 20, 3, 25, 5);
    // (60 + 20 + 3 - 25) / (60 + 20 + 3 - 7) = 58 / 76 = 0.7632
    expect(result).toBeCloseTo(0.763, 2);
  });
});

// ---------------------------------------------------------------------------
// Hitting
// ---------------------------------------------------------------------------

describe('avg', () => {
  it('computes batting average', () => {
    expect(avg(60, 200)).toBeCloseTo(0.300, 3);
  });
  it('returns null for 0 AB', () => {
    expect(avg(0, 0)).toBeNull();
  });
});

describe('obp', () => {
  it('computes on-base percentage', () => {
    // (60 + 20 + 5) / (200 + 20 + 5 + 3) = 85 / 228 = 0.3728
    expect(obp(60, 20, 5, 200, 3)).toBeCloseTo(0.3728, 3);
  });
});

describe('slg', () => {
  it('computes slugging percentage', () => {
    expect(slg(120, 200)).toBeCloseTo(0.600, 3);
  });
});

describe('totalBases', () => {
  it('computes TB from hit components', () => {
    // 60 hits: 40 singles, 10 doubles, 5 triples, 5 HR
    // 40 + 20 + 15 + 20 = 95
    expect(totalBases(60, 10, 5, 5)).toBe(95);
  });
});

describe('ops', () => {
  it('adds OBP and SLG', () => {
    expect(ops(0.373, 0.600)).toBeCloseTo(0.973, 3);
  });
});

describe('iso', () => {
  it('computes isolated power', () => {
    expect(iso(0.600, 0.300)).toBeCloseTo(0.300, 3);
  });
});

describe('babip', () => {
  it('computes BABIP', () => {
    // (60 - 5) / (200 - 40 - 5 + 3) = 55 / 158 = 0.348
    expect(babip(60, 5, 200, 40, 3)).toBeCloseTo(0.348, 2);
  });
  it('returns null when denominator is zero', () => {
    expect(babip(1, 1, 2, 1, 0)).toBeNull();
  });
});

describe('woba', () => {
  it('computes wOBA with default weights', () => {
    // Small sample: 5 BB, 2 HBP, 20 singles, 8 doubles, 2 triples, 5 HR
    // denom = 100 + 5 + 3 + 2 = 110
    const result = woba(5, 2, 20, 8, 2, 5, 100, 3);
    expect(result).toBeGreaterThan(0);
    expect(result).toBeLessThan(1);
  });
  it('returns null for 0 PA', () => {
    expect(woba(0, 0, 0, 0, 0, 0, 0, 0)).toBeNull();
  });
});

describe('wrcPlus', () => {
  it('returns ~100 for league-average wOBA', () => {
    const result = wrcPlus(0.320, 0.320);
    expect(result).toBeCloseTo(100, 0);
  });
  it('returns > 100 for above-average wOBA', () => {
    const result = wrcPlus(0.400, 0.320);
    expect(result).toBeGreaterThan(100);
  });
  it('returns < 100 for below-average wOBA', () => {
    const result = wrcPlus(0.280, 0.320);
    expect(result).toBeLessThan(100);
  });
});
