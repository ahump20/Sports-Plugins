"""Checks against nflverse's own player stats and published passer ratings."""
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import nflfast  # noqa: E402

GAME = os.path.join(HERE, "fixtures", "pbp_2024_BAL_KC_week1.csv")  # 2024_01_BAL_KC, nflverse pbp


def rows():
    return list(nflfast.read_pbp(GAME))


class PlayerTotalsMatchNflverse(unittest.TestCase):
    # nflverse stats_player_week_2024, game 2024_01_BAL_KC
    def test_passing_epa(self):
        self.assertAlmostEqual(nflfast.player_summary(rows(), "00-0034796")["passing_epa"], -2.491, places=3)
        self.assertAlmostEqual(nflfast.player_summary(rows(), "00-0033873")["passing_epa"], 11.084, places=3)

    def test_rushing_epa(self):
        self.assertAlmostEqual(nflfast.player_summary(rows(), "00-0034796")["rushing_epa"], 5.008, places=3)
        self.assertAlmostEqual(nflfast.player_summary(rows(), "00-0032764")["rushing_epa"], 2.193, places=3)

    def test_cpoe_mean(self):  # nflverse passing_cpoe: Jackson -3.687, Mahomes 4.191
        self.assertAlmostEqual(nflfast.player_summary(rows(), "00-0034796")["cpoe"], -3.69, places=2)
        self.assertAlmostEqual(nflfast.player_summary(rows(), "00-0033873")["cpoe"], 4.19, places=2)


class Dropbacks(unittest.TestCase):
    def test_scrambles_count_as_dropbacks(self):  # 42 passes + 10 scrambles in this game
        lamar = nflfast.player_summary(rows(), "00-0034796")
        self.assertEqual(lamar["dropbacks"], 52)
        self.assertAlmostEqual(lamar["epa_per_dropback"], 0.005, places=3)


class TeamEfficiency(unittest.TestCase):
    def setUp(self):
        self.t = nflfast.team_efficiency(rows(), weeks={1})

    def test_both_teams_and_mirrored_sides(self):
        self.assertEqual(set(self.t), {"BAL", "KC"})
        self.assertEqual(self.t["KC"]["off_plays"], self.t["BAL"]["def_plays"])
        self.assertEqual(self.t["KC"]["off_epa_per_play"], self.t["BAL"]["def_epa_per_play"])

    def test_filter_drops_kneels_spikes_and_special_teams(self):
        kept = [r for r in rows() if nflfast.is_scrimmage(r)]
        self.assertTrue(kept)
        self.assertFalse(any(r["play_type"] in ("qb_kneel", "qb_spike", "punt", "kickoff", "field_goal",
                                                "extra_point") for r in kept))

    def test_penalty_plays_stay_in(self):
        # nflverse keeps pass/rush flags on plays nullified by penalty; this game has 10 of them.
        self.assertEqual(sum(1 for r in rows() if nflfast.is_scrimmage(r) and r["play_type"] == "no_play"), 10)


class PasserRating(unittest.TestCase):
    def test_rodgers_2011_nfl_record(self):  # 343/502, 4643 yds, 45 TD, 6 INT -> 122.5 (Packers.com)
        self.assertEqual(round(nflfast.nfl_passer_rating(343, 502, 4643, 45, 6), 1), 122.5)

    def test_perfect_rating_cap(self):
        self.assertAlmostEqual(nflfast.nfl_passer_rating(10, 10, 300, 5, 0), 158.333, places=3)

    def test_burrow_2019_ncaa_record(self):  # 402/527, 5671 yds, 60 TD, 6 INT -> 202.0 (Davey O'Brien Award)
        self.assertEqual(round(nflfast.ncaa_passing_efficiency(402, 527, 5671, 60, 6), 1), 202.0)


class Weeks(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(nflfast.parse_weeks("1-3,7"), {1, 2, 3, 7})
        self.assertIsNone(nflfast.parse_weeks(None))


@unittest.skipUnless(os.environ.get("SPORTS_LIVE"), "set SPORTS_LIVE=1 to download nflverse data")
class Live(unittest.TestCase):
    def test_lamar_2024_season_passing_epa(self):  # nflverse stats_player_week_2024 REG sum: 172.279
        s = nflfast.player_summary(nflfast.read_pbp(nflfast.pbp_path(2024)), "00-0034796")
        self.assertAlmostEqual(s["passing_epa"], 172.279, places=2)


if __name__ == "__main__":
    unittest.main()


class Ranking(unittest.TestCase):
    def test_zero_net_epa_sorts_between_positive_and_negative(self):
        play = lambda off, dfn, epa: {"season_type": "REG", "week": "1", "posteam": off,
                                      "defteam": dfn, "epa": str(epa), "pass": "1"}
        plays = [play("A", "Z", 1.0), play("B", "Z", 0.0), play("C", "Z", -1.0)]
        plays += [play("Z", team, 0.0) for team in "ABC"]  # every team needs a defensive snap
        t = nflfast.team_efficiency(plays, weeks={1})
        order = [k for k in t if k in ("A", "B", "C")]
        self.assertEqual(order, ["A", "B", "C"])
