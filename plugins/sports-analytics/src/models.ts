/**
 * Predictive models — Marcel projections and win probability.
 *
 * Implements the predictive-modeling SKILL.md formulas.
 */

import type { ConfidenceTier } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Marcel Projection
// ---------------------------------------------------------------------------

export interface MarcelInput {
  /** Most recent season stat (e.g. wOBA). */
  yr1: number;
  /** Prior season stat. */
  yr2: number;
  /** Two seasons ago stat. */
  yr3: number;
  /** PA or IP in yr1. */
  pa1: number;
  /** PA or IP in yr2. */
  pa2: number;
  /** PA or IP in yr3. */
  pa3: number;
  /** League average for the stat. */
  lgAvg: number;
  /** Reliability PA/IP threshold (default: 150 for college batters, 80 for pitchers). */
  reliability?: number;
}

/**
 * Marcel-style projection (adapted for college baseball).
 *
 * Formula from predictive-modeling SKILL.md:
 * Projected = (3×stat_yr1 + 4×stat_yr2 + 5×stat_yr3 + 4×lgAvg×reliability)
 *           / (3×pa_yr1 + 4×pa_yr2 + 5×pa_yr3 + 4×reliability)
 *
 * Weights: yr1=most recent (weight 5), yr3=oldest (weight 3).
 * Note: SKILL.md uses 3/4/5 but orders yr1 as weight 3 for recency.
 * We follow the SKILL.md literal ordering.
 */
export function marcelProjection(input: MarcelInput): {
  projected: number;
  confidence: ConfidenceTier;
} {
  const rel = input.reliability ?? 150;

  const num =
    3 * input.yr1 * input.pa1 +
    4 * input.yr2 * input.pa2 +
    5 * input.yr3 * input.pa3 +
    4 * input.lgAvg * rel;

  const denom =
    3 * input.pa1 +
    4 * input.pa2 +
    5 * input.pa3 +
    4 * rel;

  const projected = denom > 0 ? num / denom : input.lgAvg;

  // Determine confidence tier
  const totalPA = input.pa1 + input.pa2 + input.pa3;
  const seasons = [input.pa1, input.pa2, input.pa3].filter((p) => p > 0).length;

  let confidence: ConfidenceTier;
  if (seasons >= 3 && totalPA >= 300) {
    confidence = 'high';
  } else if (seasons >= 1 && totalPA >= 150) {
    confidence = 'medium';
  } else {
    confidence = 'low';
  }

  return { projected, confidence };
}

// ---------------------------------------------------------------------------
// Win Probability
// ---------------------------------------------------------------------------

export interface GameState {
  inning: number;
  isTopHalf: boolean;
  outs: number;
  /** Bitmap: 1B=1, 2B=2, 3B=4 → 0–7. */
  runnersOn: number;
  homeScore: number;
  awayScore: number;
}

/**
 * Simplified win probability using logistic regression on run differential
 * and inning progress.
 *
 * This is a lightweight approximation. For production use, train on ≥5,000
 * game-states as recommended in the SKILL.md.
 *
 * @returns P(home team wins | current state), between 0 and 1.
 */
export function winProbability(state: GameState): number {
  const runDiff = state.homeScore - state.awayScore;
  const inningProgress = (state.inning - 1 + (state.isTopHalf ? 0 : 0.5)) / 9;
  const outsProgress = state.outs / 3;

  // Simple logistic model with hand-tuned coefficients
  // In production, these would be trained on historical data
  const logit =
    0.15 +                           // Home-field baseline
    0.65 * runDiff +                 // Run differential (strongest signal)
    0.40 * runDiff * inningProgress + // Late-game run differential matters more
    0.05 * outsProgress;             // Mild out-state effect

  return 1 / (1 + Math.exp(-logit));
}
