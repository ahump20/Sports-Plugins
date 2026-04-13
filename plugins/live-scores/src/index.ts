/**
 * live-scores plugin — core library.
 *
 * Provides scoreboard data types, KV cache helpers, and game-state
 * rendering utilities as documented in the scoreboard-ui and
 * real-time-data SKILL.md files.
 */

export { GameCardState, resolveGameCardState, type GameCardProps } from './game-card.js';
export { ScoreCache, type CachedScore } from './cache.js';
export { formatPeriod, formatClock, SPORT_BADGE_COLORS } from './display.js';
