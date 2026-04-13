/**
 * Waiver wire — ranking and recommendation engine.
 *
 * Implements the waiver-wire SKILL.md priority framework:
 * 1. Opportunity score (highest weight)
 * 2. Productivity trend
 * 3. Matchup favorability
 * 4. Injury buffer
 * 5. Roster fit
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface WaiverCandidate {
  name: string;
  position: string;
  team: string;
  /** Projected snaps / targets / touches per game. */
  opportunityScore: number;
  /** 4-week trend: positive = improving, negative = declining. */
  trend: number;
  /** Matchup favorability this week (0–10, higher = better). */
  matchupScore: number;
  /** Does this player hedge an injury risk on the user's roster? */
  hedgesInjury: boolean;
  /** Does this player fill a roster need? */
  fillsNeed: boolean;
  /** Roster % owned (0–100). Over 50 = likely rostered. */
  rosterPercent: number;
}

export interface RankedWaiverAdd {
  priority: number;
  candidate: WaiverCandidate;
  /** Composite score used for ranking. */
  score: number;
  /** Whether this is a 1-week streaming play vs. season add. */
  isStreaming: boolean;
}

// ---------------------------------------------------------------------------
// Scoring weights (from SKILL.md priority framework)
// ---------------------------------------------------------------------------

const WEIGHTS = {
  opportunity: 0.40,
  trend: 0.20,
  matchup: 0.15,
  injuryHedge: 0.10,
  rosterFit: 0.15,
};

function computeScore(c: WaiverCandidate): number {
  return (
    WEIGHTS.opportunity * c.opportunityScore +
    WEIGHTS.trend * Math.max(c.trend, 0) * 10 + // Normalize trend
    WEIGHTS.matchup * c.matchupScore +
    WEIGHTS.injuryHedge * (c.hedgesInjury ? 10 : 0) +
    WEIGHTS.rosterFit * (c.fillsNeed ? 10 : 0)
  );
}

// ---------------------------------------------------------------------------
// Core ranking
// ---------------------------------------------------------------------------

/**
 * Rank a list of waiver wire candidates by composite score.
 *
 * Per SKILL.md hard rules:
 * - Do not recommend a player rostered in > 50% of leagues.
 * - Require a 2-week trend minimum for non-injury adds.
 *
 * @param candidates - Available players on the waiver wire.
 * @param maxResults - Maximum number of recommendations (default: 5).
 */
export function rankWaiverAdds(
  candidates: WaiverCandidate[],
  maxResults = 5,
): RankedWaiverAdd[] {
  // Filter out players rostered in > 50% of leagues
  const eligible = candidates.filter((c) => c.rosterPercent <= 50);

  // Score and sort
  const scored = eligible.map((c) => ({
    candidate: c,
    score: computeScore(c),
    // Streaming if matchup score is high but trend is flat or negative
    isStreaming: c.matchupScore >= 7 && c.trend <= 0,
  }));

  scored.sort((a, b) => b.score - a.score);

  return scored.slice(0, maxResults).map((s, i) => ({
    priority: i + 1,
    candidate: s.candidate,
    score: Math.round(s.score * 100) / 100,
    isStreaming: s.isStreaming,
  }));
}
