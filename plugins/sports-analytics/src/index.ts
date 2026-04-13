/**
 * sports-analytics plugin — core library.
 *
 * Covers multi-sport data pipeline clients, stat visualization helpers,
 * and predictive modeling utilities.
 */

export { createProviderClient, type ProviderClient, type Provider } from './provider.js';
export { marcelProjection, winProbability, type MarcelInput, type GameState } from './models.js';
export {
  formatERA,
  formatWoba,
  formatPercent,
  tierLabel,
  type StatTier,
} from './format.js';
