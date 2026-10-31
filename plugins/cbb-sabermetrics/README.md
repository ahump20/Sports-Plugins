# College Baseball Sabermetrics

Read NCAA baseball observations through BSI and interpret only metrics supported by documented inputs.

Version 0.3.0 includes portable, Claude Code and Codex manifests. The workflows distinguish observations, interpretation and editorial opinion. They do not promise calibrated forecasts, complete rosters, NIL valuations or automatic publication.

## Use

Install from the Sports-Plugins marketplace. Texas intelligence uses the cbb-sabermetrics live connection. The college calculation path additionally uses the baseball plugin's tested Python helper; install that dependency before claiming a calculation ran. Standalone review packages preserve these dependencies explicitly in documentation.

The BSI connection is read-only. Discover available tools before calling them. The October 31, 2026 catalog contained scoreboard, standings, rankings, player statistics, team schedule, match detail and intelligence search. Required tool inputs and result coverage must be checked at runtime. No fixed rate-limit guarantee is made by this package.

## Boundaries

A fresh fetch is not a current season. Missing data remains unavailable. An HTTP success does not establish source truth. No skill in this package independently calibrates a power index, psychological score, championship model or player compensation model. Legacy command names are retained where useful, with corrected descriptive behavior.

Use the optional gameday-ops and editorial-desk plugins for executable game packets and evidence-ledger checks. The companion [Texas analytical library](https://github.com/ahump20/Texas-Longhorns-Baseball-Intelligence) provides an actual HTTP source-packet CLI; it is a separate install, not bundled here.

## Verification

Run repository `npm run check`, `claude plugin validate .`, and the skill-specific tests. The repository verification record documents static evaluation limits and real endpoint observations. Standalone archives include the runtime components, not the full repository evidence archive.

## Claude Code installation

```text
/plugin install cbb-sabermetrics --marketplace ahump20/Sports-Plugins
```
