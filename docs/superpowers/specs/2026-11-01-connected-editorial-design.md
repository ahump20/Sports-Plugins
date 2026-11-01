# Connected Editorial Intelligence Desk

Status: proposed implementation design, pending Austin's approval. This document does not claim an integrated workflow has shipped.

## Outcome

One Texas team request and an optional editorial angle produce an evidence packet, supported calculations, an editorial briefing, a citation audit, and a Markdown draft for human review. Texas baseball is the first live slice. Matchup and broader Division I orchestration follow after identity/coverage adapters are validated. Other sports remain available through the existing foundational plugins; this does not expand BSI's college-baseball-only product scope.

## Existing pieces

The Texas library already has a bounded read-only MCP client and a source-packet CLI. Sports-Plugins has seven portable packages, an editorial evidence ledger, game packets, and tested sport calculations. A source packet preserves raw tool results and request arguments. A ledger checks citation presence, exact quotation containment, timestamps, and bounded arithmetic. Neither establishes that an excerpt or factual assertion is independently true.

## Approaches considered

1. A prompt-only coordinator is quick to add but cannot enforce request deduplication or a stable evidence boundary.
2. A local orchestration command reuses the current Texas client, produces a language-neutral evidence bundle, and hands it to the existing packaged editorial checker. This is the proposed first build because it needs no server, account migration, scheduler, or product deployment.
3. A hosted workflow service can eventually support the web and iOS, but adds deployment, storage, authentication, and operational responsibilities before the core workflow is proven.

The implementation choice in this proposal is option 2. Austin's roadmap supplies the outcome and release gates; the local command and the exact fields below are proposed engineering choices.

## Shared evidence boundary

Version a JSON Schema in Sports-Plugins and an equivalent exported TypeScript type in the Texas library. An integration compatibility test validates the actual released Texas CLI output against that schema and runs the released Python ledger against it. No source path may point into either development checkout.

Each bundle contains:

- A schema version, request ID, requested entity, resolved entity ID when supported, request scope, collection start/end, and America/Chicago display timezone. UTC timestamps retain their explicit offset.
- Sources with stable IDs, endpoint or original page URL, tool and arguments, retrieval time, provider source/fetched_at, explicit season and coverage time when supplied, raw result, and a content hash. Unknown coverage stays null and carries a warning.
- Claims with IDs, fact/calculation/quote/inference/opinion kind, text, source IDs, field or JSON-pointer references to the exact evidence, temporal scope, units and denominator where relevant, and validation state.
- Calculations with a named operation or metric, exact inputs, source-field references, coefficient provenance where required, output, precision policy, and limitations. Missing constants or components block the calculation; no unlabeled substitute is used.
- Explicit errors and missing inputs, with a per-stage status and overall complete/partial/blocked status. A tool error remains visible even if other sources succeed.

The bundle is the preserved source of truth for drafting. Draft generation never silently refetches or substitutes values.

## Orchestration

Extend the existing released Texas CLI with an editorial workflow option. Keep one `BlazeMcpClient` per request and a cache keyed by endpoint, tool name, and canonically ordered arguments. Failed requests are recorded, not stored as successful empty data. Only supported read-only tools are callable. A single request has bounded timeout and response sizes; there are no implicit retries or background work.

The first workflow collects standings, team schedule, and rankings once. It resolves Texas exactly using the current aliases. A name ambiguity blocks team-level calculations. Matchup and broader Division I identity resolution are later phases, not approximate-string-match shortcuts; the first command reports those unsupported scopes explicitly.

The proposed default `--scope snapshot` requests the latest available provider observation, with no claim that it represents a current season. `--scope current --season YYYY` requires the explicit season and source coverage to match it; the command never infers a baseball season from the calendar year. `--scope historical --season YYYY` requires the same explicit season match while allowing older retrieval under the historical policy. Default retrieval freshness is 24 hours, configurable explicitly. These are proposed engineering defaults for Austin to assess with this design.

Normalize observations into the evidence boundary, then calculate only transparent supported quantities such as wins divided by wins plus losses when the inputs and scope are supplied. A record with no season is described as an undated provider observation and is ineligible for a current-season claim. Advanced metrics require their actual inputs and published constants.

Produce a ledger consumable by the existing editorial helper, run the independently packaged checker, and render an editorial briefing and draft from documented claims. The command takes an explicit installed checker path or reports that external audit is unavailable; it never searches a development workspace. No shell command string is evaluated. Local output is opt-in and cannot overwrite input evidence.

## Draft and review behavior

The first draft is a deterministic factual briefing with an opening, source-supported findings, labeled interpretations, unanswered questions, citations adjacent to claims, and an evidence appendix. It does not manufacture quotations or claim a model-written narrative has passed human editorial review. Existing writing skills can revise voice while preserving claim IDs.

A documented ledger means that required fields and arithmetic are internally consistent. A separate review field records whether an original source was independently opened and whether it substantively supports the claim. Endpoint attribution alone is not independent verification. The output remains marked for human review until those checks are complete.

`--strict` exits nonzero for failed tools, unresolved identities, unsupported numerical claims, unavailable required audits, or missing season/coverage required by a current request. Partial output is still returned with explicit status and limitations. Malformed input is a different exit code from a valid partial collection.

## Acceptance and proof

1. Install released packages into a host environment outside both source checkouts. Invoke the editorial workflow and load all referenced components there.
2. Prove deduplication with a recording local MCP server; prove failure, malformed schema, unknown identity, conflicting coverage, stale retrieval, and missing metric inputs produce explicit partial/blocked results.
3. Validate each numerical claim's field references and recompute calculations from preserved evidence. A plausible number with a source ID but no matching evidence value must fail.
4. Run a live Texas request and save redacted public evidence, CLI version, release commit, host versions, timestamps, output hash, and explicit limitations. A fresh response alone cannot pass current-season coverage.
5. Check a human-readable draft against the preserved bundle. Do not call it publication-ready while source support or current coverage is unresolved.

## Fifty-request benchmark

Create a catalog with 10 Texas baseball, 15 other college baseball, 10 college football, 10 basketball, and 5 cross-source editorial requests. Each case declares expected capabilities, source requirements, failure behavior, and a human evidence rubric. Football and basketball exercise the general plugin catalog, not BSI product expansion.

Run cases against pinned releases and retain tool traces plus outputs. Numerical traceability requires every numerical claim to resolve to evidence fields or a reproducible calculation. Invented statistics and unlabeled substitutions are hard failures. Tool failures must always be explicit. Install/load, explicit skill invocation, natural-language triggering, and useful-answer quality are separate measurements. All 50 cases start as not run; a case catalog is not a measured quality result.

The first integration release is gated on the live Texas slice and its adversarial evidence checks above. Completing all 50 cross-sport cases is a later ecosystem-quality milestone, not a claim or condition of that first Texas release. Claude Code is the first clean host for measured trigger/invocation runs; Codex native install/component discovery is checked separately, with natural-language triggering measured only when a fresh Codex runtime is available.

## Later phases

After this slice passes, expand validated Division I identities and historical/conference/player coverage. Add scheduled game-day execution only after source coverage, timezone-aware schedules, freshness policies, retry limits, and failure notification ownership are defined. Web/iOS integration and hosted scheduling require their own concrete release scope.
