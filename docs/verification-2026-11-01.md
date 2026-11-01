# Review-cycle verification, November 1, 2026

This follow-up to PR #25 addresses the release review and installation path. The proposed connected Editorial Intelligence Desk is [a separate design awaiting approval](superpowers/specs/2026-11-01-connected-editorial-design.md), not a claim that integration or scheduling is deployed.

## Review corrections

Verified and resolved all 20 CodeRabbit inline findings, plus the SHA-256 and disrupted-status test findings in the review summary. Source URL validation now checks ports and rejects angle brackets; future retrieval always fails freshness; citation IDs are canonical; rendered source/claim text is escaped; CLI output cannot overwrite input via the same path, symlinks or hardlinks. Game packets retain coverage time and clearly distinguish freshness from unavailable coverage. The college agent marks sources it cannot inspect as unverified.

Package validation now requires LICENSE, matching skill/directory identity, a complete portable MCP shape independent of the legacy file, and retained compatibility agreement. Packaging preflights output against every catalog source before writing any archive. Checksum tests recompute ZIP bytes.

Independent review found an additional editorial Markdown-link/image issue and it was fixed with literal-text and exact-quotation regressions. Full evaluator reports retain their findings, with archived command-path redaction and an explanation of the evaluator's version and informational-count defects.

## Verification

The project check runs TypeScript checking, ESLint, Node tests, Vitest, all Python skill suites and catalog/package validation. Native Claude validates the marketplace and each of seven plugin manifests. Standalone ZIP construction and extraction are exercised separately. See [evaluation reports](evaluation/2026-11-01/README.md) and [the fresh dependency audit](verification/dependency-audit-2026-11-01.json).

The candidate set installed all seven packages in a clean Claude configuration. One initial host invocation loaded its skill correctly but its calculator command was denied because it appended an extra shell command outside the narrowly allowed pattern; that was an explicit tool-permission failure, not successful execution. Final merged-release installation, individual invocation and natural-language trigger results belong in the release evidence and must be checked independently of that candidate smoke test.

Fourteen explicit candidate skill invocations and seven natural-language selections completed in Claude; a fresh Codex app-server discovered all fourteen skills in seven packages. Functional probes executed the packaged sport calculators and editorial checker. Initial harness mistakes (a variadic CLI argument boundary, an unapproved remote tool, and a noncanonical game status) were distinguished from plugin defects and corrected for the final probes.

The live Texas model response also made an incorrect comparative ranking despite retrieving the actual source successfully. That is a retained answer-quality failure, not a passing accuracy benchmark. The Texas skill now requires an explicit provider rank or an executed comparison over the relevant rows before stating numerical order. A stronger evidence-to-claim validator remains proposed integration work; prompt instructions alone do not prove the full numerical-accuracy gate. The fifty-request catalog remains unmeasured.

## Dependencies and boundaries

The minimatch override selects a patched version while retaining the declared toolchain. The current full and runtime npm audits report zero advisories. Project checks exercise the override under the existing supported Node contract; remote CI checks the Node 22 environment.

Native validators also emit optional public-directory icon warnings. The remote NCAA plugin emits a privacy-policy directory warning in the Claude validator. Those listing warnings do not prevent local validation/install, and no public-directory approval is claimed. Fresh retrieval does not certify current-season coverage. There is no BSI web/iOS deployment, account-plugin publication, automatic article publication, or recurring game-day schedule in this change.
