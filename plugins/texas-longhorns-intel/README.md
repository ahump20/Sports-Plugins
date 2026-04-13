# texas-longhorns-intel

**Texas Longhorns baseball intelligence — program doctrine plus live sabermetrics. Built on top of [`cbb-sabermetrics`](../cbb-sabermetrics/).**

Scouting reports, SEC matchup previews, roster evaluation with HAV-F scoring, NIL efficiency analysis, pre-series opponent briefs, and weekly intelligence digests. Every current-season claim verified against the live BSI MCP — no fabrication.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install cbb-sabermetrics
/plugin install texas-longhorns-intel
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install cbb-sabermetrics
codex plugins install texas-longhorns-intel
```

Plugin automatically resolves the `cbb-sabermetrics` dependency.

## Why This Exists

Texas baseball operates under a national championship standard — six CWS titles, 38 CWS appearances, 100+ MLB draft picks — and under current SEC conditions (joined 2024, Jim Schlossnagle head coach 2025-present). Generic college baseball analysis misses Texas-specific context: UFCU Disch-Falk Field park factors, SEC-era recalibration, NIL collective dynamics, Austin recruiting market. This plugin handles that context so the analysis is Texas-literate from the first sentence.

## What You Get

### 1 Agent

- **`texas-longhorns-baseball-intelligence`** — dispatches Texas-specific baseball questions with the program doctrine layer and live MCP data. Classifies requests into historical / live / mixed / analytical. Selects the right output mode. Enforces source discipline.

### 1 Skill (substantial)

- **`texas-longhorns-baseball-intelligence`** — the full operating system. Contains:
  - **Program identity layer** (history, coaching, venue, recruiting, Schlossnagle era)
  - **Live data layer** (10 MCP tools with selection heuristics)
  - **6 analytical frameworks** (HAV-F, MMI, Park Factors, Conference Strength, Leverage, Program Comparison)
  - **8-dimension comparison framework** for Texas vs any program
  - **NIL Efficiency framework** with HAV-F-to-NIL quadrant analysis
  - **8 output modes** (opsBriefing, internalMeeting, scoutingReport, editorialPiece, socialClip, hubContent, weeklyDigest, pressConferencePrep)
  - **Audience routing** (Austin, fans, coaches, NIL front offices, researchers)

### 3 Slash Commands

- **`/texas-digest`** — weekly Texas baseball intelligence digest with conference position, recent results, upcoming schedule, analytical read.
- **`/texas-matchup <opponent>`** — pre-series matchup preview using Opponent Intelligence framework. Park factors, SEC PI context, edge breakdown.
- **`/texas-scout`** — full roster scouting breakdown. Variants: `focus=offense`, `focus=pitching`, `focus=nil`, `focus=draft`.

## Dependencies

- **`cbb-sabermetrics`** (REQUIRED) — provides all 10 BSI MCP tools. This plugin cannot function without it. Install `cbb-sabermetrics` first.

## Example Queries

Once installed, try these in your Claude Code or Codex session:

```
How does Texas look this week?
```
→ The agent calls `bsi_get_team_sabermetrics team=texas`, `bsi_get_standings conference=SEC`, applies the program doctrine layer, returns an ops briefing.

```
Break down the Texas vs Arkansas matchup for this weekend.
```
→ Routes to `/texas-matchup arkansas`, fetches both teams' data, applies Opponent Intelligence framework, returns structured brief.

```
Which Texas players are undervalued on their NIL deals?
```
→ Routes to `/texas-scout focus=nil`, fetches roster stats, applies NIL Efficiency framework, returns Elite ROI and Overpaid quadrant plots.

```
Where does Texas stand in the SEC right now?
```
→ Agent combines `bsi_get_standings conference=SEC`, `bsi_get_conference_power_index`, returns SOS-adjusted positioning.

## Data Integrity

This plugin inherits and extends the `cbb-sabermetrics` integrity standard:

- **No fabrication.** If a tool returns empty, the agent says so.
- **Source attribution on every claim.** Every statistical assertion cites `meta.source` and `meta.fetched_at`.
- **Three-layer separation.** Every output separates Verified Facts / Inference / Recommendation.
- **Program doctrine as context only.** History informs expectations but never serves as proof of current-state quality.
- **No hometown discount.** Weaknesses named directly — if the bullpen is unstable, that's what we say.

## The Schlossnagle Context

Do not use Pierce-era framing as present-tense program identity. Texas shifted to Jim Schlossnagle in 2025. Coaching identity, roster construction priorities, and staff dynamics have recalibrated accordingly. The plugin keeps this current.

## Related Plugins

- [`cbb-sabermetrics`](../cbb-sabermetrics/) — the live-data foundation. Required dependency.
- Coming: `sports-storytelling` — for Texas editorial long-form content.
- Coming: `sports-viz` — for Texas-specific Savant-style charts.

## Troubleshooting

**Agent says tools are unavailable:**
- Confirm `cbb-sabermetrics` is installed in the same session.
- Check that the MCP server connected — look for errors in your session logs.

**Missing data for a current Texas player:**
- The BSI MCP covers 330 DI programs via Highlightly + BSI Savant. If a specific player is missing, it's likely upstream data — the agent will flag `unknown` rather than fabricate.

**Want to see the Texas Intelligence hub pages for reference:**
- Visit [blazesportsintel.com/college-baseball/texas-intelligence/](https://blazesportsintel.com/college-baseball/texas-intelligence/)

## License

[MIT](../../LICENSE) — use, fork, adapt, ship.

## Credit

Built by [Austin Humphrey](https://blazesportsintel.com) / Blaze Sports Intel. Texas baseball operating doctrine refined over multiple seasons of BSI coverage. Hook 'em.
