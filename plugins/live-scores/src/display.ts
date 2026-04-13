/**
 * Display helpers for the scoreboard UI.
 *
 * Sport badge colors and period/clock formatting from the
 * scoreboard-ui SKILL.md.
 */

import type { Sport } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Sport Badge Colors (from SKILL.md)
// ---------------------------------------------------------------------------

export const SPORT_BADGE_COLORS: Record<Sport, { bg: string; text: string }> = {
  'college-baseball': { bg: 'bg-orange-600', text: 'text-white' },
  'mlb':              { bg: 'bg-blue-700',   text: 'text-white' },
  'nfl':              { bg: 'bg-slate-700',  text: 'text-white' },
  'nba':              { bg: 'bg-red-700',    text: 'text-white' },
  'cfb':              { bg: 'bg-amber-700',  text: 'text-white' },
};

// ---------------------------------------------------------------------------
// Period / Clock formatting
// ---------------------------------------------------------------------------

/**
 * Format a baseball inning for display.
 * @param inning    - 1-indexed inning number.
 * @param isTopHalf - True for top half, false for bottom.
 */
export function formatPeriod(inning: number, isTopHalf: boolean): string {
  const half = isTopHalf ? 'Top' : 'Bot';
  const suffix = ordinalSuffix(inning);
  return `${half} ${inning}${suffix}`;
}

/**
 * Format a game clock string (e.g. minutes:seconds).
 * Pass-through if already formatted.
 */
export function formatClock(raw: string): string {
  // If it's already formatted (e.g. "12:34"), pass through
  if (/^\d{1,2}:\d{2}$/.test(raw)) return raw;

  // If it's seconds, convert
  const seconds = parseInt(raw, 10);
  if (!isNaN(seconds)) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  return raw;
}

function ordinalSuffix(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return 'st';
  if (mod10 === 2 && mod100 !== 12) return 'nd';
  if (mod10 === 3 && mod100 !== 13) return 'rd';
  return 'th';
}
