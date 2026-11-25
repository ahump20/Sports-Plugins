# College Baseball Sabermetrics accuracy repair

## Purpose

Answer college baseball questions with retrievable evidence: records, standings,
schedules, rosters, individual and team statistics, and documented calculations.
Austin's November 25, 2026 request authorizes repairing the existing plugin and
its data path. Preserve its identity, BSI connection and existing consumers.

## User flows

1. Resolve the requested season, association/division, team or player, and split.
2. Discover the actual MCP catalog and retrieve the supported observations.
3. Verify result identity, source season, statistical cutoff and coverage. Use
   season-specific school/conference/NCAA publications when the feed cannot
   establish a requested fact. Read the original page, not a search snippet.
4. Return useful sourced tables and calculations, with unresolved gaps visible.

The interface remains conversational. No new dashboard, authentication service,
subscription or unrelated UI is necessary for this repair.

## Architecture

- The existing remote server remains `sabermetrics.blazesportsintel.com/mcp`.
  Its implementation belongs to BSI's `workers/college-baseball-mcp`, not this
  repository. Server changes need their own tests and release evidence.
- A standalone Python 3.9+ helper in the plugin extracts attributed HTML source
  tables for hosts that can run local scripts. It supports explicit URL and
  saved-page inputs, verifies visible season evidence, bounds retrieval and
  preserves table structure. It does not independently certify a publisher,
  parse every PDF/JavaScript site, or install a new hosted MCP tool.
- Skills route web-only hosts to available search/page/browser capabilities.
  They never claim local execution or a remote deployment occurred without it.
- MCP smoke checks distinguish protocol connectivity from usable data. An empty
  JSON string, a current retrieval timestamp or a source label is insufficient
  proof of season coverage or factual accuracy.

## Data requirements

Preserve requested scope separately from observed scope. Retain source URLs,
source timestamps, retrieval time, season, split, identity, coverage, unknowns
and conflicts. A default roster for a new year cannot be joined to older stats.
Missing values are null/unavailable, not zero. Store or calculate innings as
outs. Derived metrics require all counts and applicable constants.

Official primary sources are preferred, but their conflicting sections must
still be checked. An HTTP block, unavailable category or unsupported season
must not become an empty successful leaderboard. Polls, statistical rankings,
standings and model ratings are separate outputs.

## Acceptance

- Reproduce the live defects and retain concise, attributed evidence.
- Test season mismatch, missing data, table alignment, ambiguous identities,
  unavailable sources and the distinction between connection and data checks.
- Verify historical Texas 2025 batting/record examples against official pages;
  these are historical checks, not current data fallbacks.
- Run the repository checks, package validation and an extracted-package CLI.
- Independently review the changed behavior. Submit dedicated PRs. Preserve
  production until the server release is explicitly authorized and verified.
