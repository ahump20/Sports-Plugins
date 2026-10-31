import copy, importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from datetime import datetime, timezone

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/game_packet.py"
NOW = datetime(2026, 10, 31, 12, tzinfo=timezone.utc)


def fixture():
    return {
        "source": {
            "url": "https://example.org/scoreboard",
            "provider": "synthetic-test-fixture",
            "fetched_at": "2026-10-31T11:00:00Z",
        },
        "games": [
            {
                "id": "g1",
                "status": "final",
                "home": {"name": "Home Fixture", "score": 5},
                "away": {"name": "Away Fixture", "score": 2},
            }
        ],
    }


class GamePacketTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "Executable game-packet helper is required")
        spec = importlib.util.spec_from_file_location("game_packet", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_final_score_margin_and_winner(self):
        packet = self.module.build_packet(fixture(), now=NOW)
        self.assertEqual(packet["games"][0]["winner"], "Home Fixture")
        self.assertEqual(packet["games"][0]["margin"], 3)
        self.assertIn("coverage", " ".join(packet["warnings"]).lower())

    def test_tied_final_is_not_a_home_win(self):
        data = fixture()
        data["games"][0]["away"]["score"] = 5
        self.assertIsNone(self.module.build_packet(data, now=NOW)["games"][0]["winner"])

    def test_live_leader_is_not_final_winner(self):
        data = fixture()
        data["games"][0]["status"] = "in_progress"
        game = self.module.build_packet(data, now=NOW)["games"][0]
        self.assertIsNone(game["winner"])
        self.assertEqual(game["leader"], "Home Fixture")

    def test_scheduled_missing_scores_remain_missing(self):
        data = fixture()
        data["games"][0]["status"] = "scheduled"
        data["games"][0]["home"]["score"] = None
        data["games"][0]["away"]["score"] = None
        packet = self.module.build_packet(data, now=NOW)
        self.assertIsNone(packet["games"][0]["home"]["score"])
        self.assertNotIn("0-0", self.module.render_markdown(packet))

    def test_postponed_and_suspended_are_not_final(self):
        for status in ["postponed", "cancelled", "suspended"]:
            data = fixture()
            data["games"][0]["status"] = status
            self.assertIsNone(
                self.module.build_packet(data, now=NOW)["games"][0]["winner"]
            )

    def test_rejects_invalid_scores(self):
        for score in [-1, True, 1.5, "3", float("nan"), None]:
            data = fixture()
            data["games"][0]["home"]["score"] = score
            with self.assertRaises(ValueError):
                self.module.build_packet(data, now=NOW)

    def test_rejects_duplicate_ids_unknown_status_and_bad_provenance(self):
        data = fixture()
        data["games"].append(copy.deepcopy(data["games"][0]))
        with self.assertRaises(ValueError):
            self.module.build_packet(data, now=NOW)
        for change in [
            {"url": "javascript:alert(1)"},
            {"fetched_at": "yesterday"},
            {"provider": " "},
        ]:
            data = fixture()
            data["source"].update(change)
            with self.assertRaises(ValueError):
                self.module.build_packet(data, now=NOW)
        data = fixture()
        data["games"][0]["status"] = "probably-final"
        with self.assertRaises(ValueError):
            self.module.build_packet(data, now=NOW)

    def test_stale_and_future_fetches_are_flagged(self):
        for stamp in ["2025-01-01T00:00:00Z", "2027-01-01T00:00:00Z"]:
            data = fixture()
            data["source"]["fetched_at"] = stamp
            self.assertNotEqual(
                self.module.build_packet(data, now=NOW)["freshness"], "fresh"
            )

    def test_empty_scoreboard_is_explicit_not_error(self):
        data = fixture()
        data["games"] = []
        self.assertIn(
            "No games",
            self.module.render_markdown(self.module.build_packet(data, now=NOW)),
        )

    def test_cli_json_and_invalid_input_exit_codes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            path.write_text(json.dumps(fixture()))
            run = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(path),
                    "--format",
                    "json",
                    "--now",
                    NOW.isoformat(),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["games"][0]["margin"], 3)
            path.write_text("{}")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(path)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
