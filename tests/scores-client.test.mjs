/**
 * Unit tests for lib/scores-client.ts — resolveLeague and normalisation logic.
 *
 * The formulas are re-implemented inline in plain JS to avoid requiring
 * a TypeScript compile step.  Keep in sync with lib/scores-client.ts.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";

// ---------------------------------------------------------------------------
// Inline re-implementations matching lib/scores-client.ts
// ---------------------------------------------------------------------------

const LEAGUE_PATHS = {
  mlb: "baseball/mlb",
  nfl: "football/nfl",
  nba: "basketball/nba",
  "college-baseball": "baseball/college-baseball",
  "college-football": "football/college-football",
};

function resolveLeague(input) {
  const key = input.toLowerCase().trim();
  const aliases = {
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

function mapStatus(espnStatus) {
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

function toTeamScore(c) {
  return {
    name: c.team.displayName,
    abbreviation: c.team.abbreviation,
    score: c.score != null ? Number(c.score) : null,
    rank:
      c.curatedRank?.current && c.curatedRank.current <= 25
        ? c.curatedRank.current
        : undefined,
    record: c.records?.[0]?.summary,
  };
}

function normaliseEvent(evt, league) {
  const comp = evt.competitions[0];
  const home = comp.competitors.find((c) => c.homeAway === "home");
  const away = comp.competitors.find((c) => c.homeAway === "away");
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

// ---------------------------------------------------------------------------
// Test data — mock ESPN event
// ---------------------------------------------------------------------------

const mockEvent = {
  id: "401585123",
  date: "2026-04-13T19:00Z",
  status: { type: { name: "STATUS_IN_PROGRESS", description: "In Progress", detail: "Top 7th" } },
  competitions: [
    {
      competitors: [
        {
          homeAway: "home",
          team: { displayName: "Texas Longhorns", abbreviation: "TEX" },
          score: "5",
          curatedRank: { current: 1 },
          records: [{ summary: "38-8" }],
        },
        {
          homeAway: "away",
          team: { displayName: "Oklahoma Sooners", abbreviation: "OU" },
          score: "3",
          curatedRank: { current: 30 },
          records: [{ summary: "25-20" }],
        },
      ],
    },
  ],
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("scores-client — resolveLeague", () => {
  it("resolves canonical league names", () => {
    assert.equal(resolveLeague("mlb"), "mlb");
    assert.equal(resolveLeague("nfl"), "nfl");
    assert.equal(resolveLeague("nba"), "nba");
    assert.equal(resolveLeague("college-baseball"), "college-baseball");
    assert.equal(resolveLeague("college-football"), "college-football");
  });

  it("resolves common aliases", () => {
    assert.equal(resolveLeague("baseball"), "mlb");
    assert.equal(resolveLeague("football"), "nfl");
    assert.equal(resolveLeague("basketball"), "nba");
    assert.equal(resolveLeague("cbb"), "college-baseball");
    assert.equal(resolveLeague("cfb"), "college-football");
    assert.equal(resolveLeague("ncaa_baseball"), "college-baseball");
    assert.equal(resolveLeague("ncaa_football"), "college-football");
    assert.equal(resolveLeague("college baseball"), "college-baseball");
    assert.equal(resolveLeague("college football"), "college-football");
  });

  it("is case-insensitive", () => {
    assert.equal(resolveLeague("MLB"), "mlb");
    assert.equal(resolveLeague("NFL"), "nfl");
    assert.equal(resolveLeague("CBB"), "college-baseball");
    assert.equal(resolveLeague("CFB"), "college-football");
  });

  it("trims whitespace", () => {
    assert.equal(resolveLeague("  mlb  "), "mlb");
    assert.equal(resolveLeague("  cbb "), "college-baseball");
  });

  it("returns null for unknown inputs", () => {
    assert.equal(resolveLeague("cricket"), null);
    assert.equal(resolveLeague(""), null);
    assert.equal(resolveLeague("mls"), null);
    assert.equal(resolveLeague("hockey"), null);
  });
});

describe("scores-client — mapStatus", () => {
  it("maps known ESPN statuses", () => {
    assert.equal(mapStatus("STATUS_FINAL"), "final");
    assert.equal(mapStatus("STATUS_IN_PROGRESS"), "in_progress");
    assert.equal(mapStatus("STATUS_SCHEDULED"), "scheduled");
    assert.equal(mapStatus("STATUS_PRE_EVENT"), "scheduled");
    assert.equal(mapStatus("STATUS_POSTPONED"), "postponed");
    assert.equal(mapStatus("STATUS_DELAYED"), "delayed");
  });

  it("defaults to scheduled for unknown statuses", () => {
    assert.equal(mapStatus("STATUS_UNKNOWN"), "scheduled");
    assert.equal(mapStatus(""), "scheduled");
    assert.equal(mapStatus("RANDOM_VALUE"), "scheduled");
  });
});

describe("scores-client — normaliseEvent", () => {
  it("normalises a mock ESPN event into a GameScore", () => {
    const game = normaliseEvent(mockEvent, "college-baseball");

    assert.equal(game.id, "401585123");
    assert.equal(game.league, "college-baseball");
    assert.equal(game.status, "in_progress");
    assert.equal(game.startTime, "2026-04-13T19:00Z");
    assert.equal(game.period, "Top 7th");
  });

  it("parses home team correctly", () => {
    const game = normaliseEvent(mockEvent, "college-baseball");
    assert.equal(game.homeTeam.name, "Texas Longhorns");
    assert.equal(game.homeTeam.abbreviation, "TEX");
    assert.equal(game.homeTeam.score, 5);
    assert.equal(game.homeTeam.rank, 1);
    assert.equal(game.homeTeam.record, "38-8");
  });

  it("parses away team correctly", () => {
    const game = normaliseEvent(mockEvent, "college-baseball");
    assert.equal(game.awayTeam.name, "Oklahoma Sooners");
    assert.equal(game.awayTeam.abbreviation, "OU");
    assert.equal(game.awayTeam.score, 3);
    // rank > 25 should be excluded
    assert.equal(game.awayTeam.rank, undefined);
    assert.equal(game.awayTeam.record, "25-20");
  });

  it("handles missing score as null", () => {
    const noScoreEvent = structuredClone(mockEvent);
    delete noScoreEvent.competitions[0].competitors[0].score;
    const game = normaliseEvent(noScoreEvent, "mlb");
    assert.equal(game.homeTeam.score, null);
  });

  it("handles missing records gracefully", () => {
    const noRecordsEvent = structuredClone(mockEvent);
    delete noRecordsEvent.competitions[0].competitors[0].records;
    const game = normaliseEvent(noRecordsEvent, "mlb");
    assert.equal(game.homeTeam.record, undefined);
  });

  it("handles missing curatedRank gracefully", () => {
    const noRankEvent = structuredClone(mockEvent);
    delete noRankEvent.competitions[0].competitors[0].curatedRank;
    const game = normaliseEvent(noRankEvent, "mlb");
    assert.equal(game.homeTeam.rank, undefined);
  });
});

describe("scores-client — LEAGUE_PATHS coverage", () => {
  it("has paths for all five supported leagues", () => {
    assert.equal(Object.keys(LEAGUE_PATHS).length, 5);
    assert.ok(LEAGUE_PATHS["mlb"]);
    assert.ok(LEAGUE_PATHS["nfl"]);
    assert.ok(LEAGUE_PATHS["nba"]);
    assert.ok(LEAGUE_PATHS["college-baseball"]);
    assert.ok(LEAGUE_PATHS["college-football"]);
  });
});
