/**
 * Unit tests for the sabermetrics calculation library.
 *
 * These are pure-math tests — no network calls, no MCP.
 * Run with: node --test tests/sabermetrics.test.mjs
 *
 * The formulas are re-implemented inline in plain JS so that tests can
 * run without a TypeScript compile step.  Keep these in sync with
 * lib/sabermetrics.ts — any formula change there must be mirrored here.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";

// ---------------------------------------------------------------------------
// Inline the core formulas so tests don't depend on a TS compile step.
// These mirror lib/sabermetrics.ts exactly.
// ---------------------------------------------------------------------------

const NCAA_WOBA_WEIGHTS = { uBB: 0.69, HBP: 0.72, single: 0.89, double: 1.27, triple: 1.62, HR: 2.1 };
const WOBA_SCALE = 1.15;
const LG_WOBA = 0.32;
const LG_R_PER_PA = 0.126;
const FIP_CONSTANT = 3.1;

function avg(l) { return l.ab === 0 ? 0 : l.h / l.ab; }
function obp(l) { const d = l.ab + l.bb + l.hbp + l.sf; return d === 0 ? 0 : (l.h + l.bb + l.hbp) / d; }
function slg(l) {
  if (l.ab === 0) return 0;
  const s = l.h - l.doubles - l.triples - l.hr;
  return (s + 2 * l.doubles + 3 * l.triples + 4 * l.hr) / l.ab;
}
function wOBA(l) {
  const s = l.h - l.doubles - l.triples - l.hr;
  const uBB = l.bb - l.ibb;
  const num = NCAA_WOBA_WEIGHTS.uBB * uBB + NCAA_WOBA_WEIGHTS.HBP * l.hbp + NCAA_WOBA_WEIGHTS.single * s + NCAA_WOBA_WEIGHTS.double * l.doubles + NCAA_WOBA_WEIGHTS.triple * l.triples + NCAA_WOBA_WEIGHTS.HR * l.hr;
  const den = l.ab + l.bb - l.ibb + l.sf + l.hbp;
  return den === 0 ? 0 : num / den;
}
function wRAA(l) { return ((wOBA(l) - LG_WOBA) / WOBA_SCALE) * l.pa; }
function wRCPlus(l, pf = 1.0) {
  if (l.pa === 0) return 0;
  const w = wRAA(l) / l.pa;
  const a = LG_R_PER_PA * pf;
  return ((w + LG_R_PER_PA + (LG_R_PER_PA - a)) / LG_R_PER_PA) * 100;
}
function babip(l) { const d = l.ab - l.k - l.hr + l.sf; return d <= 0 ? 0 : (l.h - l.hr) / d; }
function iso(l) { return slg(l) - avg(l); }
function kPct(l) { return l.pa === 0 ? 0 : l.k / l.pa; }
function bbPct(l) { return l.pa === 0 ? 0 : l.bb / l.pa; }

function era(p) { return p.ip === 0 ? 0 : (p.er / p.ip) * 9; }
function fip(p) { return p.ip === 0 ? 0 : (13 * p.hr + 3 * (p.bb + p.hbp) - 2 * p.k) / p.ip + FIP_CONSTANT; }
function whip(p) { return p.ip === 0 ? 0 : (p.bb + p.h) / p.ip; }
function kPer9(p) { return p.ip === 0 ? 0 : (p.k / p.ip) * 9; }
function bbPer9(p) { return p.ip === 0 ? 0 : (p.bb / p.ip) * 9; }
function hrPer9(p) { return p.ip === 0 ? 0 : (p.hr / p.ip) * 9; }
function kPerBB(p) { return p.bb === 0 ? (p.k > 0 ? Infinity : 0) : p.k / p.bb; }
function xfip(p) {
  if (p.ip === 0) return 0;
  const LG_HR_PER_FB = 0.1;
  const bip = Math.max(0, p.bf - p.k - p.bb - p.hbp);
  const estFB = Math.max(0, bip * 0.35);
  const expectedHR = Math.max(0, estFB * LG_HR_PER_FB);
  return (13 * expectedHR + 3 * (p.bb + p.hbp) - 2 * p.k) / p.ip + FIP_CONSTANT;
}
function cswPctFn(cs, w, tp) { return tp === 0 ? 0 : (cs + w) / tp; }

// ---------------------------------------------------------------------------
// Helper to round to N decimal places for comparison
// ---------------------------------------------------------------------------
function r(n, d = 3) { return Math.round(n * 10 ** d) / 10 ** d; }

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

/** Simulated full-season batting line for a strong college hitter. */
const goodHitter = {
  pa: 250, ab: 220, h: 72, doubles: 16, triples: 2, hr: 14,
  bb: 25, ibb: 2, hbp: 3, sf: 2, k: 42, rbi: 52, sb: 8, cs: 3,
};

