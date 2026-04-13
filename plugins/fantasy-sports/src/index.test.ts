import { describe, it, expect } from 'vitest';
import { analyzeTrade } from './trade.js';
import { rankWaiverAdds, type WaiverCandidate } from './waiver.js';
import { draftStrategy } from './draft.js';

// ---------------------------------------------------------------------------
// Trade Analyzer
// ---------------------------------------------------------------------------

describe('analyzeTrade', () => {
  it('recommends accept when getting value is significantly higher', () => {
    const result = analyzeTrade({
      giving: [{ name: 'Player A', position: 'WR', tier: 2, recentAvg: 14 }],
      getting: [{ name: 'Player B', position: 'RB', tier: 1, recentAvg: 22 }],
      scoring: 'ppr',
      record: '5-3',
      rosterNeed: 'RB',
      week: 9,
    });
    expect(result.verdict).toBe('accept');
  });

  it('recommends decline when giving up value at roster need', () => {
    const result = analyzeTrade({
      giving: [{ name: 'Player A', position: 'RB', tier: 1, recentAvg: 22 }],
      getting: [{ name: 'Player B', position: 'WR', tier: 2, recentAvg: 14 }],
      scoring: 'ppr',
      record: '4-4',
      rosterNeed: 'RB', // Giving up an RB without getting one back
      week: 9,
    });
    expect(result.verdict).toBe('decline');
    expect(result.reasoning).toContain('weakens');
  });

  it('provides a counter when value gap is moderate', () => {
    const result = analyzeTrade({
      giving: [
        { name: 'Player A', position: 'WR', tier: 1, recentAvg: 22 },
      ],
      getting: [
        { name: 'Player B', position: 'WR', tier: 3, recentAvg: 10 },
      ],
      scoring: 'standard',
      record: '3-5',
      rosterNeed: 'TE',
      week: 9,
    });
    expect(result.verdict).toBe('counter');
    expect(result.counter).toBeTruthy();
  });

  it('throws when trade sides are empty', () => {
    expect(() =>
      analyzeTrade({
        giving: [],
        getting: [{ name: 'X', position: 'WR', tier: 2, recentAvg: 10 }],
        scoring: 'ppr',
        record: '5-3',
        rosterNeed: 'RB',
        week: 9,
      }),
    ).toThrow('at least one player');
  });
});

// ---------------------------------------------------------------------------
// Waiver Wire
// ---------------------------------------------------------------------------

describe('rankWaiverAdds', () => {
  const candidates: WaiverCandidate[] = [
    { name: 'Top Add', position: 'RB', team: 'DAL', opportunityScore: 9, trend: 2, matchupScore: 8, hedgesInjury: true, fillsNeed: true, rosterPercent: 20 },
    { name: 'Streaming QB', position: 'QB', team: 'MIA', opportunityScore: 5, trend: -1, matchupScore: 9, hedgesInjury: false, fillsNeed: false, rosterPercent: 15 },
    { name: 'Already Rostered', position: 'WR', team: 'KC', opportunityScore: 10, trend: 3, matchupScore: 10, hedgesInjury: true, fillsNeed: true, rosterPercent: 75 },
    { name: 'Decent Flex', position: 'WR', team: 'BUF', opportunityScore: 6, trend: 1, matchupScore: 5, hedgesInjury: false, fillsNeed: true, rosterPercent: 30 },
  ];

  it('filters out players rostered in > 50% of leagues', () => {
    const results = rankWaiverAdds(candidates);
    const names = results.map((r) => r.candidate.name);
    expect(names).not.toContain('Already Rostered');
  });

  it('ranks by composite score', () => {
    const results = rankWaiverAdds(candidates);
    expect(results[0].candidate.name).toBe('Top Add');
    expect(results[0].priority).toBe(1);
  });

  it('identifies streaming plays', () => {
    const results = rankWaiverAdds(candidates);
    const streaming = results.find((r) => r.candidate.name === 'Streaming QB');
    expect(streaming?.isStreaming).toBe(true);
  });

  it('respects maxResults', () => {
    const results = rankWaiverAdds(candidates, 2);
    expect(results.length).toBeLessThanOrEqual(2);
  });
});

// ---------------------------------------------------------------------------
// Draft Strategy
// ---------------------------------------------------------------------------

describe('draftStrategy', () => {
  it('returns early-pick strategy for pick 1', () => {
    const plan = draftStrategy({
      sport: 'nfl',
      format: 'snake',
      scoring: 'ppr',
      leagueSize: 12,
      pickPosition: 1,
    });
    expect(plan.strategy).toContain('Early');
    expect(plan.rounds.length).toBeGreaterThanOrEqual(5);
  });

  it('returns mid-pick strategy for pick 6', () => {
    const plan = draftStrategy({
      sport: 'nfl',
      format: 'snake',
      scoring: 'ppr',
      leagueSize: 12,
      pickPosition: 6,
    });
    expect(plan.strategy).toContain('Middle');
  });

  it('returns late-pick strategy for pick 11', () => {
    const plan = draftStrategy({
      sport: 'nfl',
      format: 'snake',
      scoring: 'half-ppr',
      leagueSize: 12,
      pickPosition: 11,
    });
    expect(plan.strategy).toContain('Late');
  });

  it('includes superflex note when applicable', () => {
    const plan = draftStrategy({
      sport: 'nfl',
      format: 'snake',
      scoring: 'ppr',
      leagueSize: 12,
      pickPosition: 2,
      superflex: true,
    });
    const superflexRound = plan.rounds.find((r) => r.guidance.toLowerCase().includes('superflex'));
    expect(superflexRound).toBeTruthy();
  });
});
