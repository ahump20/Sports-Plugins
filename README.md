# Sports-Plugins

Sports plugins for Claude Code and Codex: baseball, football, basketball, game-day packets and editorial evidence. Core analytics scripts are checked against published examples; new workflow helpers use explicitly synthetic edge-case fixtures. Neither static checks nor source attribution establish predictive accuracy.

```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install baseball@Sports-Plugins
```

| Plugin | Skills | Checked against |
|---|---|---|
| [baseball](plugins/baseball/) | rules, analytics, data | Ohtani 2024 wOBA .431, Skubal 2024 FIP 2.49 (FanGraphs) |
| [football](plugins/football/) | rules, analytics, data, NFL and college | nflverse player stats to three decimals; Texas 2024 EPA (sportsdataverse game boxes); Ewers 2024 NCAA efficiency 148.98 |
| [basketball](plugins/basketball/) | rules, analytics, data | Curry 2015-16 TS% .669; Warriors ratings 114.5 / 103.8 (Basketball-Reference) |
| [cbb-sabermetrics](plugins/cbb-sabermetrics/) | live NCAA DI baseball via the Blaze Sports Intel MCP | |
| [texas-longhorns-intel](plugins/texas-longhorns-intel/) | Texas baseball, built on cbb-sabermetrics | |
| [gameday-ops](plugins/gameday-ops/) | executable game packets, final/live/status handling, source freshness | synthetic edge cases and command-line tests |
| [editorial-desk](plugins/editorial-desk/) | evidence ledgers, exact excerpt matching, arithmetic and citation completeness | synthetic edge cases and command-line tests |

The three foundational sport plugins each have three skills:

- **rules**: rulings by level (pro, college, international), with rule numbers and the season each rule took effect.
- **analytics**: a standard-library Python script that computes the metrics, plus what each metric means and when it misleads.
- **data**: free sources that work today, with exact URLs, field names and the traps in each.

The bundled local helpers need no API keys or paid services. External source availability is not guaranteed. The scripts need Python 3.9+.

## Tests

```bash
npm run test:py
SPORTS_LIVE=1 python3 -m unittest discover -s plugins/football/skills/football-analytics/tests   # downloads real data
claude plugin validate .
```

CI runs the offline tests on every pull request and the live ones weekly.

## Plugin Structure

Every plugin follows the standard [Claude Code plugin structure](https://github.com/anthropics/claude-plugins-official):

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── skills/              # Skill definitions (preferred)
│   ├── skill-name/
│   │   └── SKILL.md     # Model-invoked skill
│   └── command-name/
│       └── SKILL.md     # User-invoked slash command
└── README.md            # Documentation (required)
```

### Codex

Each listed plugin also has a `.codex-plugin/plugin.json`, plus a portable root `plugin.json`. Codex has a native `.agents/plugins/marketplace.json`; Claude keeps `.claude-plugin/marketplace.json`. The catalog validator checks that both list the same seven packages. Existing host-specific manifests remain available:


```bash
codex plugin marketplace add ahump20/Sports-Plugins
```

Use the desktop Plugins Directory to install from the added marketplace and test in a fresh conversation. Host installation was not performed by this repository upgrade.

## Validation

```bash
node scripts/validate-plugins.mjs
```

## Shared Library (`/lib`)

The `lib/` directory contains portable TypeScript modules used across plugins:

| Module | Description |
|--------|-------------|
| **[sabermetrics.ts](lib/sabermetrics.ts)** | Pure-function sabermetric calculations — wOBA, FIP, wRC+, BABIP, ISO, xFIP, CSW%, and more with legacy illustrative default weights (not NCAA-calibrated) |
| **[scores-client.ts](lib/scores-client.ts)** | ESPN public API client — fetches live scoreboards, normalises response data into typed `GameScore` objects |
| **[types.ts](lib/types.ts)** | Shared TypeScript interfaces — `BattingLine`, `PitchingLine`, `GameScore`, `Player`, `TeamStanding`, etc. |

### Sabermetrics Library

The legacy defaults in `lib/sabermetrics.ts` are not empirically calibrated NCAA constants. Do not present outputs using these defaults as official or season-adjusted metrics. The supported college calculation workflow is the baseball plugin's tested `saber.py` with the requested season's published league totals.

```ts
import { wOBA, fip, computeBattingAdvanced } from "./lib/sabermetrics.ts";

const advanced = computeBattingAdvanced(battingLine, parkFactor);
console.log(advanced.wOBA, advanced.wRCPlus, advanced.babip);
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting new sports plugins.

## Related Projects

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — The official Claude Code plugins directory
- [ahump20/BSI](https://github.com/ahump20/BSI) — Blaze Sports Intel — the sports platform powering the BSI external plugin
- [OpenAI Codex Use Cases](https://developers.openai.com/codex/use-cases) — Codex agent patterns for tool use

## License

[MIT](LICENSE)

## Release verification

See [the upgrade evidence and limitations](docs/verification-2026-10-31.md). Standalone workflow plugins require local Python execution and supplied observations; they do not fetch or publish by themselves. The Texas engine companion now discovers the deployed MCP tools and preserves raw response provenance. A fresh API response may still lack season coverage metadata.

## Build standalone plugin archives

```bash
npm run package:plugins
# Or select a plugin and an output directory outside its source folder:
python3 scripts/package-plugins.py --plugin gameday-ops --output ./dist/plugin-packages
```

Each ZIP contains one plugin at its root, including hidden compatibility manifests and its MIT notice. Archives omit caches and marketplace wrappers. Identical input produces identical archive bytes; the command prints SHA-256 checksums. These are local review/install packages, not a claim of public-directory approval.
