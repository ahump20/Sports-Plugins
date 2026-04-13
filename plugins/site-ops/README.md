# site-ops

**Site operations for sports intelligence platforms.** Visual compliance, deploy gates, and skill-package curation — the tooling that keeps a live sports site honest.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install site-ops
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install site-ops
```

## What You Get

### 1 Skill

- **`visual-audit`** — systematic visual audits of sports intelligence properties. Checks Heritage v2.1 tokens (burnt-orange #BF5700, bone #F5F2EB, dust #C4B8A5, vintage border), typography (Bebas Neue / Oswald / Cormorant Garamond), heritage stamps, corner marks, grain overlay. Catches banned text and old glass-card tokens that should have been removed.

### 2 Agents

- **`build-verify`** — in-session visual verification after UI changes. Opens the affected page in Chrome, screenshots at desktop and mobile viewports, checks for Heritage v2.1 compliance, console errors, and banned text. Escalates to computer-use for Safari cross-browser checks when the change touches responsive CSS, animations, or font rendering. **Use proactively** after any edit to `app/`, `components/`, or style files.

- **`skill-package-curator`** — read, validate, and publish `.skill` package manifests. Enforces BSI naming conventions (`bsi-{domain}-{function}` workers, `BSI_{DOMAIN}_{PURPOSE}` KV namespaces), the anti-mock-data protocol, the four-state data surface requirement, and the `meta: { source, fetched_at, timezone }` response shape. Integrates with the `universal-skills-marketplace.skill` manifest at `BSI-repo/skill-packages/`.

### Bundled MCP

- **chrome-devtools** (stdio) — via `npx chrome-devtools-mcp@latest`. Powers the `build-verify` agent's screenshot and console-message checks. Auto-starts on plugin activation.

## Heritage v2.1 reference (for quick lookup)

| Token | Value | Use |
|---|---|---|
| `--surface-dugout` | #161616 | Cards |
| `--surface-scoreboard` | #0A0A0A | Hero background |
| `--surface-press-box` | #111111 | Table headers |
| `--bsi-primary` | #BF5700 | Stamps, borders, buttons (burnt-orange) |
| `--bsi-bone` | #F5F2EB | Primary text |
| `--bsi-dust` | #C4B8A5 | Secondary text |
| `--heritage-columbia-blue` | #4B9CD3 | Data links |
| `--border-vintage` | rgba(140,98,57,0.3) | Subtle borders |

**Typography:** Bebas Neue hero headings at `clamp(2.5rem, 6vw, 5rem)`. Oswald section headings (uppercase). Cormorant Garamond body. JetBrains Mono code.

**Classes:** `.heritage-stamp` · `.heritage-card` · `.btn-heritage` / `.btn-heritage-fill` · `.corner-marks` (20px inset) · `.grain-overlay` (scoped)

## Non-negotiable rules enforced

- **No mock data.** Pre-commit hook and the build-verify agent both block `Math.random()` in data contexts, `mockGames`, `sampleData`, `faker.`, hardcoded team/score objects.
- **No freshness fabrication.** No hardcoded "live", "updated just now", "current" strings. Freshness comes from `meta.fetched_at`.
- **Verification before completion.** "Build passed" is not verification. Must `curl` the affected URLs and confirm real data appears.

## Origin

Ported from Blaze Sports Intel workspace:
- `visual-audit` skill from `BSI-repo/.claude/skills/visual-audit/`
- `build-verify` agent from `BSI-repo/.claude/agents/build-verify.md`
- `skill-package-curator` agent from `~/.claude/agents/skill-package-curator.md`
