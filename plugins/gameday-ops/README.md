# Game-day Operations

Build sourced game packets with tested status and score handling.

Python 3.9+; no dependencies, keys, paid APIs, background monitoring, or automatic publication. Supply source observations using the documented schema. These tools check structure and arithmetic, not source truth.

```bash
python3 skills/gameday-packet/scripts/game_packet.py --input input.json --format markdown
python3 -m unittest discover -s skills/gameday-packet/tests -v
```

See [the workflow](skills/gameday-packet/SKILL.md) and [input contract](skills/gameday-packet/references/input-contract.md). JSON output is available with `--format json`; use `--strict` for a nonzero exit on unresolved freshness or documentation checks. `--output` writes only the requested output file. All included example observations are synthetic test fixtures.

## Claude Code installation

```text
/plugin install gameday-ops --marketplace ahump20/Sports-Plugins
```
