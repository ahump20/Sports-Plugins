---
name: texas-scout
description: Prepare a source-attributed Texas baseball scouting brief, with explicit limits on missing roster, player and advanced-metric inputs.
arguments:
  - name: focus
    description: Optional offense, pitching, draft or nil research focus
    required: false
---

# /texas-scout

Load `texas-longhorns-baseball-intelligence`. Read Texas standings and schedule, then resolve player names from supplied identities or an official roster before requesting individual statistics. Do not call a searched subset a complete roster.

Use the `interpreting-advanced-metrics` calculation path only with required inputs and league totals. Report observed offense/pitching, sample sizes, missing inputs, supported comparisons and a labeled scouting opinion. Do not generate composite scores or infer health from workload.

`focus=offense` or `focus=pitching` narrows the observed metrics. `focus=draft` requires dated expert reporting or official draft records; no unsourced projected rounds. `focus=nil` is public-source research only; without verified compensation and a documented method, quantitative return or player-value judgments are unavailable.

End with the key unresolved question and sources. Preserve the user's requested format and voice. No publication or recurring monitoring is performed.
