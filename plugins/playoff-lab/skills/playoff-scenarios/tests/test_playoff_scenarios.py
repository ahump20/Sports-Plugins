"""All leagues in this file are synthetic, hand-enumerated fixtures."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "playoff_scenarios.py"
sys.path.insert(0, str(SCRIPT.parent))


def snapshot(records=((2, 0, 0), (1, 1, 0), (1, 1, 0), (0, 2, 0)),
             games=((3, "A", "B"), (3, "C", "D")), completed=2, weeks=3):
    teams = []
    for team_id, (wins, losses, ties) in zip("ABCDE", records):
        remaining = sum(team_id in (a, b) for _, a, b in games)
        teams.append(dict(id=team_id, name="Team " + team_id, wins=wins,
                          losses=losses, ties=ties, season_games=wins+losses+ties+remaining))
    return {
        "league": "SYNTHETIC League", "season": "2026", "source": "SYNTHETIC test",
        "as_of": "2026-11-01T12:00:00Z", "completed_week": completed, "regular_season_weeks": weeks,
        "remaining_schedule_complete": True,
        "settings": {"playoff_slots": 2, "standings": "overall", "ranking": "win_percentage",
                     "existing_ties": "half_win", "future_ties": "excluded",
                     "median_games": False, "tiebreak": {"mode": "unresolved"}},
        "teams": teams, "remaining_games": [
            {"id": "g" + str(i), "week": w, "home": a, "away": b}
            for i, (w, a, b) in enumerate(games, 1)
        ],
    }


def analyze(data, winners=()):
    from playoff_scenarios import analyze_scenarios
    return analyze_scenarios(data, winners)


def standings(report):
    return {t["id"]: (t["best_seed"], t["worst_seed"], t["guaranteed_qualifications"],
                      t["possible_qualifications"], t["status"]) for t in report["teams"]}


class TestScenarios(unittest.TestCase):
    def test_four_outcomes_with_cutoff_ties(self):
        data = snapshot()
        original = copy.deepcopy(data)
        report = analyze(data)
        self.assertEqual(report["scenarios"], 4)
        self.assertEqual(standings(report), {
            "A": (1, 3, 3, 4, "alive"), "B": (1, 4, 1, 3, "alive"),
            "C": (1, 4, 1, 3, "alive"), "D": (2, 4, 0, 1, "alive")})
        self.assertEqual(report["source"], data["source"])
        self.assertEqual(report["as_of"], data["as_of"])
        self.assertEqual(original, data)
        self.assertEqual(report, analyze(original))

    def test_completed_season_percentages_with_byes_and_past_ties(self):
        report = analyze(snapshot(((1, 0, 1), (2, 1, 0), (0, 1, 1), (1, 2, 0)),
                                  games=(), completed=3))
        self.assertEqual(report["scenarios"], 1)
        self.assertEqual(standings(report), {
            "A": (1, 1, 1, 1, "clinched"), "B": (2, 2, 1, 1, "clinched"),
            "C": (4, 4, 0, 0, "eliminated"), "D": (3, 3, 0, 0, "eliminated")})

    def test_complete_tiebreak_order_can_change_who_qualifies(self):
        data = snapshot()
        data["settings"]["tiebreak"] = {"mode": "fixed_order", "order": list("DCBA")}
        report = analyze(data)
        self.assertEqual({i: (v[2], v[3]) for i, v in standings(report).items()},
                         {"A": (3, 3), "B": (2, 2), "C": (2, 2), "D": (1, 1)})
        self.assertEqual(report["settings"]["tiebreak"], data["settings"]["tiebreak"])

    def test_report_retains_the_policy_used_to_compute_its_counts(self):
        from playoff_scenarios import render_markdown
        data = snapshot()
        first = analyze(data)
        first_text = render_markdown(first)
        data["settings"]["tiebreak"] = {"mode": "fixed_order", "order": list("DCBA")}
        second = analyze(data)
        data["settings"]["tiebreak"]["order"].reverse()
        self.assertEqual(first["settings"]["tiebreak"], {"mode": "unresolved"})
        self.assertEqual(render_markdown(first), first_text)
        self.assertEqual(standings(first)["A"][2:4], (3, 4))
        self.assertEqual(second["settings"]["tiebreak"]["order"], list("DCBA"))
        self.assertIn("D, C, B, A", render_markdown(second))
        self.assertEqual(standings(second)["A"][2:4], (3, 3))

    def test_conditioning_on_two_winners_is_one_outcome(self):
        report = analyze(snapshot(), [("g1", "A"), ("g2", "C")])
        self.assertEqual(report["scenarios"], 1)
        self.assertEqual(standings(report), {
            "A": (1, 1, 1, 1, "clinched"), "C": (2, 2, 1, 1, "clinched"),
            "B": (3, 3, 0, 0, "eliminated"), "D": (4, 4, 0, 0, "eliminated")})

    def test_bad_winner_constraints(self):
        for winners in [[("x", "A")], [("g1", "C")], [("g1", "A"), ("g1", "B")]]:
            with self.subTest(winners=winners), self.assertRaises(ValueError):
                analyze(snapshot(), winners)

    def test_rejects_bad_policy_records_scope_and_schedule(self):
        cases = [
            (("settings", "ranking"), "wins"), (("settings", "standings"), "divisions"),
            (("settings", "median_games"), 0), (("settings", "future_ties"), "allowed"),
            (("settings", "division_winners"), 1), (("settings", "existing_ties"), "ignored"),
            (("settings", "playoff_slots"), True), (("settings", "playoff_slots"), 5),
            (("settings", "tiebreak"), {"mode": "head_to_head"}),
            (("settings", "tiebreak"), {"mode": "fixed_order", "order": list("ABAA")}),
            (("settings", "tiebreak"), {"mode": "unresolved", "order": list("ABCD")}),
            (("teams", 0, "wins"), True), (("teams", 1, "wins"), 1.0),
            (("teams", 3, "losses"), -1), (("teams", 0, "id"), "B"),
            (("teams", 0, "season_games"), 2), (("teams", 0, "name"), ""),
            (("remaining_games", 0, "home"), "B"), (("remaining_games", 0, "away"), "Z"),
            (("remaining_games", 1, "home"), "A"), (("remaining_games", 1, "id"), "g1"),
            (("remaining_games", 0, "week"), 2), (("remaining_games", 0, "week"), 4),
            (("remaining_schedule_complete",), False), (("remaining_games",), []),
            (("source",), ""), (("as_of",), "2026-11-01"), (("season",), " "),
            (("completed_week",), 1), (("playoff_games",), []),
        ]
        for path, new in cases:
            data = snapshot()
            target = data
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = new
            with self.subTest(path=path, new=new), self.assertRaises(ValueError):
                analyze(data)

    def test_rejects_unbalanced_historical_records(self):
        for new_losses, new_ties in [(0, 1), (0, 0)]:
            data = snapshot()
            data["teams"][1].update(losses=new_losses, ties=new_ties, season_games=2+new_ties)
            with self.subTest(ties=new_ties), self.assertRaises(ValueError):
                analyze(data)

    def test_idle_teams_cannot_inflate_weekly_capacity(self):
        records = ((1, 1, 0), (1, 1, 0), (1, 1, 0), (0, 0, 0))
        with self.assertRaises(ValueError):
            analyze(snapshot(records, ((3, "A", "D"),)), [("g1", "D")])
        # A, B and C can complete their three head-to-head games in three weeks.
        valid = snapshot(records, ((4, "A", "D"),), completed=3, weeks=4)
        self.assertEqual(analyze(valid)["scenarios"], 2)

    def test_decisive_and_tied_games_each_need_eligible_participants(self):
        cases = [
            ((1, 1, 0), (1, 1, 0), (1, 1, 0), (0, 0, 1), (0, 0, 1)),
            ((0, 0, 2), (0, 0, 2), (0, 0, 2), (1, 0, 0), (0, 1, 0)),
        ]
        for records in cases:
            with self.subTest(records=records), self.assertRaises(ValueError):
                analyze(snapshot(records, (), completed=2, weeks=2))

    def test_part_time_opponents_cannot_absorb_all_unpaired_games(self):
        # Three teams played every week. Their two other opponents have just two
        # appearances between them, leaving at least five internal games in four weeks.
        records = ((2, 2, 0), (2, 2, 0), (2, 2, 0), (1, 0, 0), (0, 1, 0))
        with self.assertRaises(ValueError):
            analyze(snapshot(records, (), completed=4, weeks=4))

    def test_limit_applies_after_forcing_winners(self):
        games = [(week, "A", "B") for week in range(1, 18)]
        data = snapshot(((0, 0, 0), (0, 0, 0)), games=games, completed=0, weeks=17)
        data["settings"]["playoff_slots"] = 1
        with self.assertRaisesRegex(ValueError, "16"):
            analyze(data)
        winners = [(g["id"], "A") for g in data["remaining_games"][:1]]
        report = analyze(data, winners)
        self.assertEqual(report["scenarios"], 65536)
        self.assertEqual(standings(report)["A"][2:4], (39203, 39203))


class TestCLI(unittest.TestCase):
    def run_cli(self, source, *flags):
        return subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), *map(str, flags)],
                              capture_output=True, text=True, check=False)

    def test_invalid_json_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "snapshot.json"
            output = Path(directory) / "report.md"
            output.write_text("prior report")
            cases = [('{"league":1,"league":2}', "duplicate JSON field"),
                     ('{"bad":NaN}', "invalid JSON number"), ('{"bad":Infinity}', "invalid JSON number"),
                     ('[', "Expecting value"), ('{}', "missing field")]
            for bad, reason in cases:
                source.write_text(bad)
                result = self.run_cli(source, "--output", output)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn(reason, result.stderr)
                self.assertEqual(output.read_text(), "prior report")

    def test_rejects_input_as_output_including_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.json"
            original = json.dumps(snapshot())
            source.write_text(original)
            symlink = Path(directory) / "symlink"
            symlink.symlink_to(source)
            hardlink = Path(directory) / "hardlink"
            os.link(source, hardlink)
            for out in [source, symlink, hardlink]:
                result = self.run_cli(source, "--output", out)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(source.read_text(), original)

    def test_cli_json_markdown_and_force(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "in.json"
            source.write_text(json.dumps(snapshot()))
            output = Path(directory) / "result.json"
            result = self.run_cli(source, "--winner", "g1=A", "--format", "json", "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())["scenarios"], 2)
            md = self.run_cli(source, "--format", "markdown")
            self.assertEqual(md.returncode, 0, md.stderr)
            for field in ["SYNTHETIC test", "2026-11-01T12:00:00Z", "Team A", "3/4", "4/4",
                          "unresolved", "declared", "win percentage"]:
                self.assertIn(field, md.stdout)
