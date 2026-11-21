# Sports Plugins project scorecard

## Definition of done

A plugin helps someone finish a specific sports task, produces inspectable output from real inputs, and remains usable after standalone extraction. The catalog describes implemented behavior. Keep prose direct and tables readable; do not add decorative labels or badges that imply validation not performed.

| Check | Exact verification | Required evidence |
|---|---|---|
| Existing behavior stays green | `npm ci && npm run check` on Node 22.12+; Python 3.9+ available | Full log, commit/tree and environment versions |
| Both hosts discover the same packages | `node --test tests/package-contract.test.mjs`; `npm run validate` | Identical package names and valid manifest/component paths |
| Roster differences respect identity and coverage | `python3 -m unittest discover -s plugins/roster-watch/skills/roster-diff/tests -v` | Hand-verifiable changes, duplicate identity rejection, partial coverage, temporal and scope tests |
| Playoff results follow declared rules | `python3 -m unittest discover -s plugins/playoff-lab/skills/playoff-scenarios/tests -v` | Hand-counted scenarios, unresolved cutoff ties, constraints, rejected unsupported settings and enumeration cap |
| Packages work outside the checkout | `npm run package:plugins`; extract each changed ZIP into a fresh directory and run its README example | Archive hash, exact command, successful JSON and Markdown output; no sibling dependency |
| Output is legible and truthful | Inspect the actual Markdown and JSON examples from the changed package | Clear headers/units, sources and assumptions; synthetic examples labeled; unknowns visible |
| CLI behavior is usable | Run `--help`, valid input, malformed input and an input/output path collision | Help text, documented exit code, useful error, input preserved |
| Host compatibility | `claude plugin validate .`; isolated host install and invoke using recorded host/version when available | Distinguish schema validation, installation, skill discovery and actual invocation |
| Live provider behavior | Run only the relevant provider smoke, record date/endpoint/status/coverage | Successful response or concrete failure; no claims beyond observed fields |
| Runtime stays bounded | Exercise the maximum supported Playoff Lab unforced-game count; roster-size cap if provided by its contract | Completion/resource bound or explicit validation rejection; never silent sampling |

The project is a CLI/assistant package collection, so keyboard-operable text output and readable tables are the relevant accessibility surface. There is no web page, game frame or mobile layout in this change. Any future UI needs its own viewed reference frames and accessibility checks.

## Reference locations

- [Roster example inputs](../plugins/roster-watch/skills/roster-diff/examples/): define a reproducible diff, not a current roster.
- [Playoff example input](../plugins/playoff-lab/skills/playoff-scenarios/examples/league.json): defines a reproducible league scenario, not Austin's live league.
- [Existing sport fixtures](../plugins/): source-attributed calculation checks under each analytics skill's `tests/`.
- [Package contract tests](../tests/package-contract.test.mjs): portable and host manifest requirements.
- [Latest verification](verification-2026-11-21.md): actual commands and outcomes for this revision.
- Intended prose style: the root workflow table and each plugin's exact example. No graphical reference frame is applicable to these local tools.

## Release gate

**Pass:** all required offline checks pass, changed archives execute independently, documentation describes the same behavior, and the exact reviewed tree is identified.

**Blocked:** a calculation is wrong, identity or season scope is ambiguous, required settings are missing, catalog/package validation fails, source files can be overwritten accidentally, or a promised runtime path cannot execute.

**Accepted debt:** a provider outage or unavailable host smoke may be documented without blocking a clearly labeled offline package, provided no claim of live access or host invocation is made. Legacy illustrative metric defaults must remain explicitly labeled.

**Exception:** record the affected check, rationale, evidence, scope, owner and revisit condition in the verification note. An exception cannot relabel fabricated data, a failed calculation or an untested capability as passed.

A passing source PR does not publish a release or install an account plugin. Releases use reviewed commits and explicit tagged-release workflow.
