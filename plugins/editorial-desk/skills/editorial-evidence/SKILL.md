---
name: editorial-evidence
description: Use when checking a sports article, scouting brief or recap for missing evidence, quotation discrepancies, stale source dates or calculation errors.
---

# Editorial evidence desk

Use when preparing or checking a sourced article or sports brief. It does not rewrite an argument, authorize publication, or judge a writer's style unless asked.

## Workflow

1. Extract factual assertions, exact quotations, calculations and opinions without changing their meaning. Read each source using an available tool or the supplied original material. Never invent an excerpt, publication time, source URL or citation.
2. Build a ledger using [the input contract](references/input-contract.md). Keep facts, quotations, calculations and opinions distinct. Identify historical claims explicitly; the default freshness policy is for current claims.
3. Run `python3 scripts/evidence_ledger.py --input ledger.json --format markdown --strict` from this skill directory. JSON output is available with `--format json`.
4. Resolve each issue against the original source. A quotation must match a cited excerpt exactly. Arithmetic passes only for the supplied numbers, so separately verify inputs, units, dates, denominators and scope. A complete ledger means documented, not factually verified or approved to publish.
5. Return the evidence ledger and a short list of factual corrections. Preserve rhythm, opinion, structure and voice unless the user requests a rewrite. Identify conflicts between sources rather than silently selecting a convenient version.

## Boundaries

The helper checks local data only. Source retrieval time is not the statistical coverage date. Do not infer injuries, mental states, intent, NIL values or private information from a box score. Public facts need source support; opinion stays labeled opinion. No email, posting, source deletion or background monitoring occurs.

## Verification and errors

Run `python3 -m unittest discover -s tests -v`. Exit codes: 0 processed, 1 unresolved ledger with `--strict`, 2 invalid schema or file error. Missing tools are a limitation, not permission to manufacture a source. Never use the tests' synthetic observations in a real article.
