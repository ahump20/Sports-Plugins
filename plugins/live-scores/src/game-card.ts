/**
 * Game card state machine — determines the visual treatment for a game card
 * based on the current LiveGameState status.
 *
 * Implements the GameCard States table from scoreboard-ui SKILL.md.
 */

import type { GameStatus, LiveGameState, Sport } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export enum GameCardState {
  Scheduled = 'scheduled',
  InProgress = 'in-progress',
  Final = 'final',
  Postponed = 'postponed',
  Cancelled = 'cancelled',
}

export interface GameCardProps {
  state: GameCardState;
  /** Show the pulsing live dot. Only true for in-progress. */
  showLiveDot: boolean;
  /** Show score values. False for scheduled games. */
  showScore: boolean;
  /** Badge text to display (e.g. "Final", "PPD"). Null when none. */
  badgeText: string | null;
  /** CSS class for the card surface. */
  surfaceClass: string;
  /** Display text for the game period/time/status. */
  statusText: string;
}

// ---------------------------------------------------------------------------
// Surface classes (Tailwind)
// ---------------------------------------------------------------------------

const SURFACE: Record<GameCardState, string> = {
  [GameCardState.Scheduled]: 'bg-card',
  [GameCardState.InProgress]: 'bg-card shadow-md ring-1 ring-primary/20',
  [GameCardState.Final]: 'bg-muted',
  [GameCardState.Postponed]: 'bg-muted opacity-75',
  [GameCardState.Cancelled]: 'bg-muted opacity-75',
};

// ---------------------------------------------------------------------------
// Core
// ---------------------------------------------------------------------------

/**
 * Resolve the visual props for a GameCard from a LiveGameState.
 *
 * Per SKILL.md hard rules:
 * - Never show a pulsing live dot for a final game.
 * - Never show a score for a scheduled game — show start time instead.
 */
export function resolveGameCardState(game: LiveGameState): GameCardProps {
  const state = statusToCardState(game.status);

  return {
    state,
    showLiveDot: state === GameCardState.InProgress,
    showScore: state !== GameCardState.Scheduled,
    badgeText: badgeForState(state),
    surfaceClass: SURFACE[state],
    statusText: statusTextForGame(game, state),
  };
}

function statusToCardState(status: GameStatus): GameCardState {
  switch (status) {
    case 'scheduled': return GameCardState.Scheduled;
    case 'in-progress': return GameCardState.InProgress;
    case 'final': return GameCardState.Final;
    case 'postponed': return GameCardState.Postponed;
    case 'cancelled': return GameCardState.Cancelled;
  }
}

function badgeForState(state: GameCardState): string | null {
  switch (state) {
    case GameCardState.Final: return 'Final';
    case GameCardState.Postponed: return 'PPD';
    case GameCardState.Cancelled: return 'Cancelled';
    default: return null;
  }
}

function statusTextForGame(game: LiveGameState, state: GameCardState): string {
  switch (state) {
    case GameCardState.Scheduled:
      return formatStartTime(game.startTime);
    case GameCardState.InProgress:
      return game.clock ? `${game.period} — ${game.clock}` : game.period;
    case GameCardState.Final:
      return 'Final';
    case GameCardState.Postponed:
      return 'Postponed';
    case GameCardState.Cancelled:
      return 'Cancelled';
  }
}

function formatStartTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  } catch {
    return iso;
  }
}

// Export Sport type for external use
export type { Sport };
