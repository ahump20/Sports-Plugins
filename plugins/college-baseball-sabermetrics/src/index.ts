/**
 * college-baseball-sabermetrics plugin — core library.
 *
 * Provides the computation and analysis functions documented in the plugin's
 * four SKILL.md files: sabermetrics-analysis, pitcher-analytics,
 * lineup-optimizer, and game-data-pipeline.
 */

export { computeBatterMetrics, computePitcherMetrics } from './metrics.js';
export { evaluatePitcher, type PitcherEvaluation, type PitchMix } from './pitcher-eval.js';
export { optimizeLineup, type LineupSlot, type LineupCard } from './lineup.js';
export { ingestBoxScore, type IngestResult } from './ingest.js';
