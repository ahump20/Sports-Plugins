"""Checks against nflverse's own player stats and published passer ratings."""
import gzip
import io
import os
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr
from unittest import mock

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

    def test_josh_allen_2023_passing_epa(self):  # nflverse stats_player_week_2023 REG sum: 91.693
        s = nflfast.player_summary(nflfast.read_pbp(nflfast.pbp_path(2023)), "00-0034857")
        self.assertAlmostEqual(s["passing_epa"], 91.693, places=2)


class Ranking(unittest.TestCase):
    def test_zero_net_epa_sorts_between_positive_and_negative(self):
        play = lambda off, dfn, epa: {"season_type": "REG", "week": "1", "posteam": off,
                                      "defteam": dfn, "epa": str(epa), "pass": "1"}
        plays = [play("A", "Z", 1.0), play("B", "Z", 0.0), play("C", "Z", -1.0)]
        plays += [play("Z", team, 0.0) for team in "ABC"]  # every team needs a defensive snap
        t = nflfast.team_efficiency(plays, weeks={1})
        order = [k for k in t if k in ("A", "B", "C")]
        self.assertEqual(order, ["A", "B", "C"])


def play(**kw):
    r = {"season_type": "REG", "week": "1", "posteam": "A", "defteam": "Z", "play_type": "pass", "pass": "1",
         "rush": "0", "qb_dropback": "1", "epa": "0.5", "qb_epa": "0.5", "cpoe": "NA",
         "passer_player_id": "NA", "passer_player_name": "NA", "rusher_player_id": "NA", "rusher_player_name": "NA"}
    r.update(kw)
    return r


class PassingEpaFilter(unittest.TestCase):
    # nflverse sums qb_epa only where play_type is pass or qb_spike (nflfastR calculate_stats).
    # 2023: J.Allen's nullified two-point pass (2023_07_BUF_NE play 3782, play_type no_play, qb_epa 1.053)
    # made passing_epa 92.746 against nflverse's 91.693. 2025: J.Karty, blocked field goal, -2.985 against 0.
    def test_no_play_and_field_goal_rows_are_not_passing_epa(self):
        qb = dict(passer_player_id="00-1", passer_player_name="Q.Back")
        plays = [play(**qb, qb_epa="1.0", cpoe="10"),
                 play(**qb, play_type="no_play", qb_epa="1.053", cpoe="50"),
                 play(**qb, play_type="field_goal", qb_epa="-2.985", cpoe="-50")]
        s = nflfast.player_summary(plays, "00-1")
        self.assertAlmostEqual(s["passing_epa"], 1.0, places=3)
        self.assertEqual(s["cpoe"], 10.0)


class PlayerLookup(unittest.TestCase):
    def test_short_name_shared_by_two_players_is_refused(self):
        # 2024: B.Robinson is both Bijan Robinson (00-0038542) and Brian Robinson (00-0037746).
        run = {"play_type": "run", "pass": "0", "rush": "1", "qb_dropback": "0", "rusher_player_name": "B.Robinson"}
        plays = [play(**run, rusher_player_id="00-0038542", posteam="ATL"),
                 play(**run, rusher_player_id="00-0037746", posteam="WAS")]
        with self.assertRaises(ValueError) as e:
            nflfast.player_summary(plays, "B.Robinson")
        self.assertIn("00-0038542", str(e.exception))
        self.assertIn("00-0037746", str(e.exception))
        self.assertEqual(nflfast.player_summary(plays, "00-0037746")["player"], "B.Robinson")

    def test_unknown_player_is_refused_not_zero(self):
        with self.assertRaises(ValueError):
            nflfast.player_summary(rows(), "L.jackson")


class WeeksParsing(unittest.TestCase):
    def test_reversed_and_malformed_ranges_are_refused(self):
        for spec in ("9-1", "1-", "abc", "1,,3", "-3", "0"):
            with self.assertRaises(ValueError, msg=spec):
                nflfast.parse_weeks(spec)
        self.assertEqual(nflfast.parse_weeks(" 3 , 5-6 "), {3, 5, 6})


