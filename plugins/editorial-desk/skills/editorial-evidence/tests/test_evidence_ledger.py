import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from datetime import datetime, timezone

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/evidence_ledger.py"
NOW = datetime(2026, 10, 31, 12, tzinfo=timezone.utc)


def fixture():
    return {
        "sources": [
            {
                "id": "s1",
                "url": "https://example.org/box",
                "title": "Synthetic fixture",
                "retrieved_at": "2026-10-31T11:00:00Z",
                "excerpt": "We played well.",
            }
        ],
        "claims": [
            {
                "id": "c1",
                "kind": "fact",
                "text": "Fixture team scored five.",
                "source_ids": ["s1"],
            }
        ],
    }


class EvidenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            SCRIPT.is_file(), "Executable evidence-ledger helper is required"
        )
        spec = importlib.util.spec_from_file_location("evidence_ledger", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_complete_is_documentation_not_truth_verification(self):
        result = self.module.audit_ledger(fixture(), now=NOW)
        self.assertTrue(result["complete"])
        self.assertIn("not", result["limitation"])
        self.assertEqual(result["claims"][0]["status"], "documented")

    def test_unsourced_fact_and_unknown_source_block_completion(self):
        for sources in [[], ["missing"]]:
            data = fixture()
            data["claims"][0]["source_ids"] = sources
            self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_quote_requires_exact_excerpt_match(self):
        data = fixture()
        data["claims"][0].update(kind="quote", text="We played well.")
        self.assertTrue(self.module.audit_ledger(data, now=NOW)["complete"])
        data["claims"][0]["text"] = "We were perfect."
        self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_safe_arithmetic_checks_supported_operations(self):
        for operation, inputs, value in [
            ("sum", [3, 4], 7),
            ("difference", [5, 2], 3),
            ("ratio", [3, 4], 0.75),
            ("percentage", [3, 4], 75),
        ]:
            data = fixture()
            data["claims"][0].update(
                kind="calculation",
                calculation={"operation": operation, "inputs": inputs, "value": value},
            )
            result = self.module.audit_ledger(data, now=NOW)
            self.assertTrue(result["complete"], result)
            data["claims"][0]["calculation"]["value"] = 999
            self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_zero_denominator_and_nonfinite_input_block_completion(self):
        for inputs in [[1, 0], [float("nan"), 2], [True, 2]]:
            data = fixture()
            data["claims"][0].update(
                kind="calculation",
                calculation={"operation": "ratio", "inputs": inputs, "value": 0},
            )
            self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_opinions_remain_labeled(self):
        data = fixture()
        data["claims"][0].update(kind="opinion", source_ids=[])
        result = self.module.audit_ledger(data, now=NOW)
        self.assertTrue(result["complete"])
        self.assertEqual(result["claims"][0]["status"], "opinion")

    def test_current_stale_sources_block_but_historical_do_not(self):
        data = fixture()
        data["sources"][0]["retrieved_at"] = "2025-01-01T00:00:00Z"
        self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])
        data["claims"][0]["temporal_scope"] = "historical"
        self.assertTrue(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_rejects_duplicate_ids_and_missing_source_dates(self):
        data = fixture()
        data["sources"].append(dict(data["sources"][0]))
        with self.assertRaises(ValueError):
            self.module.audit_ledger(data, now=NOW)
        data = fixture()
        del data["sources"][0]["retrieved_at"]
        with self.assertRaises(ValueError):
            self.module.audit_ledger(data, now=NOW)

    def test_empty_claims_are_not_ready(self):
        data = fixture()
        data["claims"] = []
        self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_cli_strict_nonzero_for_unresolved_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            data = fixture()
            data["claims"][0]["source_ids"] = []
            path = Path(temp) / "input.json"
            path.write_text(json.dumps(data))
            run = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(path),
                    "--format",
                    "json",
                    "--strict",
                    "--now",
                    NOW.isoformat(),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertFalse(json.loads(run.stdout)["complete"])


if __name__ == "__main__":
    unittest.main()
