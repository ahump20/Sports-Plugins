# Sports-Plugins

Claude Code plugins for baseball, football and basketball. Every number a skill produces comes from a script with tests that check it against a published source.

```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install baseball@Sports-Plugins
```

| Plugin | Skills | Checked against |
|---|---|---|
| [baseball](plugins/baseball/) | rules, analytics, data | Ohtani 2024 wOBA .431, Skubal 2024 FIP 2.49 (FanGraphs) |
| [football](plugins/football/) | rules, analytics, data | nflverse player stats to three decimals; passer rating 122.5 (Rodgers 2011) |
| [basketball](plugins/basketball/) | rules, analytics, data | Curry 2015-16 TS% .669; Warriors ratings 114.5 / 103.8 (Basketball-Reference) |
| [cbb-sabermetrics](plugins/cbb-sabermetrics/) | live NCAA DI baseball via the Blaze Sports Intel MCP | |
| [texas-longhorns-intel](plugins/texas-longhorns-intel/) | Texas baseball, built on cbb-sabermetrics | |

Each sport has three skills:

- **rules**: rulings by level (pro, college, international), with rule numbers and the season each rule took effect.
- **analytics**: a standard-library Python script that computes the metrics, plus what each metric means and when it misleads.
- **data**: free sources that work today, with exact URLs, field names and the traps in each.

No API keys and no paid services. The scripts need Python 3.9+.

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

Each listed plugin also has a `.codex-plugin/plugin.json`, and Codex reads this repo's marketplace file:

```bash
codex plugin marketplace add ahump20/Sports-Plugins
codex plugin add baseball@Sports-Plugins
```

## Validation

```bash
node scripts/validate-plugins.mjs
```

## Shared Library (`/lib`)

The `lib/` directory contains portable TypeScript modules used across plugins:

| Module | Description |
|--------|-------------|
| **[sabermetrics.ts](lib/sabermetrics.ts)** | Pure-function sabermetric calculations — wOBA, FIP, wRC+, BABIP, ISO, xFIP, CSW%, and more with NCAA-calibrated linear weights |
| **[scores-client.ts](lib/scores-client.ts)** | ESPN public API client — fetches live scoreboards, normalises response data into typed `GameScore` objects |
| **[types.ts](lib/types.ts)** | Shared TypeScript interfaces — `BattingLine`, `PitchingLine`, `GameScore`, `Player`, `TeamStanding`, etc. |

### Sabermetrics Library

The formulas in `lib/sabermetrics.ts` are calibrated for NCAA Division I college baseball (BBCOR bats, smaller samples). They can also be used for MLB data by adjusting the linear-weight constants.

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
