"""Checks against numbers published by FanGraphs and the MLB Stats API (read 2026-10-27)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import saber  # noqa: E402

# Shohei Ohtani 2024, MLB Stats API person 660271, stats[0].splits[0].stat
OHTANI_2024_API = {"plateAppearances": 731, "atBats": 636, "hits": 197, "doubles": 38, "triples": 7,
                   "homeRuns": 54, "baseOnBalls": 81, "intentionalWalks": 10, "hitByPitch": 6,
                   "sacFlies": 5, "strikeOuts": 162}
# Tarik Skubal 2024, person 669373
SKUBAL_2024 = {"IP": "192.0", "HR": 15, "BB": 35, "IBB": 0, "HBP": 9, "SO": 228, "ER": 51, "BF": 753}
# Baseball-Reference 2024 MLB batting totals
MLB_2024_TOTALS = {"PA": 182449, "AB": 163687, "R": 21343, "H": 39823, "2B": 7771, "3B": 697,
                   "HR": 5453, "BB": 14929, "IBB": 509, "HBP": 2020, "SF": 1261, "SO": 41197}


class Batting(unittest.TestCase):
    def setUp(self):
        self.s = saber.mlb_stat_to_counts(OHTANI_2024_API)
        self.line = saber.batting_line(self.s, saber.constants(2024))

    def test_woba_matches_fangraphs(self):  # FanGraphs: .431
        self.assertEqual(self.line["wOBA"], 0.431)

    def test_slash_and_rates(self):  # FanGraphs: .310/.390/.646, ISO .336, BABIP .336, BB% 11.1, K% 22.2
        self.assertEqual((self.line["AVG"], self.line["OBP"], self.line["SLG"]), (0.310, 0.390, 0.646))
        self.assertEqual(self.line["ISO"], 0.336)
        self.assertEqual(self.line["BABIP"], 0.336)
        self.assertAlmostEqual(self.line["BB%"], 0.111, places=3)
        self.assertAlmostEqual(self.line["K%"], 0.222, places=3)

    def test_wrc_plus_near_fangraphs(self):
        # FanGraphs: 179. It divides by NL non-pitcher wRC/PA and uses its park factor,
        # so a neutral-park, all-league approximation lands a few points off.
        self.assertLessEqual(abs(self.line["wRC+"] - 179), 5)


class Pitching(unittest.TestCase):
    def test_fip_matches_fangraphs(self):  # FanGraphs: FIP 2.49, ERA 2.39, K/9 10.69, BB/9 1.64, HR/9 0.70
        line = saber.pitching_line(SKUBAL_2024, saber.constants(2024))
        self.assertEqual(line["FIP"], 2.49)
        self.assertEqual(line["ERA"], 2.39)
        self.assertEqual((line["K/9"], line["BB/9"], line["HR/9"]), (10.69, 1.64, 0.70))

    def test_scoreless_line_reports_zero_era(self):
        line = saber.pitching_line({"IP": "6.0", "HR": 0, "BB": 1, "SO": 7, "ER": 0}, saber.constants(2024))
        self.assertEqual(line["ERA"], 0.0)

    def test_api_pitching_object_keeps_hit_batsmen(self):
        # The Stats API's pitching group can carry hit batters as hitBatsmen.
        stat = {"inningsPitched": "192.0", "homeRuns": 15, "baseOnBalls": 35, "intentionalWalks": 0,
                "hitBatsmen": 9, "strikeOuts": 228, "earnedRuns": 51, "battersFaced": 753}
        line = saber.pitching_line(saber.mlb_stat_to_counts(stat), saber.constants(2024))
        self.assertEqual(line["FIP"], 2.49)

    def test_parse_ip_counts_outs(self):
        self.assertAlmostEqual(saber.parse_ip("6.2"), 6 + 2 / 3)
        self.assertAlmostEqual(saber.parse_ip("192.0"), 192)
        self.assertEqual(saber.parse_ip(7), 7)
        with self.assertRaises(ValueError):
            saber.parse_ip("6.5")


class LeagueMode(unittest.TestCase):
    def test_rebuilds_fangraphs_scale_from_totals(self):
        c = saber.league_constants(MLB_2024_TOTALS)
        self.assertAlmostEqual(c["scale"], 1.242, delta=0.003)
        self.assertAlmostEqual(c["lg_woba"], 0.310, delta=0.001)
        self.assertAlmostEqual(c["r_pa"], 0.117, delta=0.001)
        self.assertAlmostEqual(c["wHR"], 2.050, delta=0.005)

    def test_league_woba_equals_league_obp(self):
        ncaa_like = {"PA": 50000, "AB": 43000, "R": 8000, "H": 12500, "2B": 2500, "3B": 250,
                     "HR": 1100, "BB": 5000, "IBB": 100, "HBP": 1200, "SF": 400, "SO": 9500}
        c = saber.league_constants(ncaa_like)
        self.assertAlmostEqual(saber.woba(ncaa_like, c), c["lg_woba"], places=9)
        self.assertGreater(c["scale"], 1.0)

    def test_cfip_from_totals_makes_league_fip_equal_era(self):
        t = dict(MLB_2024_TOTALS, ERA=5.85, IP="14000.1", BB=6000, HBP=900, SO=11000, HR=1300)
        c = saber.league_constants(t)
        self.assertAlmostEqual(saber.fip(t, c), 5.85, places=9)

    def test_unknown_season_says_what_to_do(self):
        with self.assertRaisesRegex(KeyError, "league_constants"):
            saber.constants(1999)


class Cli(unittest.TestCase):
    def test_pitching_json(self):
        import io
        import json
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            saber.main(["pitching", "--season", "2024", "--stats", json.dumps(SKUBAL_2024)])
        self.assertEqual(json.loads(buf.getvalue())["FIP"], 2.49)


class EdgeCases(unittest.TestCase):
    """Inputs that used to crash or return nonsense instead of an answer or a clear error."""

    def test_zero_pa_leaves_run_values_undefined(self):  # --stats '{}' raised ZeroDivisionError
        line = saber.batting_line({}, saber.constants(2024))
        self.assertIsNone(line["AVG"])
        self.assertIsNone(line["wOBA"])
        self.assertIsNone(line["wRC+"])

    def test_zero_ip_leaves_rates_undefined(self):  # {"IP":"0.0"} raised ZeroDivisionError
        line = saber.pitching_line({"IP": "0.0", "BB": 1, "ER": 3, "BF": 2}, saber.constants(2024))
        self.assertIsNone(line["FIP"])
        self.assertIsNone(line["ERA"])
        self.assertIsNone(line["K/9"])
        self.assertEqual(line["BB%"], 0.5)

    def test_ibb_above_bb_is_rejected(self):  # gave a negative unintentional-walk count
        with self.assertRaisesRegex(ValueError, "IBB"):
            saber.batting_line({"AB": 10, "H": 3, "BB": 1, "IBB": 4}, saber.constants(2024))

    def test_impossible_counts_are_rejected(self):
        for s in ({"AB": 10, "H": -3}, {"AB": 10, "H": 2, "HR": 3}, {"AB": 2, "H": 3}):
            with self.assertRaises(ValueError, msg=s):
                saber.batting_line(s, saber.constants(2024))
        for ip in ("-5.0", ""):
            with self.assertRaises(ValueError, msg=ip):
                saber.parse_ip(ip)

    def test_numeric_strings_are_read_as_numbers(self):  # '{"AB":"636"}' raised TypeError
        as_text = {k: str(v) for k, v in saber.mlb_stat_to_counts(OHTANI_2024_API).items()}
        self.assertEqual(saber.batting_line(as_text, saber.constants(2024))["wOBA"], 0.431)

    def test_park_factor_on_fangraphs_100_scale(self):  # 105 gave wRC+ -10217
        s, c = saber.mlb_stat_to_counts(OHTANI_2024_API), saber.constants(2024)
        self.assertEqual(saber.batting_line(s, c, 105), saber.batting_line(s, c, 1.05))
        with self.assertRaises(ValueError):
            saber.batting_line(s, c, 0)


class LeagueTotalsMissingFields(unittest.TestCase):
    BAT = {k: v for k, v in MLB_2024_TOTALS.items() if k not in ("R",)}

    def test_no_era_means_no_cfip_not_mlb_cfip(self):  # silently kept MLB 2024 cFIP 3.166
        c = saber.league_constants(MLB_2024_TOTALS)
        self.assertIsNone(c["cfip"])
        self.assertIn("cfip", c["missing"])
        self.assertIsNone(saber.pitching_line(SKUBAL_2024, c)["FIP"])

    def test_no_runs_means_no_wrc_plus(self):  # PA without R gave R/PA 0, then ZeroDivisionError
        c = saber.league_constants(self.BAT)
        self.assertIsNone(c["r_pa"])
        line = saber.batting_line(saber.mlb_stat_to_counts(OHTANI_2024_API), c)
        self.assertEqual(line["wOBA"], 0.431)
        self.assertIsNone(line["wRC+"])

    def test_zero_ip_with_era_does_not_crash(self):
        c = saber.league_constants(dict(MLB_2024_TOTALS, ERA=4.0, IP="0.0"))
        self.assertIsNone(c["cfip"])

    def test_era_that_is_not_a_number_is_named(self):
        for era in ("x", [4.0]):
            with self.assertRaisesRegex(ValueError, "ERA"):
                saber.league_constants(dict(MLB_2024_TOTALS, ERA=era, IP="1000.0"))

    def test_empty_totals_say_what_is_needed(self):  # raised ZeroDivisionError
        with self.assertRaisesRegex(ValueError, "AB"):
            saber.league_constants({})


class CliErrors(unittest.TestCase):
    def run_cli(self, argv):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = saber.main(argv)
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def test_unknown_season_is_a_message_not_a_traceback(self):
        code, _, err = self.run_cli(["batting", "--season", "1999", "--stats", '{"AB":1}'])
        self.assertEqual(code, 2)
        self.assertIn("no FanGraphs constants for 1999", err)

    def test_bad_json_is_a_message(self):
        code, _, err = self.run_cli(["league", "--totals", '{"PA":..}'])
        self.assertEqual(code, 2)
        self.assertIn("JSON", err)

    def test_json_that_is_not_an_object_is_a_message(self):
        for argv in (["batting", "--season", "2024", "--stats", "[1]"],
                     ["pitching", "--season", "2024", "--stats", "5"],
                     ["league", "--totals", "[1]"],
                     ["batting", "--totals", '"x"', "--stats", "{}"]):
            code, _, err = self.run_cli(argv)
            self.assertEqual(code, 2, argv)
            self.assertIn("object", err)

    def test_stdin_that_is_not_an_object_is_a_message(self):
        import io
        from unittest import mock
        with mock.patch("sys.stdin", io.StringIO("[1, 2]")):
            code, _, err = self.run_cli(["batting", "--season", "2024"])
        self.assertEqual(code, 2)
        self.assertIn("object", err)

    def test_values_that_are_not_numbers_are_a_message(self):
        for value in ("[1]", '{"n": 1}', "true"):
            code, _, err = self.run_cli(["batting", "--season", "2024", "--stats", '{"AB": %s}' % value])
            self.assertEqual(code, 2, value)
            self.assertIn("AB", err)

    def test_unreachable_api_is_a_message(self):
        import urllib.error
        from unittest import mock
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("blocked")):
            code, _, err = self.run_cli(["batting", "--season", "2024", "--mlb-person", "660271"])
        self.assertEqual(code, 2)
        self.assertIn("MLB Stats API", err)

    def test_league_without_era_still_prints_and_warns(self):
        import json
        code, out, err = self.run_cli(["league", "--totals", json.dumps(MLB_2024_TOTALS)])
        self.assertEqual(code, 0)
        self.assertIsNone(json.loads(out)["cfip"])
        self.assertIn("ERA", err)


class TradedPlayer(unittest.TestCase):
    def test_takes_combined_split(self):
        # Shape of /people/665862/stats?stats=season&season=2024&group=hitting (Jazz Chisholm, MIA then NYY):
        # the combined split has numTeams and no team key.
        import io
        import json
        from unittest import mock
        body = {"stats": [{"splits": [
            {"season": "2024", "numTeams": 2, "stat": {"plateAppearances": 621, "atBats": 562, "hits": 144}},
            {"season": "2024", "team": {"name": "Miami Marlins"}, "stat": {"plateAppearances": 430}},
            {"season": "2024", "team": {"name": "New York Yankees"}, "stat": {"plateAppearances": 191}}]}]}
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(json.dumps(body).encode())
        with mock.patch("urllib.request.urlopen", return_value=resp):
            self.assertEqual(saber.fetch_mlb(665862, 2024, "hitting")["PA"], 621)


@unittest.skipUnless(os.environ.get("SPORTS_LIVE"), "set SPORTS_LIVE=1 to hit the MLB Stats API")
class Live(unittest.TestCase):
    def test_mlb_stats_api_ohtani(self):
        s = saber.fetch_mlb(660271, 2024, "hitting")
        self.assertEqual(saber.batting_line(s, saber.constants(2024))["wOBA"], 0.431)


if __name__ == "__main__":
    unittest.main()
