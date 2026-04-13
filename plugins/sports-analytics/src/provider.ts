/**
 * Multi-provider sports data client factory.
 *
 * Implements the data-pipeline SKILL.md provider-wrapper pattern.
 * Each provider gets a typed fetch wrapper; API keys are resolved
 * from environment variables — never embedded in client code.
 */

import type { DataSource } from '../../../src/types/index.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type Provider = 'sportsdata-io' | 'mlb-stats-api' | 'ncaa-stats' | 'bsi-mcp' | 'espn';

export interface ProviderClient {
  provider: Provider;
  source: DataSource;
  /**
   * Generic typed fetch against the provider's base URL.
   * @param path - Path appended to the provider base URL.
   */
  get: <T>(path: string) => Promise<T>;
}

interface ProviderConfig {
  baseUrl: string;
  source: DataSource;
  /** Header key used for auth, if any. */
  authHeader?: string;
  /** Environment variable that holds the API key. */
  authEnvVar?: string;
}

const PROVIDERS: Record<Provider, ProviderConfig> = {
  'sportsdata-io': {
    baseUrl: 'https://api.sportsdata.io/v3',
    source: 'sportsdata-io',
    authHeader: 'Ocp-Apim-Subscription-Key',
    authEnvVar: 'SPORTS_DATA_IO_API_KEY',
  },
  'mlb-stats-api': {
    baseUrl: 'https://statsapi.mlb.com/api/v1',
    source: 'mlb-stats-api',
  },
  'ncaa-stats': {
    baseUrl: 'https://stats.ncaa.org',
    source: 'ncaa-stats',
  },
  'bsi-mcp': {
    baseUrl: 'https://blazesportsintel.com/mcp',
    source: 'bsi-mcp',
  },
  'espn': {
    baseUrl: 'https://site.api.espn.com/apis/site/v2/sports',
    source: 'espn',
  },
};

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

/**
 * Create a typed fetch client for a given provider.
 *
 * @param provider - One of the supported provider identifiers.
 * @param env      - Environment object or `process.env` for key resolution.
 */
export function createProviderClient(
  provider: Provider,
  env: Record<string, string | undefined> = typeof process !== 'undefined' ? process.env : {},
): ProviderClient {
  const config = PROVIDERS[provider];
  if (!config) {
    throw new Error(`Unknown provider: ${provider}`);
  }

  const headers: Record<string, string> = {};
  if (config.authHeader && config.authEnvVar) {
    const key = env[config.authEnvVar];
    if (!key) {
      throw new Error(
        `Missing environment variable ${config.authEnvVar} for provider ${provider}.`,
      );
    }
    headers[config.authHeader] = key;
  }

  return {
    provider,
    source: config.source,
    async get<T>(path: string): Promise<T> {
      const url = `${config.baseUrl}${path}`;
      const res = await fetch(url, { headers });
      if (!res.ok) {
        throw new Error(`${provider} ${res.status} for ${path}`);
      }
      return res.json() as Promise<T>;
    },
  };
}
