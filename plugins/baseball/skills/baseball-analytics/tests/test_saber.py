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


@unittest.skipUnless(os.environ.get("SPORTS_LIVE"), "set SPORTS_LIVE=1 to hit the MLB Stats API")
class Live(unittest.TestCase):
    def test_mlb_stats_api_ohtani(self):
        s = saber.fetch_mlb(660271, 2024, "hitting")
        self.assertEqual(saber.batting_line(s, saber.constants(2024))["wOBA"], 0.431)


if __name__ == "__main__":
    unittest.main()
