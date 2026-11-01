---
name: conference-strength
description: Use when comparing college baseball conferences, contextualizing a team's record, or separating conference standings and poll representation from schedule-strength and postseason claims.
---

# Conference comparison without an invented index

Standings alone cannot establish strength of schedule. Treat conference tables and poll representation as descriptive observations, not calibrated ratings.

## Workflow

1. Resolve the requested season, conferences and statistical cutoff. Discover the live tools, then read `bsi_get_standings` and `bsi_get_rankings`. For an individual team's opposition, also read `bsi_get_team_schedule`.
2. Check conference coverage, unique team identity and matching time scope. Preserve source and provider fetch metadata separately from the client retrieval time. Missing teams or a missing season prevents a complete-population claim.
3. Show supported measures: supplied team records, published poll positions, and a count of matched ranked teams. A poll count is a statement about that poll, not proof of opponent strength or tournament qualification.
4. Only aggregate complete, compatible numeric fields. Summed team decisions count an intraconference game twice; intraconference wins and losses cancel in the aggregate, but the denominator still includes those decisions. Do not call an all-games run differential per team-game a nonconference-only rate. A nonconference comparison needs game-level classification and complete coverage.
5. Explain what additional evidence would resolve a schedule-strength or postseason question: a sourced opponent-adjusted method, game-level schedule, current selection criteria and relevant results. Do not construct a power index by mixing poll counts, record and run differential without a defined, validated method.

## Output

Use a comparison table headed **Descriptive conference comparison**, followed by a method note and missing-data statement. When sorting a supported field, name that field; do not relabel its order as overall conference strength. Treat every program under the same evidentiary standard, including mid-majors. Conference prestige does not prove a particular team's schedule was harder.

## Failure and limits

Unavailable data remains unavailable. Never infer an automatic bid from regular-season standings alone or eliminate an at-large case solely from conference identity. Check the applicable tournament format and official criteria. This workflow produces no bracket forecast, hidden difficulty multiplier or empirically calibrated conference score.
