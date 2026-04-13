/**
 * Stat formatting helpers aligned with stats-visualization SKILL.md rules.
 *
 * ERA → 2 decimal places
 * wOBA → 3 decimal places
 * K% → 1 decimal + "%"
 */

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

/** Format ERA to 2 decimal places. */
export function formatERA(value: number): string {
  return value.toFixed(2);
}

/** Format wOBA to 3 decimal places (no leading zero, e.g. ".345"). */
export function formatWoba(value: number): string {
  return value.toFixed(3);
}

/** Format a percentage to 1 decimal place with % suffix. */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

// ---------------------------------------------------------------------------
// Tier Classification
// ---------------------------------------------------------------------------

export type StatTier = 'elite' | 'above-avg' | 'average' | 'below-avg';

interface TierBands {
  elite: number;
  aboveAvg: number;
  average: number;
}

const PITCHING_TIERS: Record<string, TierBands & { direction: 'lower-better' | 'higher-better' }> = {
  era:  { elite: 2.50, aboveAvg: 3.50, average: 4.50, direction: 'lower-better' },
  fip:  { elite: 2.80, aboveAvg: 3.60, average: 4.50, direction: 'lower-better' },
  kPer9: { elite: 11.0, aboveAvg: 9.0, average: 7.0, direction: 'higher-better' },
  bbPer9: { elite: 2.0, aboveAvg: 3.0, average: 4.0, direction: 'lower-better' },
  whip: { elite: 1.00, aboveAvg: 1.20, average: 1.40, direction: 'lower-better' },
};

const HITTING_TIERS: Record<string, TierBands & { direction: 'higher-better' }> = {
  wrcPlus: { elite: 140, aboveAvg: 115, average: 85, direction: 'higher-better' },
  ops: { elite: 0.950, aboveAvg: 0.850, average: 0.720, direction: 'higher-better' },
  iso: { elite: 0.220, aboveAvg: 0.160, average: 0.100, direction: 'higher-better' },
};

/**
 * Classify a metric value into a tier based on the college baselines
 * defined in the sabermetrics-analysis SKILL.md.
 *
 * @param stat  - Stat name (e.g. "era", "wrcPlus").
 * @param value - The numeric value.
 */
export function tierLabel(stat: string, value: number): StatTier {
  const bands = { ...PITCHING_TIERS, ...HITTING_TIERS }[stat];
  if (!bands) return 'average'; // unknown stat → default

  if (bands.direction === 'lower-better') {
    if (value < bands.elite) return 'elite';
    if (value < bands.aboveAvg) return 'above-avg';
    if (value < bands.average) return 'average';
    return 'below-avg';
  }

  // higher-better
  if (value > bands.elite) return 'elite';
  if (value > bands.aboveAvg) return 'above-avg';
  if (value > bands.average) return 'average';
  return 'below-avg';
}
