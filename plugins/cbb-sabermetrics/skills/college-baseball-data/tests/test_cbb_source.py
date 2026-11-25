"""Source-backed extraction checks and explicitly synthetic adverse HTML cases."""

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cbb_source.py"
spec = importlib.util.spec_from_file_location("cbb_source", SCRIPT)
cbb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cbb)
FIXTURES = ROOT / "tests" / "fixtures"
SOURCE = {
    "requested_url": "https://texaslonghorns.com/sports/baseball/stats/2025",
    "final_url": "https://texaslonghorns.com/sports/baseball/stats/2025",
    "retrieved_at": None,
    "input_mode": "supplied_html",
}


def inspect(html, season=2025, kind="stats"):
    return cbb.inspect_html(html, SOURCE, season, kind)


def synthetic(body, title="2025 Baseball Statistics"):
    return "<!DOCTYPE html><html><head><title>%s</title></head><body><h1>%s</h1>%s</body></html>" % (title, title, body)


class SourceBackedTests(unittest.TestCase):
    def test_mendoza_original_source_cells_and_opponent_totals(self):
        packet = inspect((FIXTURES / "texas-2025-batting-excerpt.html").read_text())
        self.assertEqual(packet["status"], "ok")
        table = packet["tables"][0]
        self.assertEqual(table["column_count"], 22)
        self.assertEqual(table["header_rows"][0][:6], ["#", "Player", "AVG", "OPS", "GP-GS", "AB"])
        mendoza = table["rows"][0]
        self.assertEqual(mendoza[1], "Mendoza, Ethan")
        self.assertEqual(mendoza[5:11], ["225", "53", "75", "9", "4", "5"])
        self.assertEqual(mendoza[12:16], ["107", ".476", "36", "6"])
        self.assertEqual(table["rows"][-1][1], "Opponents")
        self.assertEqual(table["rows"][-1][5], "1862")
        self.assertEqual(table["rows"][-2][5], "1980")
        self.assertIsNone(table["rows"][-1][0])
        self.assertIsNone(packet["source"]["as_of"])
        self.assertEqual(packet["coverage"]["completeness"], "unknown")

    def test_original_screen_reader_record_labels_are_not_lost(self):
        packet = inspect((FIXTURES / "texas-2025-record-excerpt.html").read_text(), kind="schedule")
        self.assertEqual(packet["status"], "ok")
        self.assertEqual(packet["reported_record"]["overall"], {"wins": 44, "losses": 14, "ties": None})
        self.assertEqual(packet["reported_record"]["conference"], {"wins": 22, "losses": 8, "ties": None})
        self.assertEqual(packet["schedule_games"], [])
        self.assertFalse(packet["coverage"]["includes_all_pages"])

    def test_roster_ads_and_coaching_groups_are_not_players(self):
        packet = inspect((FIXTURES / "texas-2025-roster-excerpt.html").read_text(), kind="roster")
        players, staff = packet["tables"]
        self.assertEqual(players["row_sections"].count("body"), 7)
        self.assertEqual(players["row_sections"].count("advertisement"), 1)
        self.assertEqual(players["rows"][-1], ["Skip Ad"] * 10)
        self.assertEqual(staff["heading"], "Coaching Staff")
        self.assertEqual(staff["heading_source"], "column_group_header")
        self.assertEqual(staff["rows"][0][1:3], ["Jim Schlossnagle", "Head Coach"])
        self.assertNotIn("Skip Ad", cbb.markdown(packet))


