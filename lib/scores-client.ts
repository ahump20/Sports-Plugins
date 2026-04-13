/**
 * ESPN public API client for live sports scores.
 *
 * This module wraps the ESPN "site" API endpoints which are publicly
 * available and don't require an API key.  They return JSON for
 * current scoreboards, schedules, and team information.
 *
 * These endpoints are used by the `live-scores` plugin to feed the
 * `fetch-scores` skill and `/scoreboard` command.
 */

import type { GameScore, GameStatus, League, TeamScore } from "./types.js";

/* ------------------------------------------------------------------ */
/*  ESPN endpoint mapping                                              */
/* ------------------------------------------------------------------ */

const ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports";

const LEAGUE_PATHS: Record<League, string> = {
  mlb: "baseball/mlb",
  nfl: "football/nfl",
  nba: "basketball/nba",
  "college-baseball": "baseball/college-baseball",
  "college-football": "football/college-football",
};

/* ------------------------------------------------------------------ */
/*  Public API                                                        */
/* ------------------------------------------------------------------ */

/**
 * Fetch today's scoreboard for a given league.
 *
 * @param league — one of the supported League values
 * @param date   — optional YYYY-MM-DD; defaults to today (ESPN's default)
 * @returns array of normalised GameScore objects
 *
 * @example
 * ```ts
 * const games = await fetchScoreboard("mlb");
 * const cfbGames = await fetchScoreboard("college-football", "2026-10-15");
 * ```
 */
export async function fetchScoreboard(league: League, date?: string): Promise<GameScore[]> {
  const path = LEAGUE_PATHS[league];
  if (!path) throw new Error(`Unsupported league: ${league}`);

  const url = new URL(`${ESPN_BASE}/${path}/scoreboard`);
  if (date) url.searchParams.set("dates", date.replace(/-/g, ""));

  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`ESPN API error ${res.status}: ${res.statusText}`);
  }

  const data = (await res.json()) as ESPNScoreboardResponse;
  return (data.events ?? []).map((evt) => normaliseEvent(evt, league));
}

/**
 * Resolve common sport aliases to a canonical League value.
 *
 * @example
 * ```ts
 * resolveLeague("baseball")       // "mlb"
 * resolveLeague("cbb")            // "college-baseball"
 * resolveLeague("cfb")            // "college-football"
 * ```
 */
export function resolveLeague(input: string): League | null {
  const key = input.toLowerCase().trim();
  const aliases: Record<string, League> = {
    mlb: "mlb",
    baseball: "mlb",
    nfl: "nfl",
    football: "nfl",
    nba: "nba",
    basketball: "nba",
    "college-baseball": "college-baseball",
    cbb: "college-baseball",
    "college baseball": "college-baseball",
    ncaa_baseball: "college-baseball",
    "college-football": "college-football",
    cfb: "college-football",
    "college football": "college-football",
    ncaa_football: "college-football",
  };
  return aliases[key] ?? null;
}

/* ------------------------------------------------------------------ */
/*  Internal — ESPN response types (minimal)                          */
/* ------------------------------------------------------------------ */

interface ESPNScoreboardResponse {
  events?: ESPNEvent[];
}

interface ESPNEvent {
  id: string;
  date: string;
  status: { type: { name: string; description: string; detail: string } };
  competitions: Array<{
    competitors: Array<{
      homeAway: "home" | "away";
      team: { displayName: string; abbreviation: string };
      score?: string;
      curatedRank?: { current: number };
      records?: Array<{ summary: string }>;
    }>;
  }>;
}

/* ------------------------------------------------------------------ */
/*  Internal — normalise ESPN event → GameScore                       */
/* ------------------------------------------------------------------ */

function normaliseEvent(evt: ESPNEvent, league: League): GameScore {
  const comp = evt.competitions[0];
  const home = comp.competitors.find((c) => c.homeAway === "home")!;
  const away = comp.competitors.find((c) => c.homeAway === "away")!;

  return {
    id: evt.id,
    league,
    status: mapStatus(evt.status.type.name),
    startTime: evt.date,
    period: evt.status.type.detail,
    homeTeam: toTeamScore(home),
    awayTeam: toTeamScore(away),
  };
}

function toTeamScore(c: ESPNEvent["competitions"][0]["competitors"][0]): TeamScore {
  return {
    name: c.team.displayName,
    abbreviation: c.team.abbreviation,
    score: c.score != null ? Number(c.score) : null,
    rank: c.curatedRank?.current && c.curatedRank.current <= 25 ? c.curatedRank.current : undefined,
    record: c.records?.[0]?.summary,
  };
}

function mapStatus(espnStatus: string): GameStatus {
  switch (espnStatus) {
    case "STATUS_FINAL":
      return "final";
    case "STATUS_IN_PROGRESS":
      return "in_progress";
    case "STATUS_SCHEDULED":
    case "STATUS_PRE_EVENT":
      return "scheduled";
    case "STATUS_POSTPONED":
      return "postponed";
    case "STATUS_DELAYED":
      return "delayed";
    default:
      return "scheduled";
  }
}
