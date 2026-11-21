# Roster comparison

`"Example College"` · `"baseball"` · `"2099"`
Identity namespace `"synthetic:example-college:2099"`

- **Earlier** `"2099-01-10T15:00:00Z"` · complete · **SYNTHETIC** · `"https://example.invalid/synthetic-roster/before"`
- **Later** `"2099-01-17T15:00:00Z"` · partial · **SYNTHETIC** · `"https://example.invalid/synthetic-roster/after"`

2 earlier records, 2 later records, 0 unchanged.

## Observed only in the earlier snapshot (1)

- `"Cam Rivera"` (ID `"ex-02"`). Later snapshot was partial. Coverage is unresolved.
  - Fields `{"number": 4}`

## Observed only in the later snapshot (1)

- `"Jordan Price"` (ID `"ex-03"`). Absent from the earlier snapshot declared complete.
  - Fields `{"number": 12}`

## Changed records (1)

- `"Ari Chen"` (ID `"ex-01"`)
  - Field `"number"`. `8` → `17`
  - Field `"position"`. `null` → (missing)

## Limits

- Counts describe supplied snapshots and their declared coverage. Claims of transfer, injury, eligibility, departure or cause require independent evidence.
- Different IDs are separate source records, including identical names. A source ID change can produce two observed-only records for one player.
- The later snapshot is partial. Coverage for IDs observed only earlier is unresolved.
