/**
 * Pitcher evaluation — pitch mix, role recommendations, and series cards.
 *
 * Implements the pitcher-analytics SKILL.md logic.
 */

import type { PitcherLine } from '../../../src/types/index.js';
import { computePitcherMetrics, type ComputedPitcherMetrics } from './metrics.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type PitchType =
  | 'four-seam'
  | 'two-seam'
  | 'cutter'
  | 'curveball'
  | 'slider'
  | 'changeup'
  | 'splitter'
  | 'other';

export interface PitchMix {
  pitch: PitchType;
  /** Usage rate as a fraction (0–1). */
  usage: number;
  /** Whiff rate on this pitch, if available. */
  whiffPercent?: number;
}

export type PitcherRole =
  | 'friday-starter'
  | 'saturday-starter'
  | 'sunday-starter'
  | 'midweek-starter'
  | 'multi-inning-reliever'
  | 'closer'
  | 'high-leverage';

export interface PitcherEvaluation {
  name: string;
  role: PitcherRole;
  metrics: ComputedPitcherMetrics;
  arsenal: PitchMix[];
  /** One-sentence key tendency. */
  tendency: string;
  /** Recommended role based on thresholds from SKILL.md. */
  recommendedRole: 'starter' | 'reliever';
  /** Flags for platoon vulnerability thresholds. */
  flags: string[];
}

// ---------------------------------------------------------------------------
// Role recommendation thresholds (from pitcher-analytics SKILL.md)
// ---------------------------------------------------------------------------

interface RoleThresholds {
  minArsenalDepth: number;
  maxBbPer9: number;
}

const STARTER_THRESHOLDS: RoleThresholds = {
  minArsenalDepth: 3,
  maxBbPer9: 3.5,
};

const RELIEVER_THRESHOLDS: RoleThresholds = {
  minArsenalDepth: 2,
  maxBbPer9: 4.5,
};

// ---------------------------------------------------------------------------
// Core evaluation
// ---------------------------------------------------------------------------

/**
 * Evaluate a pitcher and produce a structured card.
 *
 * @param line      - Pitcher's counting stats.
 * @param role      - Current role assignment.
 * @param arsenal   - Known pitch mix (may be empty if data is unavailable).
 */
export function evaluatePitcher(
  line: PitcherLine,
  role: PitcherRole,
  arsenal: PitchMix[] = [],
): PitcherEvaluation {
  const metrics = computePitcherMetrics(line);
  const flags: string[] = [];

  // Determine recommended role based on thresholds
  const arsenalDepth = arsenal.length || 2; // unknown arsenal defaults to 2
  const bbPer9 = metrics.bbPer9 ?? 99;

  const fitsStarter =
    arsenalDepth >= STARTER_THRESHOLDS.minArsenalDepth &&
    bbPer9 <= STARTER_THRESHOLDS.maxBbPer9;

  const fitsReliever =
    arsenalDepth >= RELIEVER_THRESHOLDS.minArsenalDepth &&
    bbPer9 <= RELIEVER_THRESHOLDS.maxBbPer9;

  let recommendedRole: 'starter' | 'reliever';
  if (fitsStarter) {
    recommendedRole = 'starter';
  } else if (fitsReliever) {
    recommendedRole = 'reliever';
  } else {
    recommendedRole = 'reliever';
    flags.push('High walk rate — may limit high-leverage usage.');
  }

  // Check for over-reliance on one pitch
  const dominantPitch = arsenal.find((p) => p.usage > 0.70);
  if (dominantPitch) {
    flags.push(
      `Over-relies on ${dominantPitch.pitch} (${(dominantPitch.usage * 100).toFixed(0)}% usage).`,
    );
  }

  // Build tendency sentence
  const tendency = buildTendency(metrics, arsenal);

  return {
    name: line.name,
    role,
    metrics,
    arsenal,
    tendency,
    recommendedRole,
    flags,
  };
}

function buildTendency(
  metrics: ComputedPitcherMetrics,
  arsenal: PitchMix[],
): string {
  const parts: string[] = [];

  if (metrics.kPer9 != null && metrics.kPer9 >= 9.0) {
    parts.push('high strikeout rate');
  }
  if (metrics.bbPer9 != null && metrics.bbPer9 <= 2.0) {
    parts.push('elite control');
  } else if (metrics.bbPer9 != null && metrics.bbPer9 >= 4.0) {
    parts.push('walk issues');
  }

  const bestPitch = arsenal
    .filter((p) => p.whiffPercent != null)
    .sort((a, b) => (b.whiffPercent ?? 0) - (a.whiffPercent ?? 0))[0];

  if (bestPitch) {
    parts.push(`best pitch is the ${bestPitch.pitch}`);
  }

  if (parts.length === 0) {
    return 'Metrics pending — insufficient sample for tendency call.';
  }

  return parts.join(', ') + '.';
}
