---
name: visual-audit
description: |
  On-demand visual audit of BSI properties using a tiered tool strategy:
  Chrome for fast web sweep, computer use for Safari cross-browser and design judgment,
  Playwright for CI regression baselines.

  Triggers: "/visual-audit", "audit the site visually", "check all pages",
  "visual sweep", "design audit", "cross-browser check"
---

# BSI Visual Audit

Sweep BSI properties for visual issues, design drift, and cross-browser rendering problems.
Produces a structured findings report.

## Arguments

- `flagship` (default) — blazesportsintel.com only
- `arcade` — arcade.blazesportsintel.com only
- `portfolio` — portfolio site only
- `all` — all three properties
- `safari` — Safari cross-browser check only (requires computer-use MCP)
- `design` — design judgment pass only (requires computer-use MCP)

## Route Priority List

### Flagship (blazesportsintel.com)
```
/                              # Homepage data dashboard
/scores                        # Scores hub
/college-baseball              # CBB landing
/college-baseball/scores       # CBB scores
/college-baseball/standings    # CBB standings
/college-baseball/savant       # Savant leaderboard
/mlb                           # MLB landing
/mlb/scores                    # MLB scores
/mlb/standings                 # MLB standings
/nfl                           # NFL landing
/nba                           # NBA landing
/pricing                       # Pricing page
/about                         # About page
/podcast                       # Podcast page
```

### Arcade (arcade.blazesportsintel.com)
```
/                              # Arcade landing
```

### Portfolio
```
/                              # Portfolio landing
```

## Phase 1: Chrome Sweep (Fast)

Use Claude in Chrome (mcp__claude-in-chrome__* tools) or the chrome-devtools-mcp plugin.
For each route in the target scope:

### Desktop pass (1440px viewport)
1. Navigate to the route
2. Wait for main content to be visible (wait for `main` element)
3. Wait 2 seconds for client-side data to load
4. Screenshot the full page
5. Run checks (see Checks section below)

### Mobile pass (375px viewport)
1. Resize to 375x812
2. Navigate to the same route
3. Wait for main content
4. Screenshot
5. Run overflow check (see below)

### Checks per page
Run these checks via JavaScript evaluation or DOM inspection:

**Content integrity:**
- Page returns 200
- `main` element is visible
- No banned text in body: "Loading..." (after 3s wait), "undefined", "null", "[object Object]", "No data" (when data should exist), empty `<table>` or `<tbody>` with zero rows
- No console errors (filter benign: PostHog, amplitude, favicon, Failed to load resource)

**Heritage v2.1 compliance (spot-check):**
- Check 3 elements for computed background-color against Heritage surfaces:
  - A card element: should use `#161616` (surface-dugout) or close
  - The page background: should use `#0A0A0A` (surface-scoreboard) or close
  - A nav/header element: should use `#111111` (surface-press-box) or close
- Check primary text color: should be near `#F5F2EB` (bsi-bone)
- Check for forbidden colors: any SaaS blue (`#007bff`, `#0d6efd`), purple gradients, `#1A1A2E`

**Mobile overflow (375px only):**
```javascript
// Reuse pattern from tests/smoke/mobile-overflow.spec.ts
const viewportWidth = window.innerWidth;
const docOverflow = document.documentElement.scrollWidth - viewportWidth;
const bodyOverflow = document.body.scrollWidth - viewportWidth;
// Flag if either > 1
```

### Classification
For each finding, assign severity:
- **CRITICAL** — broken layout, missing content, console error, data not rendering
- **WARNING** — Heritage color drift, minor overflow, spacing inconsistency
- **NOTE** — polish items, minor typography issues, non-blocking visual feedback

## Phase 2: Computer Use Layer (Targeted)

**Requires:** computer-use MCP server enabled via `/mcp`. Skip this phase if not available.

### Safari cross-browser check
1. Use computer-use tools to open Safari
2. Navigate to the top 5 flagship routes:
   - `/`
   - `/scores`
   - `/college-baseball`
   - `/mlb`
   - `/pricing`
3. Screenshot each page in Safari
4. Compare visually against Chrome screenshots from Phase 1
5. Flag Safari-specific issues:
   - Font rendering differences (Safari uses different font smoothing)
   - CSS grid/flexbox gap rendering
   - Scrollbar appearance (Safari overlay scrollbars vs Chrome)
   - Sticky header behavior
   - Backdrop-filter rendering differences
   - Score ticker animation behavior

### Design judgment pass
Using the screenshots captured in Phases 1 and 2, evaluate each key page as a design reviewer:

**Visual hierarchy check:**
- Does the eye flow correctly? Hero -> section headers -> content -> footer
- Is there a clear primary action on the page?
- Are section breaks clear without being heavy-handed?

**Spacing consistency:**
- Are card gaps uniform across the page?
- Do margins and padding feel consistent between sections?
- Is the vertical rhythm maintained?

**Typography scale check:**
- Hero headings: Bebas Neue at large clamp sizes
- Section headings: Oswald, uppercase
- Body text: Cormorant Garamond
- Data/code: JetBrains Mono
- Do the sizes step down correctly?

**Heritage "feel" check:**
- Does the page feel like a heritage newsroom/dugout, or has it drifted toward generic SaaS?
- Are burnt-orange accents used for identity moments (stamps, CTAs, rules)?
- Is columbia blue reserved for data/links only?
- Is grain texture present but not overwhelming?
- Are corner-marks used appropriately on featured cards?

### iOS Simulator (optional)
Only if Xcode and iOS Simulator are installed:
1. Open iOS Simulator via computer use
2. Open Safari in the simulator
3. Navigate to blazesportsintel.com
4. Tap through: homepage, scores, a team page
5. Screenshot key screens
6. Flag iOS WebKit-specific rendering issues

## Phase 3: Report Generation

Save report to `docs/audits/YYYY-MM-DD-visual-audit.md` with this structure:

```markdown
# Visual Audit Report — YYYY-MM-DD

## Summary
- **Properties audited:** [list]
- **Pages checked:** N
- **Issues found:** N (X critical, Y warning, Z note)
- **Cross-browser deltas:** N (Safari vs Chrome)

## Findings by Page

### [route] — [STATUS: PASS | CRITICAL | WARNING]
- **Desktop:** [description]
- **Mobile:** [description]
- **Issues:** [list with severity]

## Cross-Browser (Safari vs Chrome)
[Only if Safari check was run]

## Design Judgment Notes
[Only if design check was run]

## iOS Simulator
[Only if iOS check was run]

## Recommendations
[Prioritized list of fixes, grouped by severity]
```

## Post-Audit

After generating the report:
1. Display the summary inline (issues count, critical items)
2. If critical issues found, list them explicitly
3. Save the full report to the file path above
4. Do NOT auto-fix unless Austin asks — the report is the deliverable

## Existing Patterns to Reuse

- **Overflow evaluator:** `tests/smoke/mobile-overflow.spec.ts` — `createOverflowEvaluator()`
- **Banned placeholders:** `tests/e2e/production-audit.spec.ts` — `BANNED_PLACEHOLDERS`
- **Truthful state:** `tests/e2e/production-audit.spec.ts` — `assertTruthfulState()`
- **Heritage tokens:** `docs/design-system/heritage-tokens-reference.css`
- **Heritage spec:** `docs/design-system/heritage-v2.1-spec.md`
