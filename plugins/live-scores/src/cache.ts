/**
 * In-memory score cache simulating Cloudflare KV patterns.
 *
 * In production, this would be backed by Cloudflare KV with expiration TTLs.
 * This implementation mirrors the real-time-data SKILL.md caching strategy.
 */

import type { LiveGameState } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CachedScore {
  game: LiveGameState;
  /** ISO 8601 timestamp of when this entry was cached. */
  cachedAt: string;
  /** TTL in seconds that was set when this entry was stored. */
  ttl: number;
}

// ---------------------------------------------------------------------------
// Cache
// ---------------------------------------------------------------------------

/**
 * Simple in-memory score cache following KV patterns.
 *
 * Per SKILL.md hard rules:
 * - Never cache a failed (null/error) response.
 * - Always include a lastUpdated timestamp.
 */
export class ScoreCache {
  private store = new Map<string, CachedScore>();

  /**
   * Store a game score in cache.
   *
   * @param gameId - Unique game identifier.
   * @param game   - The game state to cache.
   * @param ttl    - Time-to-live in seconds (default: 30).
   */
  put(gameId: string, game: LiveGameState, ttl = 30): void {
    this.store.set(`game:${gameId}`, {
      game,
      cachedAt: new Date().toISOString(),
      ttl,
    });
  }

  /**
   * Retrieve a game score from cache.
   * Returns null if expired or not found.
   */
  get(gameId: string): LiveGameState | null {
    const key = `game:${gameId}`;
    const entry = this.store.get(key);
    if (!entry) return null;

    const age = (Date.now() - new Date(entry.cachedAt).getTime()) / 1000;
    if (age >= entry.ttl) {
      this.store.delete(key);
      return null;
    }

    return entry.game;
  }

  /** List all cached game IDs (regardless of expiry — for inspection). */
  keys(): string[] {
    return Array.from(this.store.keys());
  }

  /** Remove all entries. */
  clear(): void {
    this.store.clear();
  }

  /** Number of entries (including possibly expired). */
  get size(): number {
    return this.store.size;
  }
}
