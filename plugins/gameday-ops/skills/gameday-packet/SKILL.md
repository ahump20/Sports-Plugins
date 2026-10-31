---
name: gameday-packet
description: Use when preparing a sports game packet, scoreboard brief or recap fact sheet, especially when game status, scores or source freshness may be incomplete.
---

# Game-day packet

Use for a single game, scoreboard brief, or recap fact sheet. This is not a prediction model or unattended game monitor.

## Workflow

1. Obtain the requested scoreboard or game detail from an available connected sports tool or a user-supplied source. For BSI college baseball, discover the actual MCP catalog and use `bsi_get_scoreboard` or `bsi_get_match_detail`; do not invent unavailable tool names. Record the provider, source URL, retrieval time, and any separately supplied coverage time.
2. Normalize only observed values using [the input contract](references/input-contract.md). Missing scores stay null. A generic provider state such as `post` is not enough to distinguish a final from a cancelled game; inspect the full status and flag ambiguity rather than guessing.
3. Run `python3 scripts/game_packet.py --input observations.json --format markdown` from this skill directory. Use `--format json` for structured output and `--strict` when stale/future retrievals should fail the check.
4. Return the packet with its source and warnings. A live leader is not a winner. Do not claim a comeback, turning point, injury, quotation, probability or record change unless separately sourced. Preserve the user's requested sport and writing voice.

The executable validates score types, final-game completeness, duplicate IDs and provenance. It computes final margins and winners only from final scores. An empty response means no games returned, not proof no games occurred. Fresh retrieval is not evidence of fresh season coverage.

## Failure and verification

On missing tools or failed requests, say what is unavailable and use supplied files only with an explicit offline label. Never swap in the bundled synthetic fixtures. The helper makes no network calls and no publication changes.

Run `python3 -m unittest discover -s tests -v` to check behavior. Exit codes: 0 processed, 1 strict freshness failure, 2 invalid input or file error. Correct the source input before retrying.
