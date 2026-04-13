---
name: heritage-audit
description: Run a Heritage v2.1 visual compliance audit on a sports intelligence URL. Screenshots desktop and mobile, checks tokens, flags banned text.
---

# /heritage-audit

Heritage v2.1 visual compliance sweep.

## Usage

```
/heritage-audit url=https://blazesportsintel.com/scores
/heritage-audit url=/college-baseball         # relative = blazesportsintel.com
/heritage-audit url=... viewports=desktop,mobile,tablet
```

## What it does

1. Invokes the `build-verify` agent with the target URL.
2. Screenshots at desktop (1440×900) and mobile (390×844) by default.
3. Evaluates computed styles for each Heritage v2.1 token — confirms `--bsi-primary: #BF5700`, `--bsi-bone: #F5F2EB`, `--bsi-dust: #C4B8A5`, vintage border, surface colors all resolve correctly.
4. Checks for typography loading (Bebas Neue / Oswald / Cormorant Garamond / JetBrains Mono — if any are falling back to system fonts, flag it).
5. Greps rendered DOM for banned tokens (old glass-card classes, deprecated color vars).
6. Reads console messages — any error-level messages reported.
7. Returns: PASS / FAIL with the specific failure list.

## Escalation

- Font rendering or animation anomaly → escalate to `computer-use` for Safari cross-browser check.
- Heritage token mismatch → report exact computed value vs. expected, link to the offending CSS file.
- Banned text → list each occurrence with its DOM location.

## Rules

- Do not claim the audit passed until all screenshot and DOM checks return clean.
- Cache-bust every navigation (append `?v={timestamp}`) to avoid reading a stale CDN version.
