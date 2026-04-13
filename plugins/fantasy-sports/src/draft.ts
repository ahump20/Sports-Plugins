/**
 * Draft strategy — positional scarcity and pick-based planning.
 *
 * Implements the draft-assistant SKILL.md templates.
 */

import type { ScoringFormat, DraftFormat } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DraftContext {
  sport: 'nfl' | 'mlb' | 'nba';
  format: DraftFormat;
  scoring: ScoringFormat;
  leagueSize: number;
  /** 1-indexed draft position. */
  pickPosition: number;
  /** Is this a superflex league? */
  superflex?: boolean;
}

export interface DraftPlan {
  /** Overall strategy label. */
  strategy: string;
  /** Round-by-round positional targets. */
  rounds: RoundTarget[];
  /** Key strategic notes. */
  notes: string[];
}

export interface RoundTarget {
  round: number;
  /** Approximate pick number. */
  pick: number;
  /** Target position(s). */
  targetPositions: string[];
  /** Guidance for this pick. */
  guidance: string;
}

// ---------------------------------------------------------------------------
// Pick calculation
// ---------------------------------------------------------------------------

function pickForRound(position: number, round: number, leagueSize: number): number {
  // Snake draft: odd rounds go ascending, even rounds go descending
  if (round % 2 === 1) {
    return (round - 1) * leagueSize + position;
  }
  return round * leagueSize - position + 1;
}

// ---------------------------------------------------------------------------
// Strategy templates (from draft-assistant SKILL.md)
// ---------------------------------------------------------------------------

function earlyPickStrategy(ctx: DraftContext): DraftPlan {
  return {
    strategy: 'Early Pick (1–3) — Anchor with Elite RB/WR',
    rounds: [
      { round: 1, pick: pickForRound(ctx.pickPosition, 1, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Take the best RB or WR available. Do not reach.' },
      { round: 2, pick: pickForRound(ctx.pickPosition, 2, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Fill the other elite slot (RB if you took WR, or vice versa).' },
      { round: 3, pick: pickForRound(ctx.pickPosition, 3, ctx.leagueSize), targetPositions: ['RB', 'WR', 'TE'], guidance: 'RB depth or elite TE if available.' },
      { round: 4, pick: pickForRound(ctx.pickPosition, 4, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Continue building positional depth.' },
      { round: 5, pick: pickForRound(ctx.pickPosition, 5, ctx.leagueSize), targetPositions: ['QB', 'WR'], guidance: ctx.superflex ? 'QB is critical in superflex.' : 'Target QB value here.' },
    ],
    notes: [
      'Early picks have the luxury of anchoring with a top-8 RB or WR.',
      'Plan to miss QB in rounds 1–4; value emerges in rounds 5–6.',
      'Build RB depth aggressively in rounds 3–5.',
    ],
  };
}

function midPickStrategy(ctx: DraftContext): DraftPlan {
  return {
    strategy: 'Middle Pick (4–8) — Flexible WR/RB Balance',
    rounds: [
      { round: 1, pick: pickForRound(ctx.pickPosition, 1, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Best available. If top RBs are gone, pivot to WR.' },
      { round: 2, pick: pickForRound(ctx.pickPosition, 2, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Fill the gap from round 1.' },
      { round: 3, pick: pickForRound(ctx.pickPosition, 3, ctx.leagueSize), targetPositions: ['WR', 'TE'], guidance: 'Elite TE window. If missed, load WR.' },
      { round: 4, pick: pickForRound(ctx.pickPosition, 4, ctx.leagueSize), targetPositions: ['RB', 'QB'], guidance: 'RB depth or QB if superflex.' },
      { round: 5, pick: pickForRound(ctx.pickPosition, 5, ctx.leagueSize), targetPositions: ['QB', 'WR', 'RB'], guidance: 'Best available; fill remaining gaps.' },
    ],
    notes: [
      'Zero-RB is viable from mid positions — load WRs through round 4, then target upside RBs.',
      'Elite TE in rounds 3–4 compounds positional advantage.',
      'Avoid reaching for a declining RB just to fill a position.',
    ],
  };
}

function latePickStrategy(ctx: DraftContext): DraftPlan {
  return {
    strategy: 'Late Pick (9–12) — Exploit the Turn',
    rounds: [
      { round: 1, pick: pickForRound(ctx.pickPosition, 1, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Take BPA. Positional runs will thin your options.' },
      { round: 2, pick: pickForRound(ctx.pickPosition, 2, ctx.leagueSize), targetPositions: ['RB', 'WR'], guidance: 'Two picks in a row (the turn) — roster the thinning position.' },
      { round: 3, pick: pickForRound(ctx.pickPosition, 3, ctx.leagueSize), targetPositions: ['WR', 'TE', 'RB'], guidance: 'Best available. Deep-value WRs emerge here.' },
      { round: 4, pick: pickForRound(ctx.pickPosition, 4, ctx.leagueSize), targetPositions: ['QB', 'RB'], guidance: ctx.superflex ? 'Top-5 QB window — take it.' : 'QB value or RB depth.' },
      { round: 5, pick: pickForRound(ctx.pickPosition, 5, ctx.leagueSize), targetPositions: ['WR', 'RB'], guidance: 'Prioritize upside over floor in late rounds.' },
    ],
    notes: [
      'Late picks produce deep-value WRs and handcuffs — prioritize upside over floor.',
      'The turn (two picks in a row) is your biggest strategic advantage.',
      'Positional runs will happen before your picks — plan around them.',
    ],
  };
}

// ---------------------------------------------------------------------------
// Core
// ---------------------------------------------------------------------------

/**
 * Generate a draft strategy plan based on context.
 *
 * Per SKILL.md: strategy must be specific to position, scoring, league
 * size, and pick. Never give generic "best player available."
 */
export function draftStrategy(ctx: DraftContext): DraftPlan {
  if (ctx.pickPosition <= 3) {
    return earlyPickStrategy(ctx);
  } else if (ctx.pickPosition <= 8) {
    return midPickStrategy(ctx);
  } else {
    return latePickStrategy(ctx);
  }
}
