# Evidence ledger input

All text below is a synthetic example, not a sourced sports claim.

```json
{
  "sources": [{
    "id": "s1", "url": "https://example.org/box",
    "title": "Synthetic box score", "retrieved_at": "2026-10-31T11:00:00Z",
    "excerpt": "We played well."
  }],
  "claims": [{
    "id": "c1", "kind": "calculation", "text": "The sample margin is three.",
    "source_ids": ["s1"], "temporal_scope": "current",
    "calculation": {"operation": "difference", "inputs": [5, 2], "value": 3, "precision": 0}
  }]
}
```

Unique source and claim IDs are required. Sources need title, HTTPS URL and timezone-aware `retrieved_at`. Optional `published_at` must also be a timezone-aware timestamp. Optional `excerpt` must be actual source text; a source ID alone does not prove the excerpt is authentic.

Claims need ID, text and `kind`: fact, quote, calculation or opinion. Facts, quotes and calculations require known `source_ids`. Quotes use the exact quote as `text`, without adding decorative quote marks, and must be contained in one cited source excerpt. The script does not judge whether citations substantively support factual claims.

Calculation operations: sum (one or more inputs), difference, ratio, percentage (exactly two inputs). Percentage is numerator / denominator * 100. Inputs and claimed value must be finite numbers; division by zero fails. Optional precision is 0 through 6 decimal places (default 6) and sets absolute half-unit rounding tolerance. No expression evaluation or code execution is supported.

`temporal_scope` is current (default) or historical. Current claims fail freshness checks beyond 24 hours of retrieval unless `--max-age-hours` changes the policy. Historical claims do not fail solely because retrieval is old. Future retrievals fail for both. Fresh retrieval still does not prove fresh data coverage.

An empty ledger is incomplete. `--strict` returns 1 when claims remain unresolved. The JSON output includes completeness, limitations, documented/opinion/unresolved status per claim, computed results, sources and issue messages. No numerical "truth score" is produced.
