import { describe, it, expect } from 'vitest';
import { computeBatterMetrics, computePitcherMetrics } from './metrics.js';
import { evaluatePitcher } from './pitcher-eval.js';
import { optimizeLineup } from './lineup.js';
import { ingestBoxScore } from './ingest.js';
import type { BatterLine, PitcherLine, GameBoxScore } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeBatter(overrides: Partial<BatterLine> = {}): BatterLine {
  return {
    playerId: 'p1',
    name: 'Test Player',
    position: 'SS',
    ab: 200,
    r: 30,
    h: 60,
    rbi: 25,
    bb: 20,
    k: 40,
    hbp: 5,
    sf: 3,
    doubles: 10,
    triples: 2,
    hr: 5,
    sb: 8,
    cs: 2,
    ...overrides,
  };
}

function makePitcher(overrides: Partial<PitcherLine> = {}): PitcherLine {
  return {
    playerId: 'pitcher1',
    name: 'Test Pitcher',
    ip: 60,
    h: 50,
    r: 22,
    er: 20,
    bb: 18,
    k: 65,
    hr: 5,
    hbp: 3,
    decision: 'W',
    pitchCount: 1400,
    strikes: 900,
    ...overrides,
  };
}

function makeNineBatters(): BatterLine[] {
  return Array.from({ length: 9 }, (_, i) =>
    makeBatter({
      playerId: `p${i + 1}`,
      name: `Player ${i + 1}`,
      ab: 150 + i * 10,
      h: 40 + i * 3,
      bb: 10 + i * 2,
      hr: 2 + i,
      doubles: 5 + i,
    }),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('computeBatterMetrics', () => {
  it('returns non-null metrics for valid input', () => {
    const m = computeBatterMetrics(makeBatter());
    expect(m.avg).not.toBeNull();
    expect(m.obp).not.toBeNull();
    expect(m.slg).not.toBeNull();
    expect(m.ops).not.toBeNull();
    expect(m.iso).not.toBeNull();
    expect(m.babip).not.toBeNull();
    expect(m.woba).not.toBeNull();
    expect(m.wrcPlus).not.toBeNull();
    expect(m.bbPercent).not.toBeNull();
    expect(m.kPercent).not.toBeNull();
  });

  it('computes .300 AVG for 60/200', () => {
    const m = computeBatterMetrics(makeBatter());
    expect(m.avg).toBe(0.300);
  });
});

describe('computePitcherMetrics', () => {
  it('returns non-null metrics for valid input', () => {
    const m = computePitcherMetrics(makePitcher());
    expect(m.era).not.toBeNull();
    expect(m.fip).not.toBeNull();
    expect(m.whip).not.toBeNull();
    expect(m.kPer9).not.toBeNull();
    expect(m.bbPer9).not.toBeNull();
  });

  it('computes ERA ~3.00 for 20 ER in 60 IP', () => {
    const m = computePitcherMetrics(makePitcher());
    expect(m.era).toBe(3.00);
  });
});

describe('evaluatePitcher', () => {
  it('recommends starter for a pitcher with 3+ pitches and low walk rate', () => {
    const eval_ = evaluatePitcher(makePitcher(), 'friday-starter', [
      { pitch: 'four-seam', usage: 0.50 },
      { pitch: 'slider', usage: 0.30, whiffPercent: 35 },
      { pitch: 'changeup', usage: 0.20 },
    ]);
    expect(eval_.recommendedRole).toBe('starter');
    expect(eval_.flags).toHaveLength(0);
  });

  it('flags over-reliance when one pitch is >70% usage', () => {
    const eval_ = evaluatePitcher(makePitcher(), 'closer', [
      { pitch: 'four-seam', usage: 0.80 },
      { pitch: 'slider', usage: 0.20 },
    ]);
    expect(eval_.flags.some((f) => f.includes('Over-relies'))).toBe(true);
  });
});

describe('optimizeLineup', () => {
  it('produces a 9-slot lineup', () => {
    const card = optimizeLineup(makeNineBatters(), 'TCU', 'RHP');
    expect(card.lineup).toHaveLength(9);
    expect(card.opponent).toBe('TCU');
    expect(card.opponentStarterHand).toBe('RHP');
  });

  it('throws when fewer than 9 batters are provided', () => {
    expect(() => optimizeLineup([], 'TCU', 'RHP')).toThrow('at least 9');
  });
});

describe('ingestBoxScore', () => {
  it('ingests a valid box score with no warnings', () => {
    const box: GameBoxScore = {
      gameId: 'ncaa-2025-04-05-texas-tcu',
      date: '2025-04-05',
      venue: 'Disch-Falk Field',
      homeTeam: {
        teamId: 'texas',
        teamName: 'Texas Longhorns',
        conference: 'Big 12',
        runs: 5,
        hits: 8,
        errors: 1,
        lineScore: [0, 1, 0, 2, 0, 0, 1, 1, 0],
        batting: [makeBatter()],
        pitching: [makePitcher()],
      },
      awayTeam: {
        teamId: 'tcu',
        teamName: 'TCU Horned Frogs',
        conference: 'Big 12',
        runs: 3,
        hits: 6,
        errors: 0,
        lineScore: [1, 0, 0, 0, 0, 2, 0, 0, 0],
        batting: [makeBatter({ playerId: 'tcu1', name: 'TCU Batter' })],
        pitching: [makePitcher({ playerId: 'tcu-p1', name: 'TCU Pitcher' })],
      },
      innings: [],
      source: 'manual',
    };

    const result = ingestBoxScore(box);
    expect(result.success).toBe(true);
    expect(result.boxScore).not.toBeNull();
    expect(result.dedupKey).toBeTruthy();
  });

  it('warns when line score does not match runs', () => {
    const box: GameBoxScore = {
      gameId: 'ncaa-2025-04-05-texas-tcu',
      date: '2025-04-05',
      venue: 'Disch-Falk Field',
      homeTeam: {
        teamId: 'texas',
        teamName: 'Texas Longhorns',
        conference: 'Big 12',
        runs: 99,              // Intentional mismatch
        hits: 8,
        errors: 1,
        lineScore: [0, 1, 0],
        batting: [],
        pitching: [],
      },
      awayTeam: {
        teamId: 'tcu',
        teamName: 'TCU Horned Frogs',
        conference: 'Big 12',
        runs: 3,
        hits: 6,
        errors: 0,
        lineScore: [1, 0, 2],
        batting: [],
        pitching: [],
      },
      innings: [],
      source: 'manual',
    };

    const result = ingestBoxScore(box);
    expect(result.warnings.length).toBeGreaterThan(0);
    expect(result.warnings[0]).toContain('does not match');
  });
});
