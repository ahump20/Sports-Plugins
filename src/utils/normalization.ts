/**
 * Data normalization utilities shared across all plugins.
 */

// ---------------------------------------------------------------------------
// Innings Pitched
// ---------------------------------------------------------------------------

/**
 * Normalize NCAA-style innings pitched to a true decimal.
 *
 * NCAA reports partial innings as `.1` (one out) and `.2` (two outs).
 * This converts them to thirds: "6.2" → 6.667.
 *
 * @param ncaaIP - Innings pitched in NCAA notation (e.g. "6.2").
 * @returns Decimal innings pitched.
 */
export function normalizeIP(ncaaIP: string | number): number {
  const str = String(ncaaIP);
  const [fullStr, partialStr = '0'] = str.split('.');
  const full = parseInt(fullStr, 10) || 0;
  const partial = parseInt(partialStr, 10) || 0;
  return full + partial / 3;
}

// ---------------------------------------------------------------------------
// Date Helpers
// ---------------------------------------------------------------------------

/**
 * Format a Date to an ISO 8601 date string (YYYY-MM-DD).
 */
export function toISODate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

/**
 * Check whether a given hour (UTC) falls within typical US game hours.
 * Game hours: 3 PM – 4 AM UTC (11 AM – midnight ET).
 */
export function isGameHourUTC(hour: number): boolean {
  return hour >= 15 || hour < 4;
}

// ---------------------------------------------------------------------------
// Team Name Normalization
// ---------------------------------------------------------------------------

/** Common NCAA team name aliases. */
const TEAM_ALIASES: Record<string, string> = {
  'Texas': 'Texas Longhorns',
  'UT': 'Texas Longhorns',
  'UT Austin': 'Texas Longhorns',
  'Longhorns': 'Texas Longhorns',
  'Texas A&M': 'Texas A&M Aggies',
  'TAMU': 'Texas A&M Aggies',
  'Aggies': 'Texas A&M Aggies',
  'Oklahoma': 'Oklahoma Sooners',
  'OU': 'Oklahoma Sooners',
  'Oklahoma State': 'Oklahoma State Cowboys',
  'OK State': 'Oklahoma State Cowboys',
  'OSU': 'Oklahoma State Cowboys',
  'TCU': 'TCU Horned Frogs',
  'Baylor': 'Baylor Bears',
  'Texas Tech': 'Texas Tech Red Raiders',
  'TTU': 'Texas Tech Red Raiders',
  'Kansas': 'Kansas Jayhawks',
  'K-State': 'Kansas State Wildcats',
  'Kansas State': 'Kansas State Wildcats',
  'West Virginia': 'West Virginia Mountaineers',
  'WVU': 'West Virginia Mountaineers',
  'UCF': 'UCF Knights',
  'BYU': 'BYU Cougars',
  'Cincinnati': 'Cincinnati Bearcats',
  'Houston': 'Houston Cougars',
  'Iowa State': 'Iowa State Cyclones',
  'Arizona': 'Arizona Wildcats',
  'Arizona State': 'Arizona State Sun Devils',
  'ASU': 'Arizona State Sun Devils',
  'Colorado': 'Colorado Buffaloes',
  'Utah': 'Utah Utes',
};

/**
 * Resolve a team name or abbreviation to the canonical form.
 * Returns the input unchanged if no alias is found.
 */
export function normalizeTeamName(input: string): string {
  return TEAM_ALIASES[input] ?? input;
}

// ---------------------------------------------------------------------------
// Missing Data Defaults
// ---------------------------------------------------------------------------

/**
 * Apply safe defaults for commonly missing box-score fields.
 *
 * Per the game-data-pipeline SKILL.md:
 * - Missing sf  → 0
 * - Missing hbp → 0
 * - Missing pitchCount / attendance → null (never estimate)
 */
export function applyBatterDefaults<
  T extends { sf?: number; hbp?: number },
>(raw: T): T & { sf: number; hbp: number } {
  return {
    ...raw,
    sf: raw.sf ?? 0,
    hbp: raw.hbp ?? 0,
  };
}

// ---------------------------------------------------------------------------
// Deduplication
// ---------------------------------------------------------------------------

/**
 * Generate a dedup key for a game using team + date + opponent.
 * This is more reliable than gameId alone when cross-referencing sources.
 */
export function gameDedupKey(
  teamId: string,
  date: string,
  opponentId: string,
): string {
  return [teamId, date, opponentId].sort().join('::');
}

// ---------------------------------------------------------------------------
// Rounding
// ---------------------------------------------------------------------------

/**
 * Round a number to the specified precision.
 *
 * Per the stats-visualization SKILL.md:
 * - ERA → 2 decimal places
 * - wOBA → 3 decimal places
 * - K% → 1 decimal + "%"
 */
export function round(value: number, decimals: number): number {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}
