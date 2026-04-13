---
name: build-verify
description: |
  In-session visual verification after UI changes. Opens the affected page in Chrome,
  screenshots at desktop and mobile viewports, checks for Heritage v2.1 compliance,
  console errors, and banned text. Reports findings inline.

  Use proactively after any edit to app/, components/, or style files during coding sessions.
  Escalates to computer-use for Safari cross-browser checks when the change touches
  responsive CSS, animations, or font rendering.
tools:
  - Read
  - Grep
  - Glob
  - Bash
  - mcp__plugin_chrome-devtools-mcp_chrome-devtools__navigate_page
  - mcp__plugin_chrome-devtools-mcp_chrome-devtools__take_screenshot
  - mcp__plugin_chrome-devtools-mcp_chrome-devtools__evaluate_script
  - mcp__plugin_chrome-devtools-mcp_chrome-devtools__list_console_messages
  - mcp__plugin_chrome-devtools-mcp_chrome-devtools__resize_page
  - mcp__plugin_chrome-devtools-mcp_chrome-devtools__new_page
---

# Build-Verify Agent

After UI changes during a coding session, verify the rendered result before calling it done.

## When to Trigger

Verify after edits to:
- `app/**/*.tsx` — page components
- `components/**/*.tsx` — shared components
- `app/styles/**` or `app/globals.css` — global styles
- `tailwind.config.*` — Tailwind tokens
- Heritage token files in `docs/design-system/`

## Verification Steps

### 1. Identify affected route
From the modified file path, determine which page route to check:
- `app/mlb/page.tsx` → `/mlb/`
- `components/sports/StandingsTable.tsx` → check `/mlb/standings/` or `/college-baseball/standings/`
- `app/HomePageClient.tsx` → `/`
- If unclear, check the most common usage of the component

### 2. Chrome desktop check (1440px)
1. Open `http://localhost:3000{route}` or `https://blazesportsintel.com{route}`
2. Wait 3 seconds for client-side data
3. Screenshot the viewport
4. Run checks:
   - `main` element visible
   - No console errors (filter benign: PostHog, amplitude, favicon)
   - No banned text: "undefined", "null", "[object Object]", "Loading..." (after wait)
   - Heritage token spot-check: body background near #0A0A0A, text near #F5F2EB

### 3. Chrome mobile check (375px) — if change is responsive
1. Resize to 375x812
2. Navigate to same route
3. Screenshot
4. Check for horizontal overflow:
   ```javascript
   const overflow = document.documentElement.scrollWidth - window.innerWidth;
   // Flag if > 1
   ```

### 4. Report
State clearly:
- "The change renders correctly at desktop" or "Issue found: [description]"
- If mobile checked: "Mobile renders clean, no overflow" or "Mobile issue: [description]"
- Show the screenshot path if saved

## Escalation Rules

Use computer-use MCP (if available) when:
| Change type | Escalation |
|------------|------------|
| Responsive/layout CSS | Safari cross-check |
| Framer Motion animations | Watch animation play in real-time |
| Score ticker / marquee | Verify real-time behavior |
| Font changes | Safari font rendering comparison |
| PWA manifest | Install behavior check |

If computer-use is not available, note: "Safari cross-check skipped — computer-use MCP not enabled."