class ScopeTests(unittest.TestCase):
    def test_url_year_is_not_season_evidence(self):
        packet = inspect(synthetic("<table><tr><td>1</td></tr></table>", title="Baseball Statistics"))
        self.assertEqual(packet["status"], "season_unverified")
        self.assertEqual(packet["tables"], [])

    def test_future_roster_is_not_relabelled_as_requested_season(self):
        packet = inspect(synthetic("<table><tr><td>A Player</td></tr></table>", title="2027 Baseball Roster"), season=2026, kind="roster")
        self.assertEqual(packet["status"], "season_mismatch")
        self.assertEqual(packet["season"]["observed"], [2027])
        self.assertEqual(packet["tables"], [])

    def test_conflicting_page_headings_fail_closed(self):
        packet = inspect(synthetic("<h2>2026 Baseball Statistics</h2><table><tr><td>1</td></tr></table>"))
        self.assertEqual(packet["status"], "season_ambiguous")

    def test_copyright_and_scripts_are_not_season_evidence(self):
        packet = inspect(synthetic("<script><h1>2030 Baseball Statistics</h1></script><footer>Copyright 2026</footer><table><tr><td>0</td></tr></table>"))
        self.assertEqual(packet["season"]["observed"], [2025])
        self.assertEqual(packet["status"], "ok")

    def test_source_kind_cannot_be_swapped(self):
        packet = inspect(synthetic("<table><tr><td>Player</td></tr></table>", title="2025 Baseball Roster"))
        self.assertEqual(packet["status"], "source_kind_mismatch")

    def test_academic_year_resolves_explicitly_to_end_year(self):
        packet = inspect(synthetic("<table><tr><td>Player</td></tr></table>", title="2024-25 Baseball Roster"), kind="roster")
        self.assertEqual(packet["status"], "ok")
        self.assertEqual(packet["season"]["observed"], [2025])
        self.assertEqual(packet["season"]["evidence"][0]["interpretation"], "academic-year end")

    def test_javascript_only_source_requests_browser(self):
        packet = inspect(synthetic("<div id='app'></div><script>const data = [];</script>"))
        self.assertEqual(packet["status"], "needs_browser")

    def test_academic_year_handles_century_rollover(self):
        html = synthetic("<table><tr><td>Player</td></tr></table>", title="1999-00 Baseball Roster")
        self.assertEqual(inspect(html, season=2000, kind="roster")["season"]["observed"], [2000])
        self.assertEqual(inspect(html, season=1999, kind="roster")["status"], "season_mismatch")

    def test_invalid_ranges_cannot_leak_their_first_year_as_verified(self):
        for label in ["2024-26", "2024-24", "2024-2026", "2024-2023"]:
            with self.subTest(label=label):
                html = synthetic("<table><tr><td>Player</td></tr></table>", title=label + " Baseball Roster")
                packet = inspect(html, season=2024, kind="roster")
                self.assertEqual(packet["status"], "season_ambiguous")
                self.assertEqual(packet["tables"], [])


