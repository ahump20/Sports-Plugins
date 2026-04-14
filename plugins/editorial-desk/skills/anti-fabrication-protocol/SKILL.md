---
name: anti-fabrication-protocol
description: "The hard discipline against invented data, fabricated quotes, hallucinated sources, and freshness filler in sports editorial. Use whenever writing content that makes factual claims about athletes, programs, games, stats, or markets. Triggers on: \"write\", \"draft\", \"recap\", \"feature\", \"profile\", \"report\", \"analysis\", \"post-game\", \"preview\", \"newsletter\". Enforces before-you-claim-it verification: every number sources, every quote real, every 'breaking' stamp derived from metadata not prose, every contradictory evidence surfaced rather than hidden. This protocol applies to all editorial output regardless of sport, urgency, or word count."
---

# Anti-Fabrication Protocol

The hard rule: zero invented facts in editorial output.

## The four failure modes to prevent

1. **Fabricated data** — inventing a stat, a record, a ranking, or a win probability the source doesn't support.
2. **Fabricated quotes** — attributing statements to people who did not say them.
3. **Hallucinated sources** — "sources say", "according to a person familiar with the situation", without a real source.
4. **Freshness fiction** — hardcoding "live", "just now", "current", "updated X minutes ago" without metadata backing.

## Before every claim, run the check

For every factual assertion in the draft:

- [ ] **Source exists** — name it or cite the tool response (`bsi_get_*`, `bsi_search_intel`, Highlightly, SportsDataIO, ESPN, D1Baseball, Baseball Reference).
- [ ] **Freshness from metadata** — if the prose implies freshness, the value comes from `meta.fetched_at`, never invented.
- [ ] **Quote is real** — either the source literally quoted this text, or the claim is paraphrased and the quote is cut.
- [ ] **Number is correct** — wOBA, wRC+, FIP, standings, records all match what the live source returned. No rounding errors that change the read.

## Uncertainty handling

When the data isn't there, say so. Never fill the gap with a plausible-sounding fiction.

**Acceptable patterns:**
- "The BSI MCP does not yet expose [metric] for [subject]; [alternative read]."
- "Public records do not show [event]; the question remains open."
- "Reporting on this story was not possible before deadline; this piece covers what is verifiable."

**Unacceptable:**
- "Sources familiar with the program indicate..." (with no source named)
- "Reports suggest..." (with no report cited)
- "The team is reportedly..." (classic hallucination vector)

## Contradictory evidence

If two sources disagree (BSI internal data vs. ESPN vs. D1Baseball), **surface the contradiction explicitly** rather than silently picking one:

> BSI's power index ranks Dallas Baptist 28th; D1Baseball's human poll ranks them 31st. The five-spot gap is typical for the model — it weights SOS harder than the human voters.

## Freshness stamps

Every data-surfacing piece ends with either:

- A footer with `source:` + `as of:` — timestamp from `meta.fetched_at`, formatted in America/Chicago.
- OR: no freshness claim at all.

Never use: "live", "current", "just updated", "most recent" as standalone adjectives without the timestamp behind them.

## Enforcement pre-publish

Before any editorial piece leaves this desk, the draft must pass:

1. **Grep for banned phrases** — "sources say", "reportedly", "word is", "live now" without `meta.fetched_at` backing.
2. **Trace every stat** — each numeric value maps to a tool response or a cited source.
3. **Quote audit** — every quoted sentence is either (a) literal from source material, or (b) cut.
4. **Freshness audit** — every temporal claim ("current", "breaking", "ongoing") has a timestamp source.

If any step fails, the piece does not ship.

## Why this matters

BSI's editorial credibility is the product. One fabricated quote, one invented stat, and the "we cover what mainstream media overlooks" positioning collapses. Rigor is the moat.
