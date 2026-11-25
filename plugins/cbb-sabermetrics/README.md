# College Baseball Sabermetrics

Retrieve college baseball records, standings, schedules, rosters, team and
individual statistics with explicit seasons and sources. Version **0.4.0**
adds a standalone HTML source helper and official-source research workflow.

## What it can do

| Request | Retrieval path | Verification |
|---|---|---|
| Scores, standings, schedules, player observations and polls | Discover the connected BSI MCP tools and their current schemas | Check identity, source season, cutoff and coverage |
| School records, rosters, team/player statistics | Original season-specific school/conference pages and official cumulative PDFs | Inspect source headings and reconcile conflicting sections |
| National statistical leaders and records | Appropriate association/division statistics and record books | Preserve qualification rules, population and publication date |
| Reusable HTML source packet | Bundled Python helper in an execution-capable host | Raw aligned tables, source links/hash, explicit season evidence and limitations |
| Derived metrics | Companion baseball calculation skill with complete inputs | Formula, denominator and documented season/division constants |

The BSI feed covers NCAA Division I observations; it is not evidence that every
division or program is covered. Other college associations use their own official
publications. Search discovers sources; the original page must be inspected
before reporting a number.

## Use

Install `cbb-sabermetrics@Sports-Plugins` through the host's marketplace flow.
In Claude Code:

```text
/plugin install cbb-sabermetrics --marketplace ahump20/Sports-Plugins
```

Keep the existing BSI connection:

```text
https://sabermetrics.blazesportsintel.com/mcp
```

Ask for a season and task, for example:

> Get Texas's final 2025 overall and SEC records and Ethan Mendoza's batting
> line. Check the official source and preserve any rounding differences.

> Find the current Texas roster. State its published season before comparing
> it with last season's player statistics.

`/cbb-data`, `/cbb-scout` and `/cbb-leaderboard` use the same source checks.
A searched subset is labeled a selected-player comparison, not a national
leaderboard. The legacy `/cbb-power-index` produces a descriptive comparison,
not a calibrated rating.

## Run the source helper

Python 3.9+ standard library only; no API key or paid account is required.
Run from this plugin directory:

```bash
python3 skills/college-baseball-data/scripts/cbb_source.py --help

python3 skills/college-baseball-data/scripts/cbb_source.py \
  --url https://texaslonghorns.com/sports/baseball/stats/2025 \
  --season 2025 --kind stats --team Texas --format json

python3 skills/college-baseball-data/scripts/cbb_source.py \
  --input skills/college-baseball-data/tests/fixtures/texas-2025-batting-excerpt.html \
  --source-url https://texaslonghorns.com/sports/baseball/stats/2025 \
  --season 2025 --kind stats --team Texas --format markdown
```

The saved excerpt is an attributed **historical parser fixture**, not a current
feed or a complete source page. The live command retrieves the requested page.
Use `--kind roster|schedule|standings` with an appropriate discovered source;
`--output` creates a new file and refuses to overwrite existing files.

Results keep requested scope separate from observed season, include source URL,
retrieval information and aligned table cells, and state unknown completeness.
Blank cells stay null; source values are preserved as text instead of silently
coercing baseball innings or missing counts. See the
[input/output contract](skills/college-baseball-data/references/contract.md).
Wrong/ambiguous seasons, unavailable sources and unsupported markup produce
explicit error states. PDF and JavaScript-only sources need the host's PDF or
browser capabilities.

The helper does not authenticate a supplied saved page or certify a website as
official. Inspect the publisher and scope first. It does not normalize every
school template or calculate national leaderboards.

## Data accuracy

A fresh fetch is not a fresh season. An unversioned roster can already show
next year's players. Preserve overall/conference splits and W/L/T separately.
Missing HBP, sacrifice flies or conference records are not zero. Convert innings
to outs for arithmetic. Retain source-published and locally calculated rates
separately when display rounding differs.

An official page can contain a faulty summary widget: the verified Texas 2025
HTML has opponent-AB and double-play conflicts with its detailed totals/PDF.
The workflow retains source sections and requires reconciliation. See
[source routes and historical checks](skills/college-baseball-data/references/sources.md).

Use the installed baseball plugin for its `saber.py` calculations. Advanced
college metrics require applicable division/season counts and constants;
missing inputs remain unavailable. No forecast, WAR or power index is invented.

## Hosts and updates

Claude, Codex and portable manifests describe the same package. The Python
helper requires local execution. In web/mobile chat, the assistant uses the
connected MCP plus available page/browser/PDF tools; this package does not make
a local script callable as a hosted MCP tool.

The remote worker is maintained in BSI's `workers/college-baseball-mcp`.
A package update does not deploy that server. Discover the live catalog before
using newly added season, roster or team-stat capabilities.

## Verification and access

Run repository `npm run check`, `npm run package:plugins`, and the helper from
an extracted archive. Optional provider diagnostics:

```bash
node scripts/check-cbb-mcp.mjs --season 2025
SPORTS_LIVE=1 CBB_TEST_SEASON=2025 node --test tests/blaze-mcp.test.mjs
```

These repository commands separately report connectivity, source-contract
quality and data availability. They do not independently certify every fact.
A provider outage or rejected historical season must remain visible.

Public access does not grant unrestricted commercial redistribution. Respect
source terms, blocks and rate limits. No credentials are bundled, and this
package does not purchase data, publish research or change a subscription.