class TableAndScheduleTests(unittest.TestCase):
    def test_inline_fragments_preserve_digits_and_real_word_separators(self):
        html = """<table><tr><th>IP</th><th>AVG</th><th>Name</th><th>School</th></tr>
        <tr><td>70.<!-- hydration -->2</td><td><span>.3</span><span>33</span></td>
        <td>Luke<span> Harrison</span></td><td><div>Texas</div><div>Longhorns<br>Austin</div></td></tr></table>"""
        self.assertEqual(inspect(synthetic(html))["tables"][0]["rows"], [["70.2", ".333", "Luke Harrison", "Texas Longhorns Austin"]])

    def test_zero_missing_dash_and_innings_are_distinct(self):
        packet = inspect(synthetic("<table><tr><th>SO</th><th>BB</th><th>HBP</th><th>IP</th></tr><tr><td>0</td><td></td><td>-</td><td>70.2</td></tr></table>"))
        self.assertEqual(packet["tables"][0]["rows"], [["0", None, "-", "70.2"]])

    def test_duplicate_column_names_and_rowspans_preserve_alignment(self):
        html = """<table><thead><tr><th rowspan="2">Team</th><th colspan="2">Overall</th><th colspan="2">Conference</th></tr>
        <tr><th>W</th><th>L</th><th>W</th><th>L</th></tr></thead><tbody>
        <tr><th scope="row" rowspan="2">A</th><td>10</td><td>2</td><td>5</td><td>1</td></tr>
        <tr><td>11</td><td>2</td><td>6</td><td>1</td></tr></tbody></table>"""
        table = inspect(synthetic(html))["tables"][0]
        self.assertEqual(table["header_rows"][1], ["Team", "W", "L", "W", "L"])
        self.assertEqual(table["rows"], [["A", "10", "2", "5", "1"], ["A", "11", "2", "6", "1"]])
        self.assertEqual(len(table["spans"]), 4)

    def test_invalid_spans_are_reported_not_flattened(self):
        packet = inspect(synthetic('<table><tr><td rowspan="99">A</td></tr></table>'))
        self.assertEqual(packet["status"], "needs_browser")
        self.assertEqual(len(packet["rejected_tables"]), 1)
        self.assertEqual(packet["tables"], [])

    def test_valueless_spans_reject_only_the_affected_table(self):
        for attribute in ("colspan", "rowspan"):
            with self.subTest(attribute=attribute):
                html = '<table><tr><td %s>Invalid</td></tr></table><table><tr><td>70.2</td></tr></table>' % attribute
                packet = inspect(synthetic(html))
                self.assertEqual(packet["status"], "partial")
                self.assertEqual(packet["rejected_tables"], [{"source_table_index": 0, "reason": "Invalid table span"}])
                self.assertEqual(packet["tables"][0]["source_table_index"], 1)
                self.assertEqual(packet["tables"][0]["rows"], [["70.2"]])

    def test_implicitly_closed_cells_require_browser_instead_of_concatenation(self):
        packet = inspect(synthetic("<table><tr><th>H<th>AB<tr><td>1<td>3</table>"))
        self.assertEqual(packet["status"], "needs_browser")
        self.assertTrue(packet["rejected_tables"])

    def test_unaligned_rows_warn_and_preserve_missing_cells(self):
        table = inspect(synthetic("<table><tr><th>A</th><th>B</th></tr><tr><td>1</td></tr></table>"))["tables"][0]
        self.assertEqual(table["rows"], [["1", None]])
        self.assertTrue(table["warnings"])

    def test_schedule_cancellation_and_zero_record_are_source_observations(self):
        html = """<span data-test-id="schedule-record__overall-win-value">0</span>
        <span data-test-id="schedule-record__overall-loss-value">0</span>
        <div data-test-id="s-game-card-standard__root">
        <a data-test-id="s-game-card-standard__header-team-opponent-link" href="https://example.edu/">Opponent</a>
        <span data-test-id="s-game-card-standard__header-game-date-details">Mar 2 (Sun)</span>
        <span data-test-id="s-game-card-standard__header-game-team-score">Canceled</span></div>"""
        packet = inspect(synthetic(html, title="2025 Baseball Schedule"), kind="schedule")
        self.assertEqual(packet["reported_record"]["overall"], {"wins": 0, "losses": 0, "ties": None})
        game = packet["schedule_games"][0]
        self.assertEqual(game["result_text"], "Canceled")
        self.assertIsNone(game["location"])
        self.assertNotIn("team_score", game)
        self.assertEqual(game["links"][0]["url"], "https://example.edu/")

    def test_conflicting_reported_records_are_errors(self):
        html = synthetic('<span data-test-id="schedule-record__overall-win-value">44</span><span data-test-id="schedule-record__overall-win-value">45</span>', title="2025 Baseball Schedule")
        with self.assertRaisesRegex(cbb.SourceError, "Conflicting"):
            inspect(html, kind="schedule")

    def test_markdown_is_readable_without_inferring_unknown_ties(self):
        packet = inspect((FIXTURES / "texas-2025-record-excerpt.html").read_text(), kind="schedule")
        text = cbb.markdown(packet)
        self.assertIn("44 wins, 14 losses; ties unavailable", text)
        self.assertIn("Source cutoff: unavailable", text)


