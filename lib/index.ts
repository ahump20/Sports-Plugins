/**
 * Shared library entry-point.
 *
 * Re-exports all public functions and types so consumers can do:
 *   import { wOBA, fetchScoreboard } from "@sports-plugins/lib";
 */

export * from "./types.js";
export * from "./sabermetrics.js";
export * from "./scores-client.js";
