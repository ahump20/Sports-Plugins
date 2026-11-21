# Playoff Lab

Find each team's best and worst seed, identify who has clinched and test what changes if a rival wins. Supply a league snapshot with attributed standings, all remaining regular-season matchups and the rules for one overall playoff race.

Run the synthetic Harbor League example from this plugin directory with Python 3.9 or newer.

```bash
python3 skills/playoff-scenarios/scripts/playoff_scenarios.py --input skills/playoff-scenarios/examples/league.json --format markdown
python3 skills/playoff-scenarios/scripts/playoff_scenarios.py --input skills/playoff-scenarios/examples/league.json --winner harbor=anchors --format json
```

In the example there are two playoff places and four combinations of game winners. The Anchors qualify outright in three and can qualify in all four. If both the Breakers and the Cutters win, three teams finish 2–1. The Anchors can fall to third under the unresolved tiebreak. Forcing an Anchors win removes that outcome and clinches their place in both remaining scenarios.

The calculator runs locally using the Python standard library. It enumerates up to 16 unforced games, ranks by exact win percentage and preserves equal-record seed ranges unless you declare a fixed tiebreak order. Past ties count as half a win. Future matchups have a winner in every scenario. A league's divisions, median games or head-to-head tiebreak rules require a different model. Outcome counts describe schedules and carry no forecast weighting.

Use the [input contract](skills/playoff-scenarios/references/input-contract.md) to build a snapshot from your own league. See the [skill workflow](skills/playoff-scenarios/SKILL.md) for interpreting a result. Add `--output report.md` to save a report. Run `python3 -m unittest discover -s skills/playoff-scenarios/tests -v` to verify the calculator.

## Claude Code installation

```text
/plugin install playoff-lab --marketplace ahump20/Sports-Plugins
```