class AccessAndCliTests(unittest.TestCase):
    def test_private_addresses_and_non_http_sources_rejected(self):
        for url in ("file:///tmp/a", "http://127.0.0.1/a", "http://[::1]/", "http://169.254.169.254/", "http://localhost/a", "http://user:password@example.com/", "https://example.com:9000/"):
            with self.subTest(url=url), self.assertRaises(cbb.SourceError):
                cbb.validate_url(url)

    def test_dns_to_private_host_rejected(self):
        with patch.object(cbb.urllib.request, "getproxies", return_value={}), patch.object(cbb.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("10.0.0.3", 443))]):
            with self.assertRaises(cbb.SourceError):
                cbb.validate_url("https://example.edu/", resolve=True)

    def test_configured_proxy_resolves_remote_hosts_without_direct_dns(self):
        with patch.object(cbb.urllib.request, "getproxies", return_value={"https": "http://proxy.example:8080"}), patch.object(cbb.urllib.request, "proxy_bypass", return_value=False), patch.object(cbb.socket, "getaddrinfo", side_effect=AssertionError("direct DNS not used")):
            self.assertEqual(cbb.validate_url("https://example.edu/", resolve=True), "https://example.edu/")

    def test_redirect_revalidates_destination(self):
        request = cbb.urllib.request.Request("https://example.edu/")
        with self.assertRaises(cbb.SourceError):
            cbb.PublicRedirects().redirect_request(request, None, 302, "Moved", {}, "http://127.0.0.1/private")

    def test_http_error_is_unavailable_not_empty_success(self):
        opener = MagicMock()
        opener.open.side_effect = cbb.urllib.error.HTTPError("https://example.edu/", 403, "Forbidden", {}, None)
        with patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(cbb.SourceError) as caught:
                cbb.fetch_source("https://example.edu/")
        self.assertEqual(caught.exception.code, "source_unavailable")
        self.assertIn("403", str(caught.exception))

    def test_non_html_and_oversized_downloads_are_explicit_errors(self):
        for media_type, length, code in (("application/json", "100", "unsupported_format"),
                                         ("text/html", str(cbb.MAX_BYTES + 1), "source_too_large")):
            with self.subTest(media_type=media_type, length=length):
                headers = Message()
                headers["Content-Type"] = media_type
                headers["Content-Length"] = length
                response = MagicMock()
                response.headers = headers
                response.geturl.return_value = "https://example.edu/"
                response.__enter__.return_value = response
                opener = MagicMock()
                opener.open.return_value = response
                with patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener):
                    with self.assertRaises(cbb.SourceError) as caught:
                        cbb.fetch_source("https://example.edu/")
                self.assertEqual(caught.exception.code, code)
                response.read.assert_not_called()
                response.read1.assert_not_called()

    def test_http_provenance_keeps_redirect_and_retrieval_separate(self):
        headers = Message()
        headers["Content-Type"] = "text/html; charset=utf-8"
        response = MagicMock()
        response.headers = headers
        response.status = 200
        response.geturl.return_value = "https://example.edu/baseball/stats/2025"
        response.read1.side_effect = [b"<h1>2025 Baseball Statistics</h1>", b""]
        response.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener):
            html, source = cbb.fetch_source("https://example.edu/stats")
        self.assertEqual(source["requested_url"], "https://example.edu/stats")
        self.assertEqual(source["final_url"], "https://example.edu/baseball/stats/2025")
        self.assertTrue(source["retrieved_at"])
        self.assertNotIn("as_of", source)
        self.assertIn("2025 Baseball", html)

    def test_incomplete_http_response_returns_structured_unavailable(self):
        headers = Message()
        headers["Content-Type"] = "text/html"
        response = MagicMock()
        response.headers = headers
        response.geturl.return_value = "https://example.edu/"
        response.read1.side_effect = cbb.http.client.IncompleteRead(b"partial", 100)
        response.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = response
        output = io.StringIO()
        with patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener), patch.object(sys, "stdout", output):
            code = cbb.main(["--url", "https://example.edu/", "--season", "2025", "--kind", "stats"])
        packet = json.loads(output.getvalue())
        self.assertEqual(code, 3)
        self.assertEqual(packet["status"], "source_unavailable")
        self.assertIn("IncompleteRead", packet["error"])
        self.assertEqual(packet["tables"], [])

    def test_eof_after_deadline_cannot_be_accepted_as_success(self):
        headers = Message()
        headers["Content-Type"] = "text/html"
        response = MagicMock()
        response.headers = headers
        response.geturl.return_value = "https://example.edu/"
        response.__enter__.return_value = response
        clock = [0.0]

        def late_eof(size):
            clock[0] = 31.0
            return b""

        response.read1.side_effect = late_eof
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener), patch.object(cbb.time, "monotonic", side_effect=lambda: clock[0]):
            with self.assertRaisesRegex(cbb.SourceError, "bounded download time"):
                cbb.fetch_source("https://example.edu/")

    def test_body_and_chunk_header_trickles_cannot_outlive_deadline(self):
        stop = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                if self.path == "/complete":
                    body = b"<h1>2025 Baseball Statistics</h1>"
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                if self.path == "/chunked":
                    self.send_header("Transfer-Encoding", "chunked")
                else:
                    self.send_header("Content-Length", "100")
                self.end_headers()
                try:
                    for _ in range(100):
                        # The chunked case never finishes its size line. A
                        # read1/socket inactivity timeout alone is insufficient.
                        self.wfile.write(b"1")
                        self.wfile.flush()
                        if stop.wait(0.02):
                            break
                except OSError:
                    pass

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        thread.start()
        opener = cbb.urllib.request.build_opener(cbb.urllib.request.ProxyHandler({}), cbb.PublicRedirects())
        try:
            with patch.object(cbb, "DOWNLOAD_SECONDS", 0.15), patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener):
                html, source = cbb.fetch_source("http://127.0.0.1:%s/complete" % server.server_port)
            self.assertEqual(html, "<h1>2025 Baseball Statistics</h1>")
            self.assertEqual(source["http_status"], 200)
            for path in ("/body", "/chunked"):
                with self.subTest(path=path):
                    started = time.monotonic()
                    with patch.object(cbb, "DOWNLOAD_SECONDS", 0.15), patch.object(cbb, "validate_url", side_effect=lambda url, resolve=False: url), patch.object(cbb.urllib.request, "build_opener", return_value=opener):
                        with self.assertRaisesRegex(cbb.SourceError, "bounded download time"):
                            cbb.fetch_source("http://127.0.0.1:%s%s" % (server.server_port, path))
                    self.assertLess(time.monotonic() - started, 0.6)
        finally:
            stop.set()
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def command(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, timeout=10)

    def test_actual_json_and_markdown_cli(self):
        args = ["--input", str(FIXTURES / "texas-2025-batting-excerpt.html"), "--source-url", SOURCE["final_url"], "--season", "2025", "--kind", "stats"]
        result = self.command(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertIsNone(packet["source"]["retrieved_at"])
        self.assertEqual(packet["source"]["input_mode"], "supplied_html")
        self.assertEqual(len(packet["source"]["content_sha256"]), 64)
        result = self.command(*args, "--format", "markdown")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Mendoza, Ethan", result.stdout)

    def test_wrong_season_exit_is_not_successful_empty_dataset(self):
        result = self.command("--input", str(FIXTURES / "texas-2025-batting-excerpt.html"), "--source-url", SOURCE["final_url"], "--season", "2026", "--kind", "stats")
        self.assertEqual(result.returncode, 3)
        self.assertEqual(json.loads(result.stdout)["status"], "season_mismatch")

    def test_input_output_collision_preserves_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.html"
            original = synthetic("<table><tr><td>1</td></tr></table>")
            path.write_text(original)
            result = self.command("--input", str(path), "--source-url", SOURCE["final_url"], "--season", "2025", "--kind", "stats", "--output", str(path))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(path.read_text(), original)

    def test_missing_attribution_and_invalid_year_are_input_errors(self):
        for args in (["--input", str(FIXTURES / "texas-2025-batting-excerpt.html"), "--season", "2025", "--kind", "stats"],
                     ["--url", "https://example.edu/", "--season", "1", "--kind", "stats"]):
            with self.subTest(args=args):
                result = self.command(*args)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr)

    def test_invalid_url_cli_is_a_structured_input_error(self):
        result = self.command("--url", "file:///tmp/source.html", "--season", "2025", "--kind", "stats")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid_url")


if __name__ == "__main__":
    unittest.main()
