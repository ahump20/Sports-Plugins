# Sports workflows

## Check a story before filing

Use **Editorial Desk** with the actual manuscript claims, supplied source excerpts and a cutoff time. Its ledger checks attribution, quote/excerpt matches, freshness and arithmetic. Read its unresolved items before writing final copy. A passed excerpt match does not authenticate a quotation; source review is still required.

Example request: “Check these claims and quotations. Show the source, coverage date, calculation and unresolved issue for each. Keep my argument and voice.”

Do not add a second editorial plugin for the same work. A future manuscript adapter should feed this existing ledger.

## Prepare a game-day packet

Use **Gameday Ops** to normalize supplied game observations into a sourced packet. Preserve scheduled, live, final, postponed and unavailable states. Read a game's status before describing a score as a result.

Use the sport-specific analytics plugin only when the packet contains the counting stats or play-by-play the calculation requires. The packet builder does not fetch a full box score by itself.

## Track a roster page

Use **Roster Watch** with two dated snapshots. Confirm team, sport, season and identity namespace before comparing them. Use the official source's identifiers only when their stability is established within that scope.

Report “not listed in the later snapshot” rather than an inferred reason for the change. If a capture is partial, preserve the uncertainty. Player page IDs that change between seasons require a separately reviewed identity map; the current comparator rejects cross-season comparisons.

See the [roster input contract](../plugins/roster-watch/skills/roster-diff/references/input-contract.md) and the plugin's example command.

## Work through a playoff race

Use **Playoff Lab** with the league's current records and full remaining regular-season schedule. Check its actual seeding rules against the supported overall-table format before calculating. Head-to-head and points-based tiebreak rules are not implemented, so the calculator cannot report exact league outcomes under those policies. Offer unresolved ranges or a declared fixed order only as an explicitly hypothetical comparison; never label those results the league's actual clinch or elimination status.

Compare an unconstrained run with a declared outcome such as your team winning its next game. The change in possible seeds explains the consequence of that result. Outcome fractions do not become forecast odds without a separate calibrated probability model.

The plugin consumes normalized snapshots. It does not sign in to Yahoo, make lineup changes or assume a provider's default settings.

## Prepare Texas baseball research

Use **Texas Longhorns Intel** with **CBB Sabermetrics** for assistant-guided research, or run the companion [Texas evidence CLI](https://github.com/ahump20/Texas-Longhorns-Baseball-Intelligence) for a repeatable source packet.

1. Establish the requested season and reporting cutoff.
2. Discover the actual MCP tools and retain their responses.
3. Resolve Texas to an exact team identity.
4. Check the season and statistical coverage for standings, schedule and rankings separately.
5. Use official roster pages, game notes and box scores to fill the specific gaps the packet identifies.
6. Separate observations, supported interpretation and editorial recommendation.

Do not convert a missing conference record into zeros, apply an uncalibrated conference multiplier, or manufacture player metrics. The [roadmap](ROADMAP.md) defines a future Series Desk extension; it is not an existing automated series-preview command.

## Read or build with the shared library

The [lib](../lib/) modules provide TypeScript calculations, typed score objects and an ESPN scoreboard client. Keep endpoint availability separate from parsing correctness. The legacy sabermetric defaults are illustrative; explicit season constants are required for meaningful cross-team comparisons.

These workflows provide inspectable evidence for a human or assistant to use. They do not publish articles, update a website or create background jobs automatically.
