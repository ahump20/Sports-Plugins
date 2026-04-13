/**
 * Metric computation for individual players.
 *
 * Accepts raw counting stats and returns a filled metrics object.
 * All formulas are sourced from the sabermetrics-analysis SKILL.md.
 */

import type { BatterLine, PitcherLine } from '../../../src/types/index.js';
import * as saber from '../../../src/utils/sabermetrics.js';
import { round } from '../../../src/utils/normalization.js';

// ---------------------------------------------------------------------------
// Batter metrics
// ---------------------------------------------------------------------------

export interface ComputedBatterMetrics {
  avg: number | null;
  obp: number | null;
  slg: number | null;
  ops: number | null;
  iso: number | null;
  babip: number | null;
  woba: number | null;
  wrcPlus: number | null;
  bbPercent: number | null;
  kPercent: number | null;
}

/**
 * Compute all standard batting metrics for a single player line.
 *
 * @param line    - Raw batter counting stats.
 * @param lgWoba  - League-average wOBA (defaults to ~0.320 for NCAA).
 */
export function computeBatterMetrics(
  line: BatterLine,
  lgWoba = 0.320,
): ComputedBatterMetrics {
  const pa = line.ab + line.bb + line.hbp + line.sf;
  const singles = line.h - line.doubles - line.triples - line.hr;
  const tb = saber.totalBases(line.h, line.doubles, line.triples, line.hr);

  const avgVal = saber.avg(line.h, line.ab);
  const obpVal = saber.obp(line.h, line.bb, line.hbp, line.ab, line.sf);
  const slgVal = saber.slg(tb, line.ab);
  const opsVal = obpVal != null && slgVal != null ? saber.ops(obpVal, slgVal) : null;
  const isoVal = slgVal != null && avgVal != null ? saber.iso(slgVal, avgVal) : null;
  const babipVal = saber.babip(line.h, line.hr, line.ab, line.k, line.sf);
  const wobaVal = saber.woba(
    line.bb, line.hbp, singles, line.doubles, line.triples, line.hr,
    line.ab, line.sf,
  );
  const wrcPlusVal = wobaVal != null ? saber.wrcPlus(wobaVal, lgWoba) : null;

  return {
    avg: avgVal != null ? round(avgVal, 3) : null,
    obp: obpVal != null ? round(obpVal, 3) : null,
    slg: slgVal != null ? round(slgVal, 3) : null,
    ops: opsVal != null ? round(opsVal, 3) : null,
    iso: isoVal != null ? round(isoVal, 3) : null,
    babip: babipVal != null ? round(babipVal, 3) : null,
    woba: wobaVal != null ? round(wobaVal, 3) : null,
    wrcPlus: wrcPlusVal != null ? round(wrcPlusVal, 0) : null,
    bbPercent: pa > 0 ? round((line.bb / pa) * 100, 1) : null,
    kPercent: pa > 0 ? round((line.k / pa) * 100, 1) : null,
  };
}

// ---------------------------------------------------------------------------
// Pitcher metrics
// ---------------------------------------------------------------------------

export interface ComputedPitcherMetrics {
  era: number | null;
  fip: number | null;
  whip: number | null;
  kPer9: number | null;
  bbPer9: number | null;
  kPerBb: number | null;
  lobPercent: number | null;
}

/**
 * Compute all standard pitching metrics for a single pitcher line.
 *
 * @param line - Raw pitcher counting stats with innings pitched already normalized.
 */
export function computePitcherMetrics(
  line: PitcherLine,
): ComputedPitcherMetrics {
  const ip = line.ip;

  return {
    era: roundOrNull(saber.era(line.er, ip), 2),
    fip: roundOrNull(saber.fip(line.hr, line.bb, line.hbp, line.k, ip), 2),
    whip: roundOrNull(saber.whip(line.bb, line.h, ip), 2),
    kPer9: roundOrNull(saber.kPer9(line.k, ip), 1),
    bbPer9: roundOrNull(saber.bbPer9(line.bb, ip), 1),
    kPerBb: roundOrNull(saber.kPerBb(line.k, line.bb), 2),
    lobPercent: roundOrNull(
      saber.lobPercent(line.h, line.bb, line.hbp, line.r, line.hr),
      3,
    ),
  };
}

function roundOrNull(val: number | null, decimals: number): number | null {
  return val != null ? round(val, decimals) : null;
}
