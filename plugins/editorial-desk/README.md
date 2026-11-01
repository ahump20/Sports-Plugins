# Editorial Desk

Audit claim provenance, quotations, freshness and arithmetic.

Python 3.9+; no dependencies, keys, paid APIs, background monitoring, or automatic publication. Supply source observations using the documented schema. These tools check structure and arithmetic, not source truth.

```bash
python3 skills/editorial-evidence/scripts/evidence_ledger.py --input input.json --format markdown
python3 -m unittest discover -s skills/editorial-evidence/tests -v
```

See [the workflow](skills/editorial-evidence/SKILL.md) and [input contract](skills/editorial-evidence/references/input-contract.md). JSON output is available with `--format json`; use `--strict` for a nonzero exit on unresolved freshness or documentation checks. `--output` writes only the requested output file. All included example observations are synthetic test fixtures.

## Claude Code installation

```text
/plugin install editorial-desk --marketplace ahump20/Sports-Plugins
```
