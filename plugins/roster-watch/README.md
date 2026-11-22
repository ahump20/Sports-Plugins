# Roster Watch

Compare two roster captures for the same sport, team, season and player ID namespace. The report shows which IDs appear only in one capture, which fields changed for matching IDs, and where partial source coverage leaves a difference unresolved. Each report retains both source URLs and observation times.

Supply two UTF-8 JSON snapshots using the [input contract](skills/roster-diff/references/input-contract.md). Use stable source IDs and declare each capture's completeness. The comparison runs offline with Python 3.9+ and its standard library.

## Run the synthetic example

Run these commands from this package directory.

```bash
roster_diff=skills/roster-diff
python3 "$roster_diff/scripts/roster_diff.py" \
  --before "$roster_diff/examples/before.json" \
  --after "$roster_diff/examples/after.json" \
  --format markdown
python3 "$roster_diff/scripts/roster_diff.py" \
  --before "$roster_diff/examples/before.json" \
  --after "$roster_diff/examples/after.json" \
  --format json --output roster-report.json
```

The **synthetic** example shows one jersey number change and one field omission under the same ID. One player appears only in the earlier capture, and the later capture's partial coverage leaves that player's roster status unresolved. A different ID appears only in the later capture and is absent from the earlier capture declared complete. Claims about transfers, injuries, eligibility, departures or causes require independent evidence.

The CLI writes Markdown to stdout by default. `--output` writes a separate file and rejects paths that alias either input. Invalid inputs or file errors exit with status 2.

## Claude Code installation

```text
/plugin install roster-watch --marketplace ahump20/Sports-Plugins
```
