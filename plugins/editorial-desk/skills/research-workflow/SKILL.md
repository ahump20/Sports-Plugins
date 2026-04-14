---
name: research-workflow
description: "Source-validated research workflow for sports editorial — athlete profiles, program narratives, postseason bracket analysis, transfer-portal pieces, NIL valuation stories, community-impact features. Use when preparing to write, when a piece requires external research beyond the BSI MCP, when sourcing quotes or records, or when validating claims before publication. Triggers on: \"research\", \"source\", \"verify\", \"background\", \"prep for a feature\", \"investigate\", \"check the record\", \"find the quote\", \"fact-check\". Enforces source hierarchy, contradictory-evidence handling, and reproducibility — any researcher can retrace the sourcing path from the published piece."
---

# Research Workflow

How to research a sports editorial piece so every claim is traceable.

## Source hierarchy (strongest to weakest)

1. **Primary data via BSI MCP** — scoreboard, standings, team/player advanced metrics, match detail. Always preferred when available.
2. **Official sources** — NCAA.com, MLB.com, NFL.com, NBA.com, team official sites, conference sites, university athletics departments.
3. **Peer-reviewed and reference data** — Baseball Reference, Baseball Savant, FanGraphs, Pro-Football-Reference, Basketball-Reference, KenPom, Warren Nolan (D1 baseball RPI), D1Baseball.
4. **Mainstream sports journalism** — ESPN, The Athletic, Sports Illustrated, local beat writers. Useful for quotes and context, NOT for primary stats (use primary data instead).
5. **Podcasts and video** — when quoting, always confirm the exact language by listening; never paraphrase a podcast quote as if verbatim.
6. **Social posts** — only quotable if the account is verified and the post is preserved (screenshot + archived link).

Never quotable without escalation: anonymous forum posts, Reddit speculation, Twitter replies, generative AI output.

## Workflow (Five Phases)

### 1. Frame (15 min)

- What is the single claim this piece makes?
- What would falsify it? (If the answer is "nothing", the piece has no argument.)
- What is the strongest counter-read?

### 2. Pull primary data (30–60 min)

- Query the BSI MCP for every relevant `bsi_*` tool.
- Save the tool responses with their `meta.fetched_at` timestamps — these become citations.
- If the MCP doesn't cover the claim, document the gap and move to official sources.

### 3. Source secondary evidence (60–120 min)

- Official records first (rosters, bracket seeding, conference standings).
- Historical context via Baseball Reference / FanGraphs / KenPom for comparisons.
- Direct quotes from beat writers or official press conferences — with the full quote and link saved.

### 4. Reconcile contradictions (30 min)

- List every disagreement between sources.
- Note which is stronger by the hierarchy above.
- The piece surfaces the disagreement rather than hiding it.

### 5. Draft + verify (60–90 min)

- Draft with every claim annotated: `[source: BSI MCP bsi_get_team_sabermetrics, fetched 2026-04-12T14:30 CT]`.
- Before publishing, strip annotations into a sourcing appendix (internal) and keep a clean prose version (external).

## Reproducibility checklist

A published piece must allow any reader or editor to retrace the sourcing:

- [ ] Every stat has a cite (inline or footnote).
- [ ] Every quote has a link or a citation to the specific broadcast/press conference.
- [ ] Every historical comparison names the source dataset.
- [ ] `fetched_at` timestamps preserved for time-sensitive claims.
- [ ] If a claim is inference rather than data, prose says so ("the model suggests...", not "the data shows...").

## Common research traps

- **Confirmation bias** — you have the storyline before you have the data. Fix: write the counter-argument first, then draft the piece.
- **Recency bias** — last three games overweighted. Fix: always cite season-to-date and rolling 30-day side-by-side.
- **Prestige bias** — assuming an SEC program's 20-win run is more meaningful than a Sun Belt program's identical run. Fix: normalize by SOS via the Conference Power Index.
- **Sample-size denial** — drawing conclusions from 15 at-bats. Fix: state the sample explicitly, flag stability thresholds (wOBA stabilizes ~300 PAs).

## Deliverable

A research prep file saved alongside the piece:
- `research/<slug>.md` with sourcing log
- `research/<slug>-transcripts.md` with any quoted passages in full
- The piece itself references this file so an editor can audit.
