/**
 * Core sabermetric computation functions.
 *
 * Every formula mirrors the definitions in the college-baseball-sabermetrics
 * SKILL.md files. Functions accept raw counting stats and return computed
 * metrics — never raw database rows.
 */

// ---------------------------------------------------------------------------
// Pitching Metrics
// ---------------------------------------------------------------------------

/**
 * Earned Run Average.
 * ERA = (ER / IP) × 9
 */
export function era(er: number, ip: number): number | null {
  if (ip <= 0) return null;
  return (er / ip) * 9;
}

/**
 * Fielding Independent Pitching.
 * FIP = ((13×HR + 3×(BB+HBP) − 2×K) / IP) + FIP constant
 *
 * @param fipConstant - League-specific constant (~3.10 for NCAA, ~3.20 for MLB).
 */
export function fip(
  hr: number,
  bb: number,
  hbp: number,
  k: number,
  ip: number,
  fipConstant = 3.10,
): number | null {
  if (ip <= 0) return null;
  return (13 * hr + 3 * (bb + hbp) - 2 * k) / ip + fipConstant;
}

/**
 * Expected Fielding Independent Pitching.
 * xFIP replaces actual HR with expected HR using fly-ball rate and league
 * HR/FB rate.
 *
 * @param fb  - Fly balls allowed.
 * @param lgHrPerFb - League HR/FB rate (default ~0.10 for NCAA).
 */
export function xfip(
  fb: number,
  bb: number,
  hbp: number,
  k: number,
  ip: number,
  lgHrPerFb = 0.10,
  fipConstant = 3.10,
): number | null {
  if (ip <= 0 || fb <= 0) return null;
  const expectedHR = fb * lgHrPerFb;
  return (13 * expectedHR + 3 * (bb + hbp) - 2 * k) / ip + fipConstant;
}

/**
 * Walks + Hits per Inning Pitched.
 * WHIP = (BB + H) / IP
 */
export function whip(bb: number, h: number, ip: number): number | null {
  if (ip <= 0) return null;
  return (bb + h) / ip;
}

/**
 * Strikeouts per 9 innings.
 * K/9 = (K / IP) × 9
 */
export function kPer9(k: number, ip: number): number | null {
  if (ip <= 0) return null;
  return (k / ip) * 9;
}

/**
 * Walks per 9 innings.
 * BB/9 = (BB / IP) × 9
 */
export function bbPer9(bb: number, ip: number): number | null {
  if (ip <= 0) return null;
  return (bb / ip) * 9;
}

/**
 * Strikeout-to-walk ratio.
 * K/BB = K / BB
 */
export function kPerBb(k: number, bb: number): number | null {
  if (bb <= 0) return null;
  return k / bb;
}

/**
 * Strand rate (LOB%).
 * LOB% = (H + BB + HBP − R) / (H + BB + HBP − 1.4×HR)
 */
export function lobPercent(
  h: number,
  bb: number,
  hbp: number,
  r: number,
  hr: number,
): number | null {
  const denom = h + bb + hbp - 1.4 * hr;
  if (denom <= 0) return null;
  return (h + bb + hbp - r) / denom;
}

// ---------------------------------------------------------------------------
// Hitting Metrics
// ---------------------------------------------------------------------------

/**
 * Batting average.
 * AVG = H / AB
 */
export function avg(h: number, ab: number): number | null {
  if (ab <= 0) return null;
  return h / ab;
}

/**
 * On-base percentage.
 * OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
 */
export function obp(
  h: number,
  bb: number,
  hbp: number,
  ab: number,
  sf: number,
): number | null {
  const denom = ab + bb + hbp + sf;
  if (denom <= 0) return null;
  return (h + bb + hbp) / denom;
}

/**
 * Slugging percentage.
 * SLG = TB / AB
 */
export function slg(totalBases: number, ab: number): number | null {
  if (ab <= 0) return null;
  return totalBases / ab;
}

/**
 * Compute total bases from hit components.
 * TB = 1B + 2×2B + 3×3B + 4×HR
 */
export function totalBases(
  h: number,
  doubles: number,
  triples: number,
  hr: number,
): number {
  const singles = h - doubles - triples - hr;
  return singles + 2 * doubles + 3 * triples + 4 * hr;
}

/**
 * On-base plus slugging.
 */
export function ops(obpVal: number, slgVal: number): number {
  return obpVal + slgVal;
}

/**
 * Isolated power.
 * ISO = SLG − AVG
 */
export function iso(slgVal: number, avgVal: number): number {
  return slgVal - avgVal;
}

/**
 * Batting Average on Balls in Play.
 * BABIP = (H − HR) / (AB − K − HR + SF)
 */
export function babip(
  h: number,
  hr: number,
  ab: number,
  k: number,
  sf: number,
): number | null {
  const denom = ab - k - hr + sf;
  if (denom <= 0) return null;
  return (h - hr) / denom;
}

/**
 * Weighted On-Base Average (simplified, college-calibrated linear weights).
 *
 * Default weights are approximate NCAA-calibrated values.
 */
export function woba(
  bb: number,
  hbp: number,
  singles: number,
  doubles: number,
  triples: number,
  hr: number,
  ab: number,
  sf: number,
  weights = {
    bb: 0.69,
    hbp: 0.72,
    single: 0.89,
    double: 1.27,
    triple: 1.62,
    hr: 2.10,
  },
): number | null {
  const denom = ab + bb + sf + hbp;
  if (denom <= 0) return null;
  const num =
    weights.bb * bb +
    weights.hbp * hbp +
    weights.single * singles +
    weights.double * doubles +
    weights.triple * triples +
    weights.hr * hr;
  return num / denom;
}

/**
 * Weighted Runs Created Plus (league-scaled to 100 = average).
 *
 * Simplified: wRC+ ≈ ((wRAA/PA + lgR/PA) / lgWRC/PA) × 100
 *
 * This function accepts a pre-computed wOBA and league parameters.
 *
 * @param playerWoba  - Player's wOBA.
 * @param lgWoba      - League average wOBA.
 * @param wobaScale   - wOBA scale factor (typically ~1.15 for NCAA).
 * @param lgRPerPA    - League runs per PA.
 */
export function wrcPlus(
  playerWoba: number,
  lgWoba: number,
  wobaScale = 1.15,
  lgRPerPA = 0.11,
): number | null {
  if (lgRPerPA <= 0 || wobaScale <= 0) return null;
  const wRAA_PA = (playerWoba - lgWoba) / wobaScale;
  return ((wRAA_PA + lgRPerPA) / lgRPerPA) * 100;
}
