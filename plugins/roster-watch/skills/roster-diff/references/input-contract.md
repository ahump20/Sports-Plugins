# Roster snapshot contract

Provide two UTF-8 JSON objects. The objects use these exact top-level keys.

| Key | Value |
| --- | --- |
| `sport` | Nonempty string, such as `baseball`. |
| `team` | Nonempty string for the team or club. |
| `season` | Nonempty string, such as `2026`. |
| `identity_namespace` | Nonempty string describing the authority and scope of the IDs, such as `school-athletics:baseball:2026`. Use an authority ID across sources only if both preserve it. |
| `observed_at` | Capture time as `YYYY-MM-DDTHH:MM:SS` with optional one to six fractional digits, followed by `Z` or a numeric offset such as `-06:00`. This is when the roster was observed. |
| `source` | Object with `url` and `completeness` plus optional boolean `synthetic`. |
| `players` | Array of player records. An empty array is valid. |

`source.url` is an absolute HTTP(S) URL with a host and no embedded username or password. Remove credential-bearing query parameters before saving a capture. `source.completeness` is the string `complete` or `partial`. Declare `complete` only when the capture covers the source roster as presented for the stated scope. Declare `partial` for an excerpt, filtered data or uncertain coverage. Set `source.synthetic` to `true` for fabricated examples or test inputs.

Each player object has an exact, nonempty string `id` and a nonempty string `name`. An optional `fields` object holds attributes such as `number`, `position` or `profile_url`. Field values can be JSON strings, booleans, finite numbers, `null`, arrays or objects. Preserve an explicit `null` and omit an attribute when it was unobserved. An omitted `fields` object supplies zero attributes. Duplicate IDs and duplicate JSON object keys are errors. Surrounding whitespace on scope strings, IDs and names is an error. Extra attributes belong inside `fields`.

The four scope keys must match exactly. Use an ID the source can legitimately keep stable across the two captures. Season-specific IDs apply only to that season. Exact IDs determine matches, including when names repeat. A later observation can have the same timestamp instant as the earlier one. Reversed observation times fail after accounting for offsets.

## Report contract

`compare_rosters(before, after)` accepts decoded snapshots and returns the same report used by the CLI. Invalid snapshots raise `ValueError`. Array results are ordered by exact ID and field changes by field name, with a player name change first. JSON object key order has no effect, while array order and value types matter.

- `scope`, `snapshots`, `counts` and `limitations` hold the comparison scope, verbatim source metadata and timestamps, counts and interpretation limits.
- `observed_only_before` and `observed_only_after` hold full observed records and a `comparison` code. A missing ID in a snapshot declared complete is labeled `absent_from_before` or `absent_from_after`. A missing ID in a partial snapshot is labeled `before_coverage_unresolved` or `after_coverage_unresolved`.
- `changed` holds the matched `id`, full `before` and `after` records, and `fields` with each changed `path`. A field path is `["name"]` or `["fields", "attribute"]`. A field state is `{"present": false}` when omitted, and `{"present": true, "value": null}` when explicitly null. A `true` and a `1` are distinct values.

The reports describe the supplied captures and rely on declared completeness and ID stability. Confirm a changed name or ID with the original source before drawing conclusions about player identity. Establish any change in player status or its cause using independent evidence.
