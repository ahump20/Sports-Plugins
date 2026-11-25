# MCP integration and data verification

The `cbb-sabermetrics` plugin connects to:

```text
https://sabermetrics.blazesportsintel.com/mcp
```

The owning server source is BSI's `workers/college-baseball-mcp`. Updating a
Sports-Plugins package does not deploy that worker. The endpoint was reachable
as server version 4.0.0 on November 25, 2026; discover its current catalog and
schemas rather than treating this observation as a permanent contract.

## Discover before calling

The observed v4 catalog had these seven read-only tools:

| Tool | Observed v4 inputs | Data category |
|---|---|---|
| `bsi_get_scoreboard` | Optional date, conference | Scores |
| `bsi_get_standings` | Optional conference | Provider standings |
| `bsi_get_rankings` | None | Published poll |
| `bsi_get_player_stats` | Player, optional team | Player observations |
| `bsi_get_team_schedule` | Team | Schedule/results |
| `bsi_get_match_detail` | Match ID | Provider match detail |
| `bsi_search_intel` | Query, optional limit/domains | Source discovery |

That version did not accept season arguments and did not expose roster or
team-stat tools. New capabilities must be discovered after a verified server
update; never send invented arguments or claim they were honored. A historical
request must not silently fall back to the provider's default season.

The source helper in `skills/college-baseball-data` is a separate Python
workflow for execution-capable hosts. Web-only hosts inspect official sources
with their available page/browser/PDF tools.

## Evidence contract

A useful season-sensitive response needs more than a source label:

```json
{
  "status": "partial",
  "meta": {
    "source": "identified-provider",
    "source_urls": ["https://example.org/baseball/2025"],
    "requested_season": 2025,
    "season": 2025,
    "season_verification": "source-season-field",
    "source_as_of": null,
    "fetched_at": "2025-06-01T12:00:00Z",
    "retrieved_at": "2026-11-25T12:00:00Z",
    "coverage": "selected observed rows; completeness not established"
  }
}
```

This is an illustrative contract, not a live observation. A null source cutoff
is honest but cannot establish currentness or final-season completeness. Keep
provider fetch/cache time separate from response retrieval time. Do not replace
absent source season with the year the user requested.

Statuses distinguish available/partial observations, unavailability and
ambiguous identities. Failed requests and empty rankings do not count as data
success. Preserve missing counts as null, keep statistical splits separate, and
require source evidence before selecting among duplicate player names.

The plugin retains the existing remote transport configuration. It does not
promise a permanent rate limit, cache duration, complete provider catalog or
broad data license. Inspect observed 429/error responses and respect source
access conditions; do not repeatedly hammer a blocked provider.

## Diagnose and verify

From the repository root:

```bash
node scripts/check-cbb-mcp.mjs --season 2025
SPORTS_LIVE=1 CBB_TEST_SEASON=2025 node --test tests/blaze-mcp.test.mjs
```

The diagnostic performs initialization, catalog discovery and four bounded,
read-only seasonal queries. It never calls the paid intelligence-search route.
It accepts additional tools without freezing the server to seven names.

It reports three separate things: connectivity, contract checks and data
availability. Explicit unavailability can satisfy the metadata contract while
still failing the data-availability gate. Neither proves independent factual
accuracy; that requires comparison with source pages and arithmetic checks.

Offline regression tests reject missing/mismatched seasons, empty successful
rankings, unsupported input schemas, lost source cutoffs, impossible records and
selected records in an ambiguous result. Historical source checks live in the
college-baseball-data package.

See [the source guide](../plugins/cbb-sabermetrics/skills/college-baseball-data/references/sources.md)
for official-school/conference/association fallbacks and known source pitfalls.
MCP protocol reference: [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).
