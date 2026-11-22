# Sports Plugins

Tools for sports writers, analysts and fantasy managers using Claude Code or Codex. Calculate a rate, check a claim, prepare a game packet, compare roster snapshots or work through a playoff race—with the inputs and limitations attached.

Maintained by [Austin Humphrey](https://github.com/ahump20), founder of [Blaze Sports Intel](https://blazesportsintel.com).

## Choose a workflow

| What you need to do | Plugin | What you get | Inputs |
|---|---|---|---|
| Calculate and explain baseball metrics | [Baseball](plugins/baseball/) | wOBA, wRC+, FIP, rate and sample-size checks; rules and source guidance | Counting stats and the relevant league/season constants |
| Explain a football performance | [Football](plugins/football/) | NFL and college EPA, success rate and quarterback calculations; rules and source guidance | Supported play-by-play or player data |
| Compare basketball efficiency | [Basketball](plugins/basketball/) | Possessions, ratings, Four Factors and true shooting; rules and source guidance | Supported NBA or college box scores |
| Retrieve college baseball observations | [CBB Sabermetrics](plugins/cbb-sabermetrics/) | Source-attributed results from the BSI MCP endpoint | Network access and fields actually returned by the provider |
| Prepare Texas baseball research | [Texas Longhorns Intel](plugins/texas-longhorns-intel/) | Scouting, opponent and editorial workflows with evidence requirements | CBB Sabermetrics plus verified program context |
| Assemble a game-day brief | [Gameday Ops](plugins/gameday-ops/) | Status-aware game packets with score and freshness checks | Supplied game observations and sources |
| Check a story's evidence | [Editorial Desk](plugins/editorial-desk/) | Claim ledger, exact excerpt checks, arithmetic and citation completeness | Supplied claims and source excerpts |
| See what changed on a roster | [Roster Watch](plugins/roster-watch/) | Newly listed, absent and changed records; coverage and identity caveats | Two dated snapshots with the same team, season and identity namespace |
| Work through a playoff race | [Playoff Lab](plugins/playoff-lab/) | Seed ranges, qualification bounds and conditional scenarios | Standings, complete remaining schedule and explicit supported seeding rules |

All nine packages include Claude, Codex and portable manifests. The local Python helpers run on supplied data without API keys. Live retrieval is a separate capability and depends on the provider. These packages require a host that can execute local scripts; a manifest alone does not make a script callable in web-only chat.

## Install

### Claude Code

Run in a Claude Code session:

```text
/plugin marketplace add ahump20/Sports-Plugins
/plugin install roster-watch@Sports-Plugins
/plugin install playoff-lab@Sports-Plugins
```

Choose the scope in the plugin panel. Substitute any package name from the table. [Claude's installation guide](https://code.claude.com/docs/en/plugins/install) explains scope and activation.

### Codex

```bash
codex plugin marketplace add ahump20/Sports-Plugins
codex plugin add roster-watch@Sports-Plugins
codex plugin add playoff-lab@Sports-Plugins
```

The Codex CLI uses `plugin add`. In the desktop app, install from the added marketplace in the Plugins Directory. Commands above use the default branch. Preview an unmerged change by selecting its branch when adding the marketplace or by using a local checkout; a checkout is optional.

After installation, ask:

> Use Roster Watch to compare these two roster snapshots. Show the changes and anything the sources cannot establish.

> Use Playoff Lab to show my possible seeds and what changes if I win this week's game. Keep unresolved tiebreakers visible.

## Try the calculations without installing a plugin

Clone this repository and run these commands from its root. Python 3.9+ is enough; the examples are **synthetic fixtures**, not current teams or a connected fantasy league.

```bash
python3 plugins/roster-watch/skills/roster-diff/scripts/roster_diff.py \
  --before plugins/roster-watch/skills/roster-diff/examples/before.json \
  --after plugins/roster-watch/skills/roster-diff/examples/after.json \
  --format markdown

python3 plugins/playoff-lab/skills/playoff-scenarios/scripts/playoff_scenarios.py \
  --input plugins/playoff-lab/skills/playoff-scenarios/examples/league.json \
  --format markdown
```

Both also emit JSON. Each plugin's README links its exact input contract and examples.

## What the results mean

- **A roster difference is a source observation.** An omitted name does not prove a transfer, injury, dismissal or eligibility change. Partial snapshots cannot establish a complete roster difference.
- **A playoff scenario is conditional on its rules.** Playoff Lab handles one overall table and explicitly supported tiebreak treatment. It reports unresolved ties as ranges. Equal-weight outcome counts are not forecast probabilities.
- **A retrieved response can still be incomplete.** Preserve source, season, statistical coverage and retrieval time separately. Missing fields stay missing.
- **An evidence check has a defined scope.** Matching a quote to a supplied excerpt confirms the match; it does not independently authenticate the source or establish the truth of every claim.
- **A formula needs the right context.** Legacy TypeScript defaults in [lib/sabermetrics.ts](lib/sabermetrics.ts) are illustrative, not NCAA-calibrated constants. Use the baseball workflow with explicit league and season inputs.

[Practical workflows](docs/USE-CASES.md) shows how to combine the packages. [Next additions](docs/ROADMAP.md) separates implemented work from proposals.

## How the Texas repository fits

[Texas Longhorns Baseball Intelligence](https://github.com/ahump20/Texas-Longhorns-Baseball-Intelligence) owns the TypeScript library and evidence-collection CLI. This repository owns the installable assistant workflows. The Texas plugin links to that engine; it does not bundle a second copy.

## Verify and contribute

For development, use Node 22.12+ and Python 3.9+:

```bash
npm ci
npm run check
npm run package:plugins
```

The complete check runs typechecking, lint, Node tests, Vitest, Python tests and catalog/package validation. Packaging creates standalone ZIPs under `dist/plugin-packages/`, includes each package's license and manifests, and prints SHA-256 checksums. Identical source produces identical archives.

Optional provider checks are separate from the offline suite:

```bash
SPORTS_LIVE=1 python3 -m unittest discover -s plugins/football/skills/football-analytics/tests
claude plugin validate .
```

See the [project scorecard](docs/PROJECT_SCORECARD.md), [contribution requirements](CONTRIBUTING.md) and [verification record](docs/verification-2026-11-21.md). Passing calculations and package checks do not establish prediction accuracy or a host installation.

## License

[MIT](LICENSE). Third-party data keeps its provider's access and usage terms.
