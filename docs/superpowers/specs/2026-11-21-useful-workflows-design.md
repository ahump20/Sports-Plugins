# Useful sports workflows

## Purpose

Make the marketplace easy to understand and add two workflows that answer recurring sports questions with inspectable calculations. Preserve the seven existing packages and their tested behavior. This design records implementation choices made for Austin's request to update both repositories and create useful plugins; it does not imply a separate design approval or a release.

## Approaches considered

1. Add more general sports prompts. Low setup cost, but overlaps with the existing seven plugins and offers little new capability.
2. Build a hosted data platform first. Enables saved history and background refresh, but introduces provider authentication, operations and recurring costs before the workflow is proven.
3. Add deterministic local workflows over supplied, attributed snapshots. Chosen for this implementation: immediate use, no new runtime dependencies, reproducible outputs and explicit data limitations. Existing authorized connectors can supply inputs later.

## Roster Watch

Compare two snapshots for the same sport, team, season and identity namespace. Each snapshot supplies an observed-at timestamp, source URL, completeness declaration and a roster of stable player identifiers. Report added, absent and changed records, retaining both source references and the exact compared fields. An absence is an observation, never evidence of a transfer, injury, eligibility decision or departure. Partial snapshots cannot establish absence. Reject duplicate identifiers, different scopes, reversed timestamps and malformed inputs. Never join by name alone. Produce JSON and readable Markdown from one deterministic calculation.

## Playoff Lab

Enumerate remaining head-to-head win/loss outcomes for a single overall standings table. Inputs explicitly declare playoff slots, complete remaining schedule, ties policy and tiebreak treatment. Support record percentage (ties count as half a win), with either unresolved equal records or an explicit fixed tiebreak order representing the user's scenario assumption. Do not infer Yahoo settings, future points for, division qualification, head-to-head tiebreakers, median games or consolation rules. Reject unsupported settings rather than approximate them. Limit enumeration to 16 unforced games. Return seed ranges, guaranteed/possible qualification counts and clinched/eliminated/alive states conditional on supplied assumptions. Unweighted outcome counts or fractions are scenario shares, not forecast probabilities. Allow explicitly forcing known or hypothetical game winners. Preserve source and as-of metadata.

## Packaging and verification

- Python 3.9+ standard library only for new workflows; follow existing portable, Claude and Codex manifests.
- Each plugin includes its MIT notice, a concise skill, input contract, synthetic labeled examples, executable CLI and meaningful tests.
- Use the existing Skill Creator initializer and validator for bundled skills; source belongs in this Git-managed plugin repo, not the personal-skills installation checkout.
- Preserve all existing catalog entries and add both plugins to both catalogs.
- Run failing behavior tests before implementation, then the new suites, full repository checks, archive creation and extracted-package smoke tests.
- Test identity ambiguity, incomplete snapshots, temporal ordering, unresolved ties, inconsistent schedules and malformed numeric values.
- No hosting, subscriptions, database migrations, league transactions or automatic monitoring are part of this implementation.

## Documentation

Lead READMEs with jobs users can do, required inputs and actual output. Separate bundled offline calculations from live provider-dependent workflows and ideas not yet built. Replace stale About and package descriptions. Consolidate contribution requirements so synthetic fixtures are permitted as tests and examples but cannot be passed off as real observations. Document an explicit project scorecard and next opportunities with acceptance criteria.

The companion Texas repository remains the TypeScript evidence engine; its README and workflow documentation explain how it relates to the marketplace. Keep historical reference caveats and public MCP limitations visible without burying the useful starting commands.
