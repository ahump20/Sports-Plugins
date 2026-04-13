# editorial-desk

**Editorial voice and workflow for sports journalism that centers the overlooked.** Three skills that hold the line on tone, fabrication, and research discipline.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install editorial-desk
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install editorial-desk
```

## What You Get

### 3 Skills

- **`bsi-voice-guide`** — tone and cadence for the Blaze Sports Intel voice: direct and decisive, genuine and vulnerable, emotionally grounded, raw and conversational. Prohibited phrases and their fixes. Mantras to use sparingly. No soccer.

- **`anti-fabrication-protocol`** — the hard rule against invented data, fabricated quotes, hallucinated sources, and freshness filler. Four failure modes to prevent, a pre-claim checklist, and uncertainty-handling language that says "I don't know" instead of inventing.

- **`research-workflow`** — source-validated five-phase research: frame → pull primary data → source secondary evidence → reconcile contradictions → draft + verify. Source hierarchy from primary BSI MCP down through mainstream journalism, with what's quotable (and what isn't).

### 2 Commands

- **`/editorial-brief`** — produce a research brief from a storyline prompt. Surfaces gaps in the data before drafting begins.
- **`/recap-draft`** — post-game recap draft enforcing the voice guide + anti-fabrication protocol. Complements `gameday-ops` plugin's `/gameday-recap` for quick-turn output.

## How it fits with other plugins

- `gameday-ops` produces rapid 30-minute recaps. `editorial-desk` handles the slower, deeper pieces — features, profiles, postseason breakdowns.
- `cbb-sabermetrics` + `texas-longhorns-intel` supply the data. `editorial-desk` turns data into prose without losing rigor.
- `site-ops` verifies what ships. `editorial-desk` governs what gets written in the first place.

## Non-negotiable rules encoded

- No invented stats, quotes, or sources.
- No freshness fabrication — timestamps come from metadata.
- Contradictory evidence surfaced, not hidden.
- Mid-major programs get the same analytical rigor as the blue bloods.
- No soccer.

## Origin

Codifies the editorial discipline Austin Humphrey runs at Blaze Sports Intel. This plugin does not replace the writer — it keeps the writer honest when the deadline is close and the temptation to fill a gap with fiction is high.