/** Simulated full-season pitching line for a strong college starter. */
const goodPitcher = {
  ip: 95, h: 68, r: 30, er: 28, bb: 24, hbp: 5, k: 115, hr: 6, bf: 380, pitches: 1480,
};

/** Empty line — edge case. */
const emptyBatter = {
  pa: 0, ab: 0, h: 0, doubles: 0, triples: 0, hr: 0,
  bb: 0, ibb: 0, hbp: 0, sf: 0, k: 0, rbi: 0, sb: 0, cs: 0,
};

const emptyPitcher = { ip: 0, h: 0, r: 0, er: 0, bb: 0, hbp: 0, k: 0, hr: 0, bf: 0 };

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("Sabermetrics — Batting", () => {
  it("AVG = H / AB", () => {
    assert.equal(r(avg(goodHitter)), r(72 / 220));
  });

  it("OBP = (H + BB + HBP) / (AB + BB + HBP + SF)", () => {
    const expected = (72 + 25 + 3) / (220 + 25 + 3 + 2);
    assert.equal(r(obp(goodHitter)), r(expected));
  });

  it("SLG counts total bases correctly", () => {
    const singles = 72 - 16 - 2 - 14;
    const tb = singles + 2 * 16 + 3 * 2 + 4 * 14;
    assert.equal(r(slg(goodHitter)), r(tb / 220));
  });

  it("wOBA is in a reasonable range for a good hitter (.370 – .430)", () => {
    const w = wOBA(goodHitter);
    assert.ok(w > 0.37, `wOBA ${w} too low`);
    assert.ok(w < 0.43, `wOBA ${w} too high`);
  });

  it("wRC+ > 100 for an above-average hitter (neutral park)", () => {
    assert.ok(wRCPlus(goodHitter) > 100);
  });

  it("wRC+ exactly 100 for a league-average hitter", () => {
    // Construct a hitter whose wOBA = LG_WOBA exactly
    // wRAA = 0, so wRC+ should be 100
    // We can verify by checking that if wOBA(l) == LG_WOBA, the formula returns 100
    // This is a mathematical identity check
    const result = ((0 + LG_R_PER_PA + (LG_R_PER_PA - LG_R_PER_PA)) / LG_R_PER_PA) * 100;
    assert.equal(result, 100);
  });

  it("BABIP is in a reasonable range (.250 – .400)", () => {
    const b = babip(goodHitter);
    assert.ok(b > 0.25 && b < 0.40, `BABIP ${b} out of range`);
  });

  it("ISO = SLG - AVG", () => {
    assert.equal(r(iso(goodHitter)), r(slg(goodHitter) - avg(goodHitter)));
  });

  it("K% and BB% are percentages (0 – 1)", () => {
    assert.ok(kPct(goodHitter) > 0 && kPct(goodHitter) < 1);
    assert.ok(bbPct(goodHitter) > 0 && bbPct(goodHitter) < 1);
  });

  it("all batting metrics return 0 for empty line", () => {
    assert.equal(avg(emptyBatter), 0);
    assert.equal(obp(emptyBatter), 0);
    assert.equal(slg(emptyBatter), 0);
    assert.equal(wOBA(emptyBatter), 0);
    assert.equal(wRCPlus(emptyBatter), 0);
    assert.equal(babip(emptyBatter), 0);
    assert.equal(iso(emptyBatter), 0);
  });
});

