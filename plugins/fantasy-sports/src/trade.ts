/**
 * Trade analyzer — structured trade evaluation.
 *
 * Implements the trade-analyzer SKILL.md framework:
 * - Always reach a verdict (never "it depends")
 * - Always consider scoring format, record, and roster context
 * - Provide a counter when verdict is "counter"
 */

import type { ScoringFormat, TradeVerdict } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ValueTier = 1 | 2 | 3 | 4;

export interface TradePlayer {
  name: string;
  position: string;
  /** Value tier (1 = elite, 4 = depth piece). */
  tier: ValueTier;
  /** Recent weekly points average. */
  recentAvg: number;
}

export interface TradeInput {
  giving: TradePlayer[];
  getting: TradePlayer[];
  scoring: ScoringFormat;
  record: string;
  /** User's weakest roster position. */
  rosterNeed: string;
  /** Current NFL/MLB/NBA week or equivalent. */
  week: number;
  /** Playoff implications text. */
  playoffNote?: string;
}

export interface TradeResult {
  rawValue: 'edge-you' | 'even' | 'edge-them' | 'clear-winner';
  verdict: TradeVerdict;
  reasoning: string;
  counter?: string;
}

// ---------------------------------------------------------------------------
// Tier-based value scoring (from trade-analyzer SKILL.md)
// ---------------------------------------------------------------------------

const TIER_VALUES: Record<ValueTier, number> = {
  1: 100,
  2: 65,
  3: 35,
  4: 15,
};

function sumTierValue(players: TradePlayer[]): number {
  return players.reduce((sum, p) => sum + TIER_VALUES[p.tier], 0);
}

// ---------------------------------------------------------------------------
// Core analysis
// ---------------------------------------------------------------------------

/**
 * Analyze a trade and produce a structured verdict.
 *
 * Per SKILL.md hard rules:
 * - Never give a verdict without seeing both sides.
 * - Never analyze without scoring format.
 * - Never recommend a trade that weakens the user's weakest position.
 */
export function analyzeTrade(input: TradeInput): TradeResult {
  if (input.giving.length === 0 || input.getting.length === 0) {
    throw new Error('Trade analysis requires at least one player on each side.');
  }

  const givingValue = sumTierValue(input.giving);
  const gettingValue = sumTierValue(input.getting);
  const diff = gettingValue - givingValue;

  // Determine raw value assessment
  let rawValue: TradeResult['rawValue'];
  if (diff > 30) rawValue = 'clear-winner';
  else if (diff > 10) rawValue = 'edge-you';
  else if (diff < -30) rawValue = 'clear-winner';
  else if (diff < -10) rawValue = 'edge-them';
  else rawValue = 'even';

  // Check roster need
  const weakensNeed = input.giving.some(
    (p) => p.position.toLowerCase() === input.rosterNeed.toLowerCase(),
  ) && !input.getting.some(
    (p) => p.position.toLowerCase() === input.rosterNeed.toLowerCase(),
  );

  // Build verdict
  let verdict: TradeVerdict;
  const reasons: string[] = [];

  if (weakensNeed) {
    verdict = 'decline';
    reasons.push(
      `This trade gives up a ${input.rosterNeed} without getting one back — weakens your thinnest position.`,
    );
  } else if (diff > 10) {
    verdict = 'accept';
    reasons.push(`You gain a net value advantage of ~${diff} tier points.`);
  } else if (diff < -10) {
    verdict = 'counter';
    reasons.push(`You're giving up more value than you're receiving.`);
  } else {
    // Even — decide based on context
    if (input.rosterNeed && input.getting.some((p) => p.position.toLowerCase() === input.rosterNeed.toLowerCase())) {
      verdict = 'accept';
      reasons.push(`Even trade, but it fills your ${input.rosterNeed} need.`);
    } else {
      verdict = 'decline';
      reasons.push(`Even trade with no clear roster improvement. Hold.`);
    }
  }

  // Add context
  reasons.push(`Scoring: ${input.scoring}. Week ${input.week}, record ${input.record}.`);

  // Build counter suggestion if verdict is counter
  let counter: string | undefined;
  if (verdict === 'counter') {
    const bestGetting = input.getting.sort((a, b) => TIER_VALUES[b.tier] - TIER_VALUES[a.tier])[0];
    counter = `Ask for an upgrade at ${input.rosterNeed} alongside ${bestGetting.name} to close the value gap.`;
  }

  return {
    rawValue: diff >= 0 ? rawValue : (rawValue === 'clear-winner' ? 'edge-them' : rawValue),
    verdict,
    reasoning: reasons.join(' '),
    counter,
  };
}
