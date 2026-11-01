# Input contract

This is normalized input, not a claim that every provider returns these keys. Keep the original provider response beside the normalized file for inspection. All example names and scores below are synthetic.

```json
{
  "source": {
    "url": "https://example.org/scoreboard",
    "provider": "synthetic-example",
    "fetched_at": "2026-10-31T11:00:00Z",
    "data_as_of": null
  },
  "games": [{
    "id": "example-game-1",
    "status": "final",
    "away": {"name": "Away Fixture", "score": 2},
    "home": {"name": "Home Fixture", "score": 5},
    "venue": "Example Field",
    "start_time": "2026-10-31T08:00:00Z"
  }]
}
```

`source` and `games` are required. Provider and HTTPS source URL are required; timestamps need a timezone. `data_as_of`, venue and start time are optional. Do not use the download timestamp as `data_as_of` without provider support. Missing data-as-of generates a coverage warning.

Allowed status: `scheduled`, `in_progress`, `final`, `postponed`, `cancelled`, `suspended`. IDs must be unique. Team names must differ. Scores are nonnegative integers or null, never booleans or strings. Final scores must both be present. Scheduled scores must be null, not placeholder zeroes. A tied final has no winner. Non-final scores never generate a winner or final margin.

Freshness defaults to 24 hours since retrieval; change with `--max-age-hours`. `--now` accepts an ISO timestamp for reproducible offline tests, not for disguising old data as live. Output has schema_version, generated_at, source, freshness, warnings and games. `--strict` exits 1 for stale or future retrieval; warnings about unknown provider coverage remain visible even for a fresh retrieval.
