/**
 * Shared types for the Sports-Plugins platform.
 *
 * These interfaces define the canonical data shapes used across all plugins.
 * Plugin source code imports from here to stay consistent.
 */

// ---------------------------------------------------------------------------
// Sports & Common
// ---------------------------------------------------------------------------

/** Supported sport identifiers across all plugins. */
export type Sport = 'mlb' | 'nfl' | 'nba' | 'cfb' | 'college-baseball';

/** Canonical game statuses shared by every sport. */
export type GameStatus =
  | 'scheduled'
  | 'in-progress'
  | 'final'
  | 'postponed'
  | 'cancelled';

/** Provider that sourced the data. */
export type DataSource =
  | 'bsi-mcp'
  | 'sportsdata-io'
  | 'mlb-stats-api'
  | 'ncaa-stats'
  | 'espn'
  | 'manual';

// ---------------------------------------------------------------------------
// Live Scores
// ---------------------------------------------------------------------------

export interface TeamScore {
  teamId: string;
  name: string;
  abbreviation: string;
  score: number;
  record?: string;
}

export interface LiveGameState {
  gameId: string;
  sport: Sport;
  status: GameStatus;
  homeTeam: TeamScore;
  awayTeam: TeamScore;
  /** Human-readable period, e.g. "Top 7th", "Q3", "2nd Half". */
  period: string;
  /** Clock for timed sports. */
  clock?: string;
  /** ISO 8601 start time. */
  startTime: string;
  /** ISO 8601 timestamp of the last data refresh. */
  lastUpdated: string;
  source: DataSource;
}

// ---------------------------------------------------------------------------
// Baseball Box Scores
// ---------------------------------------------------------------------------

export interface BatterLine {
  playerId: string;
  name: string;
  position: string;
  ab: number;
  r: number;
  h: number;
  rbi: number;
  bb: number;
  k: number;
  hbp: number;
  sf: number;
  doubles: number;
  triples: number;
  hr: number;
  sb: number;
  cs: number;
}

export interface PitcherLine {
  playerId: string;
  name: string;
  /** Innings pitched as a decimal (6.1 → 6⅓ innings). */
  ip: number;
  h: number;
  r: number;
  er: number;
  bb: number;
  k: number;
  hr: number;
  hbp: number;
  decision?: 'W' | 'L' | 'S' | 'H' | 'BS' | null;
  pitchCount?: number;
  strikes?: number;
}

export interface TeamGameLine {
  teamId: string;
  teamName: string;
  conference: string;
  runs: number;
  hits: number;
  errors: number;
  /** Runs per inning. */
  lineScore: number[];
  batting: BatterLine[];
  pitching: PitcherLine[];
}

export interface InningLine {
  inning: number;
  homeRuns: number | null;
  awayRuns: number | null;
}

export interface GameBoxScore {
  /** Unique, source-prefixed identifier (e.g. "ncaa-2025-04-05-texas-tcu"). */
  gameId: string;
  /** ISO 8601 date. */
  date: string;
  venue: string;
  homeTeam: TeamGameLine;
  awayTeam: TeamGameLine;
  innings: InningLine[];
  /** Duration in minutes, if available. */
  duration?: number;
  attendance?: number;
  source: DataSource;
}

// ---------------------------------------------------------------------------
// Season Aggregates
// ---------------------------------------------------------------------------

export interface PlayerSeasonStats {
  playerId: string;
  teamId: string;
  season: number;
  gamesPlayed: number;

  // Batting
  pa: number;
  ab: number;
  h: number;
  doubles: number;
  triples: number;
  hr: number;
  rbi: number;
  r: number;
  bb: number;
  k: number;
  hbp: number;
  sf: number;
  sb: number;
  cs: number;

  // Pitching (populated only for pitchers)
  ip?: number;
  gs?: number;
  sv?: number;
  er?: number;
  bbAllowed?: number;
  kPitching?: number;
  hrAllowed?: number;
  hbpAllowed?: number;

  // Computed metrics (populated after ingestion)
  avg?: number;
  obp?: number;
  slg?: number;
  ops?: number;
  iso?: number;
  babip?: number;
  woba?: number;
  wrcPlus?: number;
  era?: number;
  fip?: number;
  xfip?: number;
  whip?: number;
  kPer9?: number;
  bbPer9?: number;
}

// ---------------------------------------------------------------------------
// Player Cross-Reference
// ---------------------------------------------------------------------------

export interface PlayerRef {
  /** Internal BSI identifier. */
  bsiId: string;
  ncaaId?: string;
  brefId?: string;
  name: string;
  team: string;
  season: number;
}

// ---------------------------------------------------------------------------
// Fantasy Sports
// ---------------------------------------------------------------------------

export type ScoringFormat = 'standard' | 'ppr' | 'half-ppr' | 'custom';
export type DraftFormat = 'snake' | 'auction' | 'dfs';
export type TradeVerdict = 'accept' | 'counter' | 'decline';

export interface TradeAnalysis {
  giving: string[];
  getting: string[];
  rawValue: 'edge-you' | 'even' | 'edge-them' | 'clear-winner';
  verdict: TradeVerdict;
  reasoning: string;
  counter?: string;
}

export interface WaiverRecommendation {
  priority: number;
  playerName: string;
  position: string;
  team: string;
  opportunity: string;
  matchup: string;
  dropName: string;
  dropPosition: string;
  dropReason: string;
}

// ---------------------------------------------------------------------------
// Projections
// ---------------------------------------------------------------------------

export type ConfidenceTier = 'high' | 'medium' | 'low';

export interface PlayerProjection {
  playerId: string;
  projectedWoba: number;
  projectedPA: number;
  confidence: ConfidenceTier;
  note?: string;
}

// ---------------------------------------------------------------------------
// Plugin Manifest (mirrors .claude-plugin/plugin.json)
// ---------------------------------------------------------------------------

export interface PluginManifest {
  name: string;
  description: string;
  version: string;
  author: {
    name: string;
    email: string;
  };
}

export interface MarketplaceEntry {
  name: string;
  description: string;
  source: string;
  category: string;
  homepage: string;
}

export interface Marketplace {
  $schema?: string;
  name: string;
  owner: {
    name: string;
    email: string;
  };
  metadata: {
    description: string;
  };
  plugins: MarketplaceEntry[];
}
