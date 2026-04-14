---
name: editorial-brief
description: Produce a research brief for an editorial storyline — what we know, what we need, what we can't claim, before drafting begins.
---

# /editorial-brief

Pre-draft research brief.

## Usage

```
/editorial-brief topic="Dallas Baptist's regional bid"
/editorial-brief topic="Texas SEC pitching staff after Baton Rouge"
/editorial-brief topic="transfer portal impact on Big 12 rotations"
```

## What it does

Invokes the `research-workflow` skill's five-phase framing step and produces:

1. **The claim** — one sentence. What is the argument?
2. **What falsifies it** — the counter-read. If nothing falsifies it, the piece has no argument.
3. **Primary data pulls needed** — list of BSI MCP tool calls to run.
4. **Secondary sources** — official sites, records, beat writers worth contacting.
5. **Known gaps** — what the BSI MCP doesn't expose for this topic; whether those gaps are fatal or footnote-able.
6. **Estimated research time** — rough hours before drafting is possible.

## Output format

Saves to `research/<slug>.md` in the working directory.

## Rules

- The brief does not make claims; it maps what is needed to make claims.
- If the topic cannot be researched from available sources, the brief says so — and the piece does not proceed until gaps are closed or the topic is reframed.