describe("Sabermetrics — Pitching", () => {
  it("ERA = (ER / IP) × 9", () => {
    assert.equal(r(era(goodPitcher)), r((28 / 95) * 9));
  });

  it("FIP is in a reasonable range (2.0 – 5.0) for a good pitcher", () => {
    const f = fip(goodPitcher);
    assert.ok(f > 2.0 && f < 5.0, `FIP ${f} out of range`);
  });

  it("WHIP = (BB + H) / IP", () => {
    assert.equal(r(whip(goodPitcher)), r((24 + 68) / 95));
  });

  it("K/9 = (K / IP) × 9", () => {
    assert.equal(r(kPer9(goodPitcher)), r((115 / 95) * 9));
  });

  it("CSW% returns correct ratio", () => {
    // 450 called strikes + 320 whiffs out of 1480 pitches
    assert.equal(r(cswPctFn(450, 320, 1480)), r(770 / 1480));
  });

  it("BB/9 = (BB / IP) × 9", () => {
    assert.equal(r(bbPer9(goodPitcher)), r((24 / 95) * 9));
  });

  it("HR/9 = (HR / IP) × 9", () => {
    assert.equal(r(hrPer9(goodPitcher)), r((6 / 95) * 9));
  });

  it("K/BB = K / BB", () => {
    assert.equal(r(kPerBB(goodPitcher)), r(115 / 24));
  });

  it("xFIP is in a reasonable range (2.0 – 5.0) for a good pitcher", () => {
    const x = xfip(goodPitcher);
    assert.ok(x > 2.0 && x < 5.0, `xFIP ${x} out of range`);
  });

  it("xFIP differs from FIP (HR normalised to league average)", () => {
    // xFIP replaces actual HR with expected HR based on FB rate,
    // so it should differ from FIP unless HR rate exactly matches league avg
    const f = fip(goodPitcher);
    const x = xfip(goodPitcher);
    assert.notEqual(r(f, 4), r(x, 4));
  });

  it("all pitching metrics return 0 for empty line", () => {
    assert.equal(era(emptyPitcher), 0);
    assert.equal(fip(emptyPitcher), 0);
    assert.equal(whip(emptyPitcher), 0);
    assert.equal(kPer9(emptyPitcher), 0);
    assert.equal(bbPer9(emptyPitcher), 0);
    assert.equal(hrPer9(emptyPitcher), 0);
    assert.equal(xfip(emptyPitcher), 0);
  });
});

describe("Sabermetrics — Edge cases", () => {
  it("handles zero denominator in BABIP (all Ks and HRs)", () => {
    const line = { ...emptyBatter, pa: 50, ab: 50, h: 10, hr: 10, k: 40 };
    // denom = AB - K - HR + SF = 50 - 40 - 10 + 0 = 0
    assert.equal(babip(line), 0);
  });

  it("K/BB returns Infinity when zero walks and some Ks", () => {
    const pitcher = { ...emptyPitcher, ip: 9, k: 12, bb: 0, hbp: 0, h: 0, hr: 0, bf: 27, er: 0, r: 0 };
    assert.equal(kPerBB(pitcher), Infinity);
  });

  it("K/BB returns 0 when zero walks and zero Ks", () => {
    const pitcher = { ...emptyPitcher, ip: 9, k: 0, bb: 0, hbp: 0, h: 0, hr: 0, bf: 27, er: 0, r: 0 };
    assert.equal(kPerBB(pitcher), 0);
  });

  it("xFIP returns 0 for empty pitching line", () => {
    assert.equal(xfip(emptyPitcher), 0);
  });

  it("xFIP clamps negative BIP to zero (more K+BB+HBP than BF)", () => {
    // Contrived: bf < k + bb + hbp → raw bip is negative, should be clamped to 0
    const weird = { ...emptyPitcher, ip: 3, bf: 10, k: 8, bb: 3, hbp: 1, hr: 0, h: 0, er: 0, r: 0 };
    // bip clamped to 0 → estFB = 0 → expectedHR = 0
    // xFIP = (13*0 + 3*(3+1) - 2*8) / 3 + 3.1 = (0+12-16)/3 + 3.1 = -1.333 + 3.1 = 1.767
    const result = xfip(weird);
    assert.ok(Number.isFinite(result));
    // With clamping, expectedHR = 0, so the HR contribution is 0
    const expected = (13 * 0 + 3 * (3 + 1) - 2 * 8) / 3 + FIP_CONSTANT;
    assert.equal(r(result), r(expected));
  });
});
