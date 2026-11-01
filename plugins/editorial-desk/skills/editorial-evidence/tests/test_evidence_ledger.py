import importlib.util, io, json, os, subprocess, sys, tempfile, unittest
from contextlib import redirect_stderr
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

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

    def _run_output_cli(self, path, output):
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = self.module.main([
                "--input", str(path), "--output", str(output), "--format", "json",
                "--now", NOW.isoformat(),
            ])
        return code, errors.getvalue()

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

    def test_cli_strict_marks_quote_with_null_excerpt_unresolved(self):
        with tempfile.TemporaryDirectory() as temp:
            data = fixture()
            data["sources"][0]["excerpt"] = None
            data["claims"][0].update(kind="quote", text="We played well.")
            path = Path(temp) / "input.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(path), "--format", "json",
                 "--strict", "--now", NOW.isoformat()],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 1, run.stderr)
            result = json.loads(run.stdout)
            self.assertFalse(result["complete"])
            self.assertEqual(result["claims"][0]["status"], "unresolved")
            self.assertIsNone(result["sources"][0]["excerpt"])

    def test_padded_citations_resolve_for_quotes_and_output_uses_normalized_ids(self):
        data = fixture()
        data["sources"][0]["id"] = " s1\t"
        data["claims"][0].update(
            kind="quote", text="We played well.", source_ids=["\ts1 "]
        )
        result = self.module.audit_ledger(data, now=NOW)
        self.assertTrue(result["complete"], result["issues"])
        self.assertEqual(result["claims"][0]["status"], "documented")
        self.assertEqual(result["claims"][0]["source_ids"], ["s1"])
        self.assertEqual(result["sources"][0]["id"], "s1")
        self.assertEqual(data["sources"][0]["id"], " s1\t")

    def test_markdown_renders_source_title_images_and_formatting_as_literal_text(self):
        data = fixture()
        data["sources"][0]["title"] = (
            "![Tracking pixel](https://unrelated.example/pixel) *bold* _em_ `code` "
            "<b>tag</b>\nline"
        )
        result = self.module.audit_ledger(data, now=NOW)
        self.assertTrue(result["complete"])
        self.assertIn(
            r"s1: !\[Tracking pixel\](https://unrelated.example/pixel) \*bold\* \_em\_ \`code\` &lt;b&gt;tag&lt;/b&gt; line <https://example.org/box>",
            self.module.render_markdown(result),
        )

    def test_markdown_keeps_strikethrough_markers_literal_in_titles_and_claims(self):
        data = fixture()
        data["sources"][0]["title"] = r"~~corrected~~ \~"
        data["sources"][0]["excerpt"] = "~~exact quote~~"
        data["claims"][0].update(kind="quote", text="~~exact quote~~")
        result = self.module.audit_ledger(data, now=NOW)
        self.assertTrue(result["complete"], result["issues"])
        markdown = self.module.render_markdown(result)
        self.assertIn(r"s1: \~\~corrected\~\~ \\\~ <https://example.org/box>", markdown)
        self.assertIn(r"| c1: \~\~exact quote\~\~ | quote | documented | s1 |", markdown)
        self.assertEqual(result["sources"][0]["title"], r"~~corrected~~ \~")
        self.assertEqual(result["claims"][0]["text"], "~~exact quote~~")

    def test_markdown_renders_fact_links_and_backslash_before_pipe_as_literal_text(self):
        data = fixture()
        data["claims"][0]["text"] = r"[Home](https://unrelated.example) \| *bold* _em_ `code`"
        result = self.module.audit_ledger(data, now=NOW)
        self.assertTrue(result["complete"])
        self.assertIn(
            r"| c1: \[Home\](https://unrelated.example) \\\| \*bold\* \_em\_ \`code\` | fact | documented | s1 |",
            self.module.render_markdown(result),
        )

    def test_markdown_escaping_preserves_exact_quote_and_source_excerpt(self):
        data = fixture()
        quote = r"[Home](https://unrelated.example) \| *played* _well_ `today` <b>yes</b>"
        excerpt = "Coach said: " + quote + " Then left."
        data["claims"][0].update(kind="quote", text=quote)
        data["sources"][0]["excerpt"] = excerpt
        result = self.module.audit_ledger(data, now=NOW)
        self.assertTrue(result["complete"], result["issues"])
        self.assertEqual(result["claims"][0]["status"], "documented")
        self.assertEqual(result["claims"][0]["text"], quote)
        self.assertEqual(result["sources"][0]["excerpt"], excerpt)
        self.module.render_markdown(result)
        serialized = json.loads(json.dumps(result))
        self.assertEqual(serialized["claims"][0]["text"], quote)
        self.assertEqual(serialized["sources"][0]["excerpt"], excerpt)
        data["claims"][0]["text"] = quote + "!"
        self.assertFalse(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_markdown_normalizes_line_endings_inside_claims_and_source_titles(self):
        for newline in ["\r", "\r\n", "\n"]:
            with self.subTest(newline=repr(newline)):
                data = fixture()
                data["claims"][0]["text"] = "First" + newline + "second."
                data["sources"][0]["title"] = "Source" + newline + "title"
                result = self.module.audit_ledger(data, now=NOW)
                markdown = self.module.render_markdown(result)
                self.assertNotIn("\r", markdown)
                self.assertIn("| c1: First second. | fact | documented | s1 |", markdown)
                self.assertIn("s1: Source title <https://example.org/box>", markdown)
                self.assertEqual(result["claims"][0]["text"], "First" + newline + "second.")

    def test_source_urls_reject_malformed_and_out_of_range_ports(self):
        for port in ["bad", "65536", "-1", "443.0"]:
            with self.subTest(port=port):
                data = fixture()
                data["sources"][0]["url"] = "https://example.org:" + port + "/box"
                with self.assertRaises(ValueError):
                    self.module.audit_ledger(data, now=NOW)

    def test_source_urls_accept_valid_ports_and_ipv6(self):
        for url in ["https://example.org:443/box", "https://[2001:db8::1]:8443/box"]:
            with self.subTest(url=url):
                data = fixture()
                data["sources"][0]["url"] = url
                self.assertTrue(self.module.audit_ledger(data, now=NOW)["complete"])

    def test_source_urls_reject_angle_brackets_before_markdown_rendering(self):
        for url in [
            "https://example.org/<script>alert(1)</script>",
            "https://example.org/box><b>Other</b>",
        ]:
            with self.subTest(url=url):
                data = fixture()
                data["sources"][0]["url"] = url
                with self.assertRaises(ValueError):
                    self.module.audit_ledger(data, now=NOW)

    def test_any_future_retrieval_blocks_current_and_historical_claims(self):
        for scope in ["current", "historical"]:
            for retrieved_at in [
                "2026-10-31T12:00:00.000001Z",
                "2026-10-31T12:00:01Z",
                "2026-10-31T12:01:00Z",
            ]:
                with self.subTest(scope=scope, retrieved_at=retrieved_at):
                    data = fixture()
                    data["sources"][0]["retrieved_at"] = retrieved_at
                    data["claims"][0]["temporal_scope"] = scope
                    result = self.module.audit_ledger(data, now=NOW)
                    self.assertFalse(result["complete"])
                    self.assertEqual(result["claims"][0]["status"], "unresolved")
                    self.assertIn("future", result["issues"][0]["message"])

    def test_retrieval_at_now_is_not_future(self):
        data = fixture()
        data["sources"][0]["retrieved_at"] = "2026-10-31T12:00:00Z"
        self.assertTrue(self.module.audit_ledger(data, now=NOW)["complete"])

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

    def test_cli_strict_returns_one_for_a_retrieval_one_minute_in_future(self):
        with tempfile.TemporaryDirectory() as temp:
            data = fixture()
            data["sources"][0]["retrieved_at"] = "2026-10-31T12:01:00Z"
            path = Path(temp) / "input.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(path), "--format", "json",
                 "--strict", "--now", NOW.isoformat()],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertFalse(json.loads(run.stdout)["complete"])

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
            self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["complete"])

    def test_cli_racing_output_alias_cannot_change_input_bytes_or_inode(self):
        for alias in ["symlink", "hardlink"]:
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                path, output = Path(temp) / "input.json", Path(temp) / "output.json"
                original = json.dumps(fixture()).encode("utf-8")
                path.write_bytes(original)
                input_inode = path.stat().st_ino
                output.write_text("previous report", encoding="utf-8")
                samefile = Path.samefile
                checked_outputs = {output, output.parent.resolve() / output.name}
                raced = []

                def replace_after_alias_check(candidate, other):
                    result = samefile(candidate, other)
                    if candidate in checked_outputs and not raced:
                        candidate.unlink()
                        if alias == "symlink":
                            candidate.symlink_to(path)
                        else:
                            os.link(path, candidate)
                        self.assertTrue(samefile(candidate, path))
                        raced.append(alias)
                    return result

                with patch.object(Path, "samefile", replace_after_alias_check):
                    code, errors = self._run_output_cli(path, output)
                self.assertEqual(raced, [alias])
                self.assertEqual(code, 0, errors)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(path.stat().st_ino, input_inode)
                self.assertFalse(output.samefile(path))
                self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["complete"])
                self.assertEqual({p.name for p in Path(temp).iterdir()}, {"input.json", "output.json"})

    def test_cli_keeps_selected_destination_when_public_parent_symlink_is_retargeted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_dir, selected_dir = root / "input", root / "selected"
            input_dir.mkdir()
            selected_dir.mkdir()
            path, selected_report = input_dir / "report.json", selected_dir / "report.json"
            original = json.dumps(fixture()).encode("utf-8")
            path.write_bytes(original)
            input_inode = path.stat().st_ino
            selected_report.write_text("previous report", encoding="utf-8")
            public_parent = root / "destination"
            public_parent.symlink_to(selected_dir, target_is_directory=True)
            output = public_parent / "report.json"
            checked_outputs = {output, selected_report.resolve()}
            samefile = Path.samefile
            raced = []

            def retarget_parent_after_alias_check(candidate, other):
                result = samefile(candidate, other)
                if candidate in checked_outputs and not raced:
                    public_parent.unlink()
                    public_parent.symlink_to(input_dir, target_is_directory=True)
                    raced.append("retargeted")
                return result

            with patch.object(Path, "samefile", retarget_parent_after_alias_check):
                code, errors = self._run_output_cli(path, output)
            self.assertEqual(raced, ["retargeted"])
            self.assertEqual(code, 0, errors)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(path.stat().st_ino, input_inode)
            self.assertTrue(json.loads(selected_report.read_text(encoding="utf-8"))["complete"])
            self.assertEqual({p.name for p in selected_dir.iterdir()}, {"report.json"})
            self.assertEqual({p.name for p in input_dir.iterdir()}, {"report.json"})
            self.assertEqual(public_parent.resolve(), input_dir.resolve())

    def test_cli_failed_report_write_preserves_previous_output_and_cleans_temporary_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path, output = Path(temp) / "input.json", Path(temp) / "output.json"
            original = json.dumps(fixture()).encode("utf-8")
            path.write_bytes(original)
            output.write_bytes(b"previous report")
            write_text = Path.write_text

            def fail_after_partial_write(candidate, value, **kwargs):
                write_text(candidate, "partial report", **kwargs)
                raise OSError("Simulated report write failure")

            with patch.object(Path, "write_text", fail_after_partial_write):
                code, errors = self._run_output_cli(path, output)
            self.assertEqual(code, 2, errors)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(output.read_bytes(), b"previous report")
            self.assertEqual({p.name for p in Path(temp).iterdir()}, {"input.json", "output.json"})

    def test_cli_failed_replace_preserves_previous_output_and_cleans_temporary_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path, output = Path(temp) / "input.json", Path(temp) / "output.json"
            original = json.dumps(fixture()).encode("utf-8")
            path.write_bytes(original)
            output.write_bytes(b"previous report")
            with patch.object(os, "replace", side_effect=OSError("Simulated rename failure")):
                code, errors = self._run_output_cli(path, output)
            self.assertEqual(code, 2, errors)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(output.read_bytes(), b"previous report")
            self.assertEqual({p.name for p in Path(temp).iterdir()}, {"input.json", "output.json"})

    def test_cli_preserves_existing_output_mode_and_new_file_default_permissions(self):
        for existing in [False, True]:
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as temp:
                path, output = Path(temp) / "input.json", Path(temp) / "output.json"
                path.write_text(json.dumps(fixture()), encoding="utf-8")
                expected_mode = path.stat().st_mode & 0o777
                if existing:
                    output.write_text("previous report", encoding="utf-8")
                    output.chmod(0o640)
                    expected_mode = 0o640
                code, errors = self._run_output_cli(path, output)
                self.assertEqual(code, 0, errors)
                self.assertEqual(output.stat().st_mode & 0o777, expected_mode)
                self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["complete"])


if __name__ == "__main__":
    unittest.main()
