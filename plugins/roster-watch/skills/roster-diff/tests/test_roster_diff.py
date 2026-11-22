"""Behavior tests for the offline roster comparison and its standalone CLI."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "roster_diff.py"
sys.path.insert(0, str(SCRIPT.parent))
from roster_diff import compare_rosters, render_markdown


def snapshot(players, *, earlier=True, completeness="complete", **overrides):
    capture = "before" if earlier else "after"
    return {
        "sport": "baseball",
        "team": "Test University",
        "season": "2099",
        "identity_namespace": "synthetic:test-university:2099",
        "observed_at": f"2099-01-0{1 if earlier else 2}T12:30:00Z",
        "source": {
            "url": f"https://example.invalid/{capture}",
            "completeness": completeness,
            "synthetic": True,
        },
        "players": players,
        **overrides,
    }


class CompareRostersTests(unittest.TestCase):
    def test_counts_records_provenance_and_missing_fields(self):
        before = snapshot([
            {"id": "02", "name": "Taylor Reed"},
            {"id": "01", "name": "Ada Reyes", "fields": {"number": 21, "class": None}},
            {"id": "04", "name": "Fran Yu"},
        ])
        after = snapshot([
            {"id": "04", "name": "Fran Yu", "fields": {}},
            {"id": "03", "name": "Jules Kim"},
            {"id": "01", "name": "Ada Reyes", "fields": {"number": 12, "position": None}},
        ], earlier=False)
        report = compare_rosters(before, after)
        self.assertEqual(report["counts"], {
            "before": 3, "after": 3, "unchanged": 1, "changed": 1,
            "observed_only_before": 1, "observed_only_after": 1,
        })
        self.assertEqual(report["scope"], {
            key: before[key] for key in ("sport", "team", "season", "identity_namespace")
        })
        self.assertEqual(report["snapshots"]["before"], {
            key: before[key] for key in ("observed_at", "source")
        })
        self.assertEqual(report["snapshots"]["after"], {
            key: after[key] for key in ("observed_at", "source")
        })
        self.assertEqual(report["observed_only_before"], [{
            "record": before["players"][0], "comparison": "absent_from_after",
        }])
        self.assertEqual(report["observed_only_after"], [{
            "record": after["players"][1], "comparison": "absent_from_before",
        }])
        self.assertEqual(report["changed"], [{
            "id": "01", "before": before["players"][1], "after": after["players"][2],
            "fields": [
                {"path": ["fields", "class"], "before": {"present": True, "value": None},
                 "after": {"present": False}},
                {"path": ["fields", "number"], "before": {"present": True, "value": 21},
                 "after": {"present": True, "value": 12}},
                {"path": ["fields", "position"], "before": {"present": False},
                 "after": {"present": True, "value": None}},
            ],
        }])
        markdown = render_markdown(report)
        for fragment in ("https://example.invalid/before", "https://example.invalid/after",
                         "SYNTHETIC", "(missing)", "`null`", "transfer", "eligibility", "injury"):
            self.assertIn(fragment, markdown)

    def test_same_name_different_ids_and_same_id_different_name(self):
        before = snapshot([
            {"id": "old", "name": "Sam Stone"},
            {"id": "same", "name": "Jo Ellis"},
        ])
        after = snapshot([
            {"id": "new", "name": "Sam Stone"},
            {"id": "same", "name": "Jojo Ellis"},
        ], earlier=False)
        report = compare_rosters(before, after)
        self.assertEqual(report["observed_only_before"][0]["record"]["id"], "old")
        self.assertEqual(report["observed_only_after"][0]["record"]["id"], "new")
        self.assertEqual(report["changed"][0]["fields"][0]["path"], ["name"])
        self.assertIn("reused", render_markdown(report).lower())

    def test_partial_coverage_is_unresolved_for_the_missing_side(self):
        for completeness_before, completeness_after in (
            ("partial", "complete"), ("complete", "partial"), ("partial", "partial"),
        ):
            with self.subTest(before=completeness_before, after=completeness_after):
                before = snapshot([{"id": "old", "name": "Sam Stone"}],
                                  completeness=completeness_before)
                after = snapshot([{"id": "new", "name": "Jules Kim"}], earlier=False,
                                 completeness=completeness_after)
                report = compare_rosters(before, after)
                expected_old = ("after_coverage_unresolved" if completeness_after == "partial"
                                else "absent_from_after")
                expected_new = ("before_coverage_unresolved" if completeness_before == "partial"
                                else "absent_from_before")
                self.assertEqual(report["observed_only_before"][0]["comparison"], expected_old)
                self.assertEqual(report["observed_only_after"][0]["comparison"], expected_new)
                self.assertIn("unresolved", render_markdown(report).lower())
                self.assertTrue(any("partial" in limitation.lower()
                                    for limitation in report["limitations"]))

    def test_complete_empty_and_partial_empty_are_valid(self):
        report = compare_rosters(snapshot([]), snapshot([], earlier=False, completeness="partial"))
        self.assertEqual(report["counts"], {
            "before": 0, "after": 0, "unchanged": 0, "changed": 0,
            "observed_only_before": 0, "observed_only_after": 0,
        })
        self.assertIn("unresolved", render_markdown(report).lower())

    def test_strict_json_types_and_deterministic_order(self):
        before = snapshot([
            {"id": "z", "name": "Zee"},
            {"id": "a", "name": "Aye"},
            {"id": "m", "name": "Em", "fields": {"details": {"b": 1, "a": True}}},
        ])
        after = snapshot([
            {"id": "m", "name": "Em", "fields": {"details": {"a": 1, "b": 1.0}}},
        ], earlier=False)
        report = compare_rosters(before, after)
        self.assertEqual([item["record"]["id"] for item in report["observed_only_before"]],
                         ["a", "z"])
        self.assertEqual(report["counts"]["changed"], 1)
        self.assertEqual(report["changed"][0]["fields"][0]["path"], ["fields", "details"])
        before["players"].reverse()
        self.assertEqual(compare_rosters(before, after), report)
        copied_before = copy.deepcopy(before)
        report["changed"][0]["before"]["fields"]["details"]["a"] = "edited"
        self.assertEqual(before, copied_before)

    def test_markdown_contains_untrusted_data_as_literals(self):
        name = "</code> [follow](https://example.invalid) ``\n# Forged heading"
        after = snapshot([{"id": "<i>", "name": name}], earlier=False)
        markdown = render_markdown(compare_rosters(snapshot([]), after))
        self.assertNotIn("\n# Forged heading", markdown)
        self.assertIn("``` ", markdown)
        self.assertIn(r"\n# Forged heading", markdown)

    def test_rejects_each_scope_mismatch(self):
        for scope in ("sport", "team", "season", "identity_namespace"):
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(ValueError, scope):
                    compare_rosters(snapshot([]), snapshot([], earlier=False, **{scope: "other"}))

    def test_compares_capture_times_with_offsets(self):
        before = snapshot([], observed_at="2099-01-02T01:30:00.1+02:00")
        compare_rosters(before, snapshot([], earlier=False, observed_at="2099-01-01T23:30:00.100000Z"))
        with self.assertRaisesRegex(ValueError, "earlier"):
            compare_rosters(before, snapshot([], earlier=False, observed_at="2099-01-01T23:30:00.0999Z"))

    def test_rejects_malformed_timestamps(self):
        for observed_at in (False, "2099-02-29T00:00:00Z", "2099-01-01T00:00:00",
                            "2099-01-01T00:00:00+00:60", "2099-01-01T00:00:00+24:00",
                            "20990101T000000Z", "2099-01-01 00:00:00Z"):
            with self.subTest(observed_at=observed_at):
                with self.assertRaisesRegex(ValueError, "observed_at"):
                    compare_rosters(snapshot([], observed_at=observed_at), snapshot([], earlier=False))

    def test_rejects_invalid_source_metadata(self):
        def compare_source(**source_overrides):
            before = snapshot([])
            before["source"].update(source_overrides)
            return compare_rosters(before, snapshot([], earlier=False))

        for url in ("https:///path", "ftp://example.invalid", "https://u:p@example.invalid",
                    "https://example.invalid:99999", "https://example.invalid:bad",
                    "https://ex\nample.invalid", "https://example.invalid\\@other.invalid",
                    "https://[::1]suffix/roster", "https://example.invalid/%ZZ"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "source.url"):
                    compare_source(url=url)
        with self.assertRaisesRegex(ValueError, "completeness"):
            compare_source(completeness=True)
        with self.assertRaisesRegex(ValueError, "synthetic"):
            compare_source(synthetic=1)

    def test_rejects_malformed_records_and_duplicate_ids(self):
        valid = {"id": "01", "name": "Ada Reyes"}
        cases = [
            (None, "players"), ({"id": valid}, "players"), ([None], "players"),
            ([valid, {**valid, "name": "another person"}], "duplicate"),
            ([{"id": 1, "name": "Aye"}], "id"),
            ([{"id": " 01", "name": "Aye"}], "id"),
            ([{"id": "01", "name": " "}], "name"),
            ([{**valid, "fields": None}], "fields"),
            ([{**valid, "fields": {"number": float("inf")}}], "finite"),
            ([{**valid, "fields": {"nested": {1: "invalid key"}}}], "string keys"),
            ([{**valid, "fields": {"nested": (1, 2)}}], "JSON"),
            ([{**valid, "number": 4}], "unexpected"),
        ]
        for players, error in cases:
            with self.subTest(players=players):
                with self.assertRaisesRegex(ValueError, error):
                    compare_rosters(snapshot(players), snapshot([], earlier=False))
        with self.assertRaisesRegex(ValueError, "season"):
            compare_rosters(snapshot([], season=True), snapshot([], earlier=False))


class CliTests(unittest.TestCase):
    def setUp(self):
        parent = tempfile.TemporaryDirectory()
        self.addCleanup(parent.cleanup)
        self.directory = Path(parent.name)
        self.before = self.directory / "before.json"
        self.after = self.directory / "after.json"
        self.before.write_text(json.dumps(snapshot([])), encoding="utf-8")
        self.after.write_text(json.dumps(snapshot([], earlier=False)), encoding="utf-8")

    def cli(self, *flags, before=None, after=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--before", str(before or self.before),
             "--after", str(after or self.after), *map(str, flags)],
            cwd=self.directory, capture_output=True, text=True, check=False,
        )

    def test_synthetic_example_runs_outside_repository_in_both_formats(self):
        before = SKILL / "examples" / "before.json"
        after = SKILL / "examples" / "after.json"
        result = self.cli("--format", "json", before=before, after=after)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["snapshots"]["before"]["source"]["synthetic"])
        self.assertTrue(report["snapshots"]["after"]["source"]["synthetic"])
        self.assertEqual(report["counts"]["changed"], 1)
        result = self.cli(before=before, after=after)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, render_markdown(report))

    def test_rejects_source_aliases_and_preserves_bytes(self):
        link = self.directory / "symlink.json"
        link.symlink_to(self.before)
        hardlink = self.directory / "hardlink.json"
        os.link(self.after, hardlink)
        subdirectory = self.directory / "subdir"
        subdirectory.mkdir()
        alternate = subdirectory / ".." / self.before.name
        before_bytes, after_bytes = self.before.read_bytes(), self.after.read_bytes()
        for destination in (self.before, self.after, link, hardlink, alternate):
            with self.subTest(destination=destination):
                result = self.cli("--output", destination)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("--output", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(self.before.read_bytes(), before_bytes)
                self.assertEqual(self.after.read_bytes(), after_bytes)

    def test_output_written_only_after_successful_validation(self):
        output = self.directory / "report.json"
        result = self.cli("--format", "json", "--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["counts"]["before"], 0)
        self.before.write_text("invalid JSON", encoding="utf-8")
        original = output.read_bytes()
        result = self.cli("--output", output)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("before", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(output.read_bytes(), original)

    def test_rejects_duplicate_json_keys_and_nonfinite_values(self):
        original = json.loads(self.before.read_text(encoding="utf-8"))
        values = ('{"position": "P", "position": "C"}', '{"x": NaN}',
                  '{"x": Infinity}', '{"x": 1e400}')
        for value in values:
            with self.subTest(value=value):
                original["players"] = [{"id": "1", "name": "Aye", "fields": "PLACEHOLDER"}]
                self.before.write_text(json.dumps(original).replace('"PLACEHOLDER"', value),
                                       encoding="utf-8")
                result = self.cli()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertRegex(result.stderr, r"duplicate|finite")
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
