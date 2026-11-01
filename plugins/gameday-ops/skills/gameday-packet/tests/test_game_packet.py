import copy, importlib.util, json, os, subprocess, sys, tempfile, unittest
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
            with self.subTest(status=status):
                data = fixture()
                data["games"][0]["status"] = status
                game = self.module.build_packet(data, now=NOW)["games"][0]
                self.assertIsNone(game["winner"])
                self.assertIsNone(game["leader"])
                self.assertIsNone(game["margin"])

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

    def test_source_urls_reject_malformed_and_out_of_range_ports(self):
        for port in ["notaport", "65536", "-1", "443.0"]:
            with self.subTest(port=port):
                data = fixture()
                data["source"]["url"] = "https://scores.example:" + port + "/game"
                with self.assertRaises(ValueError):
                    self.module.build_packet(data, now=NOW)

    def test_source_urls_accept_valid_ports_and_ipv6(self):
        for url in ["https://scores.example:443/game", "https://[2001:db8::1]:8443/game"]:
            with self.subTest(url=url):
                data = fixture()
                data["source"]["url"] = url
                packet = self.module.build_packet(data, now=NOW)
                self.assertEqual(packet["source"]["url"], url)

    def test_source_urls_reject_angle_brackets_before_markdown_rendering(self):
        for url in [
            "https://scores.example/<script>alert(1)</script>",
            "https://scores.example/game><b>Other</b>",
        ]:
            with self.subTest(url=url):
                data = fixture()
                data["source"]["url"] = url
                with self.assertRaises(ValueError):
                    self.module.build_packet(data, now=NOW)

    def test_any_future_fetch_is_flagged(self):
        for fetched_at in [
            "2026-10-31T12:00:00.000001Z",
            "2026-10-31T12:00:01Z",
            "2026-10-31T12:01:00Z",
        ]:
            with self.subTest(fetched_at=fetched_at):
                data = fixture()
                data["source"]["fetched_at"] = fetched_at
                packet = self.module.build_packet(data, now=NOW)
                self.assertEqual(packet["freshness"], "future")
                self.assertIn("future", packet["warnings"][0])

    def test_fetch_at_now_is_fresh(self):
        data = fixture()
        data["source"]["fetched_at"] = "2026-10-31T12:00:00Z"
        self.assertEqual(self.module.build_packet(data, now=NOW)["freshness"], "fresh")

    def test_markdown_keeps_names_literal_in_provider_teams_and_result(self):
        data = fixture()
        data["source"]["provider"] = "[Provider](https://unrelated.example) *bold* _em_ `code` \\ trail | line\nbreak"
        data["games"][0]["home"]["name"] = "[Home](https://unrelated.example)"
        data["games"][0]["away"]["name"] = "Away *stars* _under_ `ticks` \\ slash"
        markdown = self.module.render_markdown(self.module.build_packet(data, now=NOW))
        self.assertIn(
            r"Provider: \[Provider\](https://unrelated.example) \*bold\* \_em\_ \`code\` \\ trail \| line break",
            markdown,
        )
        self.assertIn(
            r"| Away \*stars\* \_under\_ \`ticks\` \\ slash: 2 | \[Home\](https://unrelated.example): 5 | final | \[Home\](https://unrelated.example) won by 3 |",
            markdown,
        )

    def test_markdown_shows_supplied_coverage_separately_from_retrieval(self):
        data = fixture()
        data["source"]["data_as_of"] = "2025-04-01T15:00:00Z"
        markdown = self.module.render_markdown(self.module.build_packet(data, now=NOW))
        self.assertIn(
            "Retrieved: 2026-10-31T11:00:00Z\nCoverage as of: 2025-04-01T15:00:00Z\n",
            markdown,
        )

    def test_markdown_labels_missing_coverage_unavailable(self):
        markdown = self.module.render_markdown(self.module.build_packet(fixture(), now=NOW))
        self.assertIn("Coverage as of: unavailable\n", markdown)

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
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertNotIn("Traceback", run.stderr)

    def test_cli_strict_returns_one_for_a_fetch_one_minute_in_future(self):
        with tempfile.TemporaryDirectory() as temp:
            data = fixture()
            data["source"]["fetched_at"] = "2026-10-31T12:01:00Z"
            path = Path(temp) / "input.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(path), "--format", "json",
                 "--strict", "--now", NOW.isoformat()],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertEqual(json.loads(run.stdout)["freshness"], "future")

    def test_cli_preserves_input_when_output_is_same_file_or_alias(self):
        for alias in ["same_path", "symlink", "hardlink"]:
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "input.json"
                original = (json.dumps(fixture()) + "\n").encode("utf-8")
                path.write_bytes(original)
                output = path if alias == "same_path" else Path(temp) / "output.json"
                if alias == "symlink":
                    output.symlink_to(path)
                elif alias == "hardlink":
                    os.link(path, output)
                run = subprocess.run(
                    [sys.executable, str(SCRIPT), "--input", str(path), "--output",
                     str(output), "--format", "json", "--now", NOW.isoformat()],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(run.returncode, 2, run.stderr)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(output.read_bytes(), original)
                self.assertNotIn("Traceback", run.stderr)

    def test_cli_writes_report_to_a_distinct_output_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            output = Path(temp) / "output.json"
            original = (json.dumps(fixture()) + "\n").encode("utf-8")
            path.write_bytes(original)
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(path), "--output",
                 str(output), "--format", "json", "--now", NOW.isoformat()],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["games"][0]["margin"], 3
            )


if __name__ == "__main__":
    unittest.main()
