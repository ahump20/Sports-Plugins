/**
 * Lineup optimizer — batting order construction and platoon logic.
 *
 * Implements the lineup-optimizer SKILL.md framework.
 */

import type { BatterLine } from '../../../src/types/index.js';
import { computeBatterMetrics, type ComputedBatterMetrics } from './metrics.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface LineupSlot {
  /** 1-indexed batting order position. */
  slot: number;
  player: BatterLine;
  metrics: ComputedBatterMetrics;
  /** Short rationale for this slot assignment. */
  note: string;
}

export interface LineupCard {
  /** Opponent team name. */
  opponent: string;
  /** Opponent starter's throwing hand. */
  opponentStarterHand: 'LHP' | 'RHP';
  /** Ordered slots 1–9. */
  lineup: LineupSlot[];
  /** 2-3 sentence rationale for non-obvious decisions. */
  rationale: string;
}

// ---------------------------------------------------------------------------
// Slot philosophy (from lineup-optimizer SKILL.md)
// ---------------------------------------------------------------------------

interface SlotCriteria {
  slot: number;
  description: string;
  /** Scoring function: higher = better fit for this slot. */
  score: (m: ComputedBatterMetrics) => number;
}

const SLOT_CRITERIA: SlotCriteria[] = [
  {
    slot: 1,
    description: 'Get on base — high OBP, low K%',
    score: (m) => (m.obp ?? 0) * 100 - (m.kPercent ?? 30),
  },
  {
    slot: 2,
    description: 'Advance runners — OBP + contact',
    score: (m) => ((m.obp ?? 0) + (m.avg ?? 0)) * 50,
  },
  {
    slot: 3,
    description: 'Best overall hitter — highest wRC+',
    score: (m) => m.wrcPlus ?? 0,
  },
  {
    slot: 4,
    description: 'Most power — high ISO',
    score: (m) => (m.iso ?? 0) * 100 + (m.slg ?? 0) * 50,
  },
  {
    slot: 5,
    description: 'Secondary run producer — ISO + walks',
    score: (m) => (m.iso ?? 0) * 80 + (m.bbPercent ?? 0),
  },
  {
    slot: 6,
    description: 'Contact depth — OBP-oriented',
    score: (m) => (m.obp ?? 0) * 80 - (m.kPercent ?? 30) * 0.5,
  },
  {
    slot: 7,
    description: 'Balance / platoon advantage',
    score: (m) => (m.ops ?? 0) * 50,
  },
  {
    slot: 8,
    description: 'Weakest bat — minimize exposure',
    score: (m) => -((m.wrcPlus ?? 100) - 100), // lower wRC+ = better fit for slot 8
  },
  {
    slot: 9,
    description: 'Modern: second leadoff — high OBP',
    score: (m) => (m.obp ?? 0) * 60,
  },
];

// ---------------------------------------------------------------------------
// Core optimizer
// ---------------------------------------------------------------------------

/**
 * Produce a recommended lineup card from a set of available batters.
 *
 * Uses a greedy slot-assignment algorithm: for each slot (1–9), pick the
 * remaining player with the highest score for that slot's criteria.
 *
 * @param batters              - Available players (at least 9).
 * @param opponent             - Opponent name.
 * @param opponentStarterHand - "LHP" or "RHP".
 * @param lgWoba               - League-average wOBA for wRC+ calculation.
 */
export function optimizeLineup(
  batters: BatterLine[],
  opponent: string,
  opponentStarterHand: 'LHP' | 'RHP',
  lgWoba = 0.320,
): LineupCard {
  if (batters.length < 9) {
    throw new Error(
      `Need at least 9 batters to build a lineup, got ${batters.length}.`,
    );
  }

  // Pre-compute metrics for every batter
  const pool = batters.map((b) => ({
    player: b,
    metrics: computeBatterMetrics(b, lgWoba),
    assigned: false,
  }));

  const lineup: LineupSlot[] = [];

  for (const criteria of SLOT_CRITERIA) {
    // Score each unassigned player
    let bestIdx = -1;
    let bestScore = -Infinity;

    for (let i = 0; i < pool.length; i++) {
      if (pool[i].assigned) continue;
      const score = criteria.score(pool[i].metrics);
      if (score > bestScore) {
        bestScore = score;
        bestIdx = i;
      }
    }

    if (bestIdx === -1) break; // should not happen with ≥9 batters

    pool[bestIdx].assigned = true;
    lineup.push({
      slot: criteria.slot,
      player: pool[bestIdx].player,
      metrics: pool[bestIdx].metrics,
      note: criteria.description,
    });
  }

  const rationale = buildRationale(lineup, opponentStarterHand);

  return {
    opponent,
    opponentStarterHand,
    lineup,
    rationale,
  };
}

function buildRationale(
  lineup: LineupSlot[],
  hand: 'LHP' | 'RHP',
): string {
  const slot2 = lineup.find((s) => s.slot === 2);
  const slot9 = lineup.find((s) => s.slot === 9);

  const parts: string[] = [];

  if (slot2) {
    parts.push(
      `Slot 2 (${slot2.player.name}) selected for contact + OBP (${slot2.metrics.obp ?? '—'} OBP).`,
    );
  }
  if (slot9) {
    parts.push(
      `Slot 9 uses the modern approach: ${slot9.player.name} (${slot9.metrics.obp ?? '—'} OBP) as a second leadoff bat.`,
    );
  }
  parts.push(`Lineup built against a ${hand} opponent starter.`);

  return parts.join(' ');
}