class EmptySelections(unittest.TestCase):
    def run_main(self, *argv):
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit) as e:
            nflfast.main(list(argv))
        self.assertNotEqual(e.exception.code, 0)
        return err.getvalue()

    def test_weeks_with_no_plays_is_an_error_not_empty_json(self):
        # Week 19+ is postseason; under the default REG filter it used to print {} silently.
        self.assertIn("no plays", self.run_main("teams", "--pbp", GAME, "--weeks", "19-22"))

    def test_missing_columns_named(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("week,posteam,defteam,epa,pass,rush\n1,BAL,KC,0.5,1,0\n")
        try:
            self.assertIn("season_type", self.run_main("teams", "--pbp", f.name))
        finally:
            os.remove(f.name)

    def test_empty_csv(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            pass
        try:
            self.run_main("teams", "--pbp", f.name)
        finally:
            os.remove(f.name)

    def test_zero_attempts_and_impossible_lines(self):
        self.run_main("rating", "--cmp", "0", "--att", "0", "--yds", "0", "--td", "0", "--int", "0")
        self.run_main("rating", "--cmp", "20", "--att", "10", "--yds", "50", "--td", "1", "--int", "0")
        self.run_main("rating", "--cmp", "5", "--att", "-10", "--yds", "50", "--td", "1", "--int", "0", "--ncaa")
        with self.assertRaises(ValueError):
            nflfast.ncaa_passing_efficiency(5, 10, 50, 6, 0)  # more touchdowns than completions

    def test_zero_rating_line(self):  # 5/20, 35 yds, 0 TD, 4 INT: every component clamps to 0
        self.assertEqual(nflfast.nfl_passer_rating(5, 20, 35, 0, 4), 0.0)


class Cache(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(nflfast, "CACHE", self.dir.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "play_by_play_2024.csv.gz")

    def write_cache(self, data, age_hours):
        with open(self.path, "wb") as f:
            f.write(data)
        t = os.path.getmtime(self.path) - age_hours * 3600
        os.utime(self.path, (t, t))

    def test_stale_cache_is_used_when_the_download_fails(self):
        self.write_cache(gzip.compress(b"a,b\n1,2\n"), age_hours=13)
        with mock.patch("urllib.request.urlretrieve", side_effect=urllib.error.URLError("offline")), \
                redirect_stderr(io.StringIO()) as err:
            self.assertEqual(nflfast.pbp_path(2024), self.path)
        self.assertIn("offline", err.getvalue())
        self.assertEqual(os.listdir(self.dir.name), ["play_by_play_2024.csv.gz"])

    def test_missing_season_is_a_clear_error(self):
        e404 = urllib.error.HTTPError("u", 404, "Not Found", None, None)
        with mock.patch("urllib.request.urlretrieve", side_effect=e404):
            with self.assertRaises(RuntimeError) as e:
                nflfast.pbp_path(2027)
        self.assertIn("2027", str(e.exception))

    def test_partial_or_corrupt_download_never_replaces_the_cache(self):
        good = gzip.compress(b"a,b\n1,2\n")
        self.write_cache(good, age_hours=13)

        def truncated(url, dest):
            with open(dest, "wb") as f:
                f.write(gzip.compress(b"a,b\n" + b"1,2\n" * 1000)[:40])
        with mock.patch("urllib.request.urlretrieve", side_effect=truncated), redirect_stderr(io.StringIO()):
            nflfast.pbp_path(2024)
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), good)
        self.assertFalse(os.path.exists(self.path + ".part"))

    def test_corrupt_cached_file_is_removed_with_a_message(self):
        body = "season_type,week,posteam,defteam,epa,pass,rush\n" + "".join(
            f"REG,1,A,Z,{i / 7:.6f},1,0\n" for i in range(5000))
        data = gzip.compress(body.encode())
        self.write_cache(data[:len(data) * 2 // 3], age_hours=0)  # header readable, body cut off
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit):
            nflfast.main(["teams", "--season", "2024"])
        self.assertIn("rerun", err.getvalue())
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
