/**
 * Game data ingestion — box score parsing, validation, and normalization.
 *
 * Implements the game-data-pipeline SKILL.md patterns.
 */

import type {
  GameBoxScore,
  BatterLine,
  PitcherLine,
  DataSource,
} from '../../../src/types/index.js';
import { normalizeIP, applyBatterDefaults, gameDedupKey } from '../../../src/utils/normalization.js';
import * as saber from '../../../src/utils/sabermetrics.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface IngestResult {
  gameId: string;
  success: boolean;
  dedupKey: string;
  /** Warnings generated during validation. */
  warnings: string[];
  /** The normalized box score (null if ingestion failed). */
  boxScore: GameBoxScore | null;
}

// ---------------------------------------------------------------------------
// Ingestion
// ---------------------------------------------------------------------------

/**
 * Ingest and validate a raw box score object.
 *
 * Returns a normalized GameBoxScore along with any validation warnings.
 * Does not throw on recoverable issues — collects them in `warnings`.
 */
export function ingestBoxScore(
  raw: GameBoxScore,
  source: DataSource = 'manual',
): IngestResult {
  const warnings: string[] = [];
  const dedupKey = gameDedupKey(
    raw.homeTeam.teamId,
    raw.date,
    raw.awayTeam.teamId,
  );

  // Normalize batter defaults
  const homeTeam = {
    ...raw.homeTeam,
    batting: raw.homeTeam.batting.map(normalizeBatter),
    pitching: raw.homeTeam.pitching.map(normalizePitcher),
  };
  const awayTeam = {
    ...raw.awayTeam,
    batting: raw.awayTeam.batting.map(normalizeBatter),
    pitching: raw.awayTeam.pitching.map(normalizePitcher),
  };

  // Validate computed runs match line score
  const homeLineTotalRuns = raw.homeTeam.lineScore.reduce((a, b) => a + b, 0);
  if (homeLineTotalRuns !== raw.homeTeam.runs) {
    warnings.push(
      `Home team line score total (${homeLineTotalRuns}) does not match runs (${raw.homeTeam.runs}).`,
    );
  }

  const awayLineTotalRuns = raw.awayTeam.lineScore.reduce((a, b) => a + b, 0);
  if (awayLineTotalRuns !== raw.awayTeam.runs) {
    warnings.push(
      `Away team line score total (${awayLineTotalRuns}) does not match runs (${raw.awayTeam.runs}).`,
    );
  }

  // Validate ERA for each pitcher
  for (const p of homeTeam.pitching) {
    validatePitcherERA(p, 'Home', warnings);
  }
  for (const p of awayTeam.pitching) {
    validatePitcherERA(p, 'Away', warnings);
  }

  const boxScore: GameBoxScore = {
    ...raw,
    homeTeam,
    awayTeam,
    source,
  };

  return {
    gameId: raw.gameId,
    success: true,
    dedupKey,
    warnings,
    boxScore,
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function normalizeBatter(b: BatterLine): BatterLine {
  return applyBatterDefaults(b) as BatterLine;
}

function normalizePitcher(p: PitcherLine): PitcherLine {
  const ip = typeof p.ip === 'string' ? normalizeIP(p.ip) : p.ip;
  return { ...p, ip };
}

function validatePitcherERA(
  p: PitcherLine,
  side: string,
  warnings: string[],
): void {
  if (p.ip <= 0) return;
  const computed = saber.era(p.er, p.ip);
  if (computed == null) return;

  // Just a sanity flag — ERA > 50 is almost certainly a data error
  if (computed > 50) {
    warnings.push(
      `${side} pitcher ${p.name}: computed ERA ${computed.toFixed(2)} seems too high — check data.`,
    );
  }
}
