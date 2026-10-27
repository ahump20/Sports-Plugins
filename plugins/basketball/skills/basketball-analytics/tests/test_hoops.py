"""Checks against Basketball-Reference's published numbers."""
import csv
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import hoops  # noqa: E402

# Stephen Curry 2015-16 regular season (Basketball-Reference: eFG% .630, TS% .669)
CURRY_2016 = {"FG": 805, "FGA": 1598, "3P": 402, "FT": 363, "FTA": 400, "PTS": 2375}
GSW_BOXES = os.path.join(HERE, "fixtures", "team_box_2016_GSW.csv")  # ESPN boxes, every GSW game


def gsw():
    with open(GSW_BOXES, newline="") as f:
        return hoops.season_totals(list(csv.DictReader(f)), "GS")


class Shooting(unittest.TestCase):
    def test_curry_2016(self):
        self.assertEqual(round(hoops.efg_pct(CURRY_2016), 3), 0.630)
        self.assertEqual(round(hoops.ts_pct(CURRY_2016), 3), 0.669)

    def test_efg_rewards_threes(self):
        twos = {"FG": 5, "FGA": 10, "3P": 0}
        threes = {"FG": 5, "FGA": 10, "3P": 5}
        self.assertEqual(hoops.efg_pct(twos), 0.5)
        self.assertEqual(hoops.efg_pct(threes), 0.75)


class TeamRatings(unittest.TestCase):
    def test_warriors_2016_record_and_totals(self):
        t, o = gsw()
        self.assertEqual(t["G"], 82)
        self.assertEqual(t["PTS"] - o["PTS"], 882)  # MOV 10.76 x 82 games (Basketball-Reference)

    def test_warriors_2016_ratings_near_bbref(self):
        # Basketball-Reference: ORtg 115.18, DRtg 104.32. ESPN's box scores differ slightly from the
        # official ones Basketball-Reference sums, so allow half a point.
        r = hoops.team_ratings(*gsw())
        self.assertAlmostEqual(r["ORtg"], 115.18, delta=0.5)
        self.assertAlmostEqual(r["DRtg"], 104.32, delta=0.5)

    def test_possessions_are_symmetric(self):
        t, o = gsw()
        self.assertAlmostEqual(hoops.possessions(t, o), hoops.possessions(o, t))

    def test_four_factors_shape(self):
        ff = hoops.team_ratings(*gsw())["offense"]
        self.assertEqual(set(ff), {"eFG%", "TOV%", "ORB%", "FT/FGA"})
        self.assertTrue(0.5 < ff["eFG%"] < 0.6)

    def test_all_star_game_is_not_counted(self):
        # ESPN files the All-Star Game (WEST vs EAST) as a regular-season game.
        t, _ = gsw()
        self.assertEqual(t["G"], 82)


class Usage(unittest.TestCase):
    def test_usage_equals_share_when_player_plays_every_minute(self):
        team = {"FGA": 80, "FTA": 20, "TOV": 12}
        player = {"FGA": 16, "FTA": 4, "TOV": 2.4, "MP": 48}
        self.assertAlmostEqual(hoops.usage_rate(player, team, 240), 0.2)


@unittest.skipUnless(os.environ.get("SPORTS_LIVE"), "set SPORTS_LIVE=1 to download sportsdataverse boxes")
class Live(unittest.TestCase):
    def test_nba_download_matches_fixture(self):
        with open(hoops.box_path("nba", 2016), newline="") as f:
            t, o = hoops.season_totals(list(csv.DictReader(f)), "GS")
        self.assertEqual(t["PTS"], gsw()[0]["PTS"])

    def test_mens_college(self):
        with open(hoops.box_path("mbb", 2024), newline="") as f:
            t, o = hoops.season_totals(list(csv.DictReader(f)), "DUKE")
        r = hoops.team_ratings(t, o)
        self.assertTrue(55 < r["possessions_per_game"] < 80)


if __name__ == "__main__":
    unittest.main()
