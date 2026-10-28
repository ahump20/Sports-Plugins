"""Checks against sportsdataverse's published advanced box scores and Texas' official 2024 passing line."""
import gzip
import io
import os
import sys
import tempfile
import time
import unittest
import urllib.error
from contextlib import redirect_stderr
from unittest import mock

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import cfbfast  # noqa: E402

# Every play of Texas' 16 games in 2024, trimmed to the script's columns, from sportsdataverse's
# espn_cfb_pbp release (play_by_play_2024.csv, rebuilt 2026-10-27).
PBP = os.path.join(HERE, "fixtures", "pbp_2024_texas.csv.gz")
# Texas passing rows of the espn_cfb_player_box release (player_box_2024.csv).
BOX = os.path.join(HERE, "fixtures", "player_box_2024_texas_passing.csv")
MICHIGAN = {2}  # Texas 31, Michigan 12 in Ann Arbor, 2024 week 2 (game 401628347)


def rows():
    return list(cfbfast.read_csv(PBP))


def box():
    return list(cfbfast.read_csv(BOX, ("category", "athlete_id", "athlete_name")))


class GameMatchesPublishedBox(unittest.TestCase):
    # sportsdataverse espn_cfb_adv_team and espn_cfb_adv_situational, 2024, game 401628347.
    # The publisher rounds EPA totals to two decimals and leaves rates unrounded.
    def setUp(self):
        self.t = cfbfast.team_efficiency(rows(), weeks=MICHIGAN, season_type="REG")

    def test_texas_offense(self):
        tex = self.t["Texas Longhorns"]
        self.assertEqual(tex["off_plays"], 68)
        self.assertAlmostEqual(tex["off_epa"], 11.43, places=2)
        self.assertAlmostEqual(tex["off_success_rate"], 28 / 68, places=3)  # published 0.4117647
        self.assertEqual((tex["off_pass_plays"], tex["off_rush_plays"]), (36, 32))
        self.assertAlmostEqual(tex["off_pass_epa_per_play"], 14.64 / 36, places=3)
        self.assertAlmostEqual(tex["off_rush_epa_per_play"], -3.21 / 32, places=3)

    def test_michigan_offense_is_texas_defense(self):
        mich, tex = self.t["Michigan Wolverines"], self.t["Texas Longhorns"]
        self.assertEqual(mich["off_plays"], 54)
        self.assertAlmostEqual(mich["off_epa"], -5.21, places=2)
        self.assertAlmostEqual(mich["off_success_rate"], 22 / 54, places=3)  # published 0.4074074
        self.assertEqual(mich["off_epa_per_play"], tex["def_epa_per_play"])
        self.assertEqual(mich["def_plays"], tex["off_plays"])

    def test_ewers_passing_epa(self):  # espn_cfb_adv_passing: 36 dropbacks, EPA 14.64, SR 0.4722222
        s = cfbfast.player_summary(rows(), "Quinn Ewers", weeks=MICHIGAN, season_type="REG")
        self.assertEqual(s["dropbacks"], 36)
        self.assertAlmostEqual(s["passing_epa"], 14.64, places=2)
        self.assertAlmostEqual(s["dropback_success_rate"], 17 / 36, places=3)


class SeasonMatchesPublishedBox(unittest.TestCase):
    # Texas' 16 games in 2024 (13 regular season, 3 playoff), summed from the same published game boxes:
    # offense 1,108 plays, 92.49 EPA, 509 successes; defense 1,020 plays, -116.82 EPA, 415 successes;
    # passing 573 plays, 91.40 EPA. Each game total is rounded to 0.01, so sums agree within 0.08.
    def setUp(self):
        self.tex = cfbfast.team_efficiency(rows(), team="Texas")["Texas Longhorns"]

    def test_offense(self):
        self.assertEqual(self.tex["off_plays"], 1108)
        self.assertAlmostEqual(self.tex["off_epa"], 92.49, delta=0.08)
        self.assertEqual(self.tex["off_epa_per_play"], 0.083)
        self.assertAlmostEqual(self.tex["off_success_rate"], 509 / 1108, places=3)
        # 0.08 of rounding over 573 plays, plus the script's own rounding to three decimals
        self.assertAlmostEqual(self.tex["off_pass_epa_per_play"], 91.40 / 573, delta=0.08 / 573 + 0.0005)

    def test_defense(self):
        self.assertEqual(self.tex["def_plays"], 1020)
        self.assertAlmostEqual(self.tex["def_epa"], -116.82, delta=0.08)
        self.assertEqual(self.tex["def_epa_per_play"], -0.115)
        self.assertAlmostEqual(self.tex["def_success_rate"], 415 / 1020, places=3)

    def test_ewers_season_passing_epa(self):  # espn_cfb_adv_passing, 14 games: 473 dropbacks, 68.59 EPA
        s = cfbfast.player_summary(rows(), "4889929")
        self.assertEqual(s["dropbacks"], 473)
        self.assertAlmostEqual(s["passing_epa"], 68.59, delta=0.07)

    def test_regular_season_and_playoff_split(self):
        reg = cfbfast.team_efficiency(rows(), season_type="REG", team="251")["Texas Longhorns"]
        post = cfbfast.team_efficiency(rows(), season_type="POST", team="251")["Texas Longhorns"]
        self.assertEqual(reg["off_plays"] + post["off_plays"], 1108)


class OfficialPassingLine(unittest.TestCase):
    def test_ewers_2024_matches_ncaa(self):
        # cfbstats.com (official NCAA data): 293/445, 3,472 yds, 31 TD, 12 INT, rating 148.98, 14 games.
        line = cfbfast.passing_line(box(), "Quinn Ewers")
        self.assertEqual({k: line[k] for k in ("games", "cmp", "att", "yds", "td", "int")},
                         dict(games=14, cmp=293, att=445, yds=3472, td=31, int=12))
        self.assertEqual(line["ncaa_efficiency"], 148.98)

    def test_play_by_play_misses_plays_the_box_score_has(self):
        # ESPN's 2024 play-by-play has 443 Ewers attempts and 11 interceptions, two and one short of the
        # official line, which is why passing lines come from the box score.
        att = sum(1 for r in rows() if r["passer_player_id"] == "4889929" and cfbfast._flag(r, "pass")
                  and not cfbfast._flag(r, "sack") and cfbfast.is_scrimmage(r))
        self.assertEqual(att, 443)

    def test_line_follows_the_game_filter(self):
        line = cfbfast.passing_line(box(), "4889929", games={"401628347"})
        self.assertEqual((line["cmp"], line["att"], line["yds"], line["td"], line["int"]), (24, 36, 246, 3, 0))


def play(**kw):
    r = {"game_id": "1", "seasonType": "2", "week": "1", "pos_team_id": "1", "pos_team": "A Aces",
         "def_pos_team_id": "2", "def_pos_team": "Z Zeds", "homeTeamId": "1", "awayTeamId": "2",
         "homeTeamName": "A", "awayTeamName": "Z", "homeTeamAbbrev": "AA", "awayTeamAbbrev": "ZZ",
         "scrimmage_play": "true", "rush": "false", "pass": "true", "sack": "false", "EPA": "0.5",
         "passer_player_id": "", "passer_player_name": "", "rusher_player_id": "", "rusher_player_name": ""}
    r.update(kw)
    return r


class Filter(unittest.TestCase):
    def test_scrimmage_play_that_is_neither_run_nor_pass_counts_in_totals(self):
        # 2024 Texas-Kentucky: a fumble returned for a touchdown is a scrimmage play with no run or pass
        # flag; the publisher's offense total (-0.51) includes its -9.76 EPA.
        plays = [play(EPA="1.0"), play(rush="true", **{"pass": "false"}, EPA="-1.0"),
                 play(**{"pass": "false"}, EPA="-3.0")]
        a = cfbfast.team_efficiency(plays)["A Aces"]
        self.assertEqual((a["off_plays"], a["off_pass_plays"], a["off_rush_plays"]), (3, 1, 1))
        self.assertAlmostEqual(a["off_epa"], -3.0)

    def test_kneels_penalties_and_kicks_are_out(self):
        kept = [r for r in rows() if cfbfast.is_scrimmage(r)]
        self.assertTrue(kept)
        self.assertFalse({r["type.text"] for r in kept} & {"Penalty", "Kickoff", "Punt", "Field Goal Good",
                                                           "Timeout"})
        kneels = [r for r in rows() if r["type.text"] == "Rush" and not cfbfast._flag(r, "scrimmage_play")]
        self.assertEqual(len(kneels), 16)

    def test_success_is_epa_above_zero(self):
        plays = [play(EPA="0.0"), play(EPA="0.01"), play(EPA="-0.2")]
        self.assertEqual(cfbfast.team_efficiency(plays)["A Aces"]["off_success_rate"], 0.333)

    def test_weeks_mean_regular_season_weeks(self):
        plays = [play(EPA="1"), play(seasonType="3", EPA="5")]  # every bowl is week 1 too
        self.assertEqual(cfbfast.team_efficiency(plays, weeks={1})["A Aces"]["off_plays"], 1)


class Players(unittest.TestCase):
    def test_full_name_shared_by_two_players_is_refused(self):
        plays = [play(passer_player_id="10", passer_player_name="Sam Smith"),
                 play(passer_player_id="20", passer_player_name="Sam Smith", pos_team="B Bees")]
        with self.assertRaises(ValueError) as e:
            cfbfast.player_summary(plays, "Sam Smith")
        self.assertIn("10", str(e.exception))
        self.assertIn("20", str(e.exception))
        self.assertEqual(cfbfast.player_summary(plays, "20")["dropbacks"], 1)

    def test_unknown_player_is_refused_not_zero(self):
        with self.assertRaises(ValueError):
            cfbfast.player_summary(rows(), "quinn ewers")


class Cli(unittest.TestCase):
    def run_main(self, *argv):
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit) as e:
            cfbfast.main(list(argv))
        self.assertNotEqual(e.exception.code, 0)
        return err.getvalue()

    def test_unknown_team_names_the_ways_to_ask(self):
        self.assertIn("TEX", self.run_main("teams", "--pbp", PBP, "--team", "Longhorns"))

    def test_weeks_with_postseason_is_refused(self):
        self.assertIn("week 1", self.run_main("teams", "--pbp", PBP, "--weeks", "1-3", "--season-type", "POST"))

    def test_missing_columns_named(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("week,pos_team,def_pos_team,EPA\n1,A,Z,0.5\n")
        try:
            self.assertIn("scrimmage_play", self.run_main("teams", "--pbp", f.name))
        finally:
            os.remove(f.name)


class Cache(unittest.TestCase):
    HEADER = ",".join(cfbfast.BOX_COLUMNS) + ",extra\n"
    ROW = "1,2024,passing,7,Q B,251,10/20,150,1,0,x\n"

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(cfbfast, "CACHE", self.dir.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.dir.cleanup)
        self.season = time.localtime().tm_year + 1  # not finished, so its file still changes
        self.path = os.path.join(self.dir.name, f"player_box_{self.season}.csv.gz")

    def serve(self, body):
        return mock.patch("urllib.request.urlopen", return_value=io.BytesIO(body.encode()))

    def test_download_is_trimmed_to_the_columns_used(self):
        with self.serve(self.HEADER + self.ROW):
            path = cfbfast.box_path(self.season)
        with gzip.open(path, "rt") as f:
            header = f.readline().strip().split(",")
        self.assertEqual(tuple(header), cfbfast.BOX_COLUMNS)
        line = cfbfast.passing_line(cfbfast.read_csv(path, ("category",)), "7")
        self.assertEqual((line["cmp"], line["att"]), (10, 20))

    def test_finished_season_is_cached_for_good(self):
        path = os.path.join(self.dir.name, "player_box_2023.csv.gz")
        with gzip.open(path, "wt") as f:
            f.write(self.HEADER)
        t = time.mktime((2024, 6, 1, 0, 0, 0, 0, 0, -1))
        os.utime(path, (t, t))
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("re-downloaded 2023")):
            self.assertEqual(cfbfast.box_path(2023), path)

    def test_stale_cache_is_used_when_the_download_fails(self):
        with gzip.open(self.path, "wt") as f:
            f.write(self.HEADER)
        t = time.time() - 25 * 3600
        os.utime(self.path, (t, t))
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")), \
                redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cfbfast.box_path(self.season), self.path)
        self.assertIn("offline", err.getvalue())
        self.assertEqual(os.listdir(self.dir.name), [os.path.basename(self.path)])

    def test_changed_layout_never_replaces_the_cache(self):
        with self.serve("game_id,season\n1,2024\n"), self.assertRaises(RuntimeError) as e:
            cfbfast.box_path(self.season)
        self.assertIn("missing columns", str(e.exception))
        self.assertEqual(os.listdir(self.dir.name), [])

    def test_corrupt_cached_file_is_removed_with_a_message(self):
        body = ",".join(cfbfast.PBP_COLUMNS) + "\n" + "".join(
            ",".join(["1", "2031", "2", "1", "1", "A", "2", "Z", "1", "2", "A", "Z", "AA", "ZZ", "Rush",
                      "true", "true", "false", "false", f"{i / 7:.6f}", "", "", "", ""]) + "\n"
            for i in range(5000))
        data = gzip.compress(body.encode())
        path = os.path.join(self.dir.name, "play_by_play_2031.csv.gz")
        with open(path, "wb") as f:
            f.write(data[:len(data) * 2 // 3])  # header readable, body cut off
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit):
            cfbfast.main(["teams", "--season", "2031"])
        self.assertIn("rerun", err.getvalue())
        self.assertFalse(os.path.exists(path))

    def test_missing_season_is_a_clear_error(self):
        e404 = urllib.error.HTTPError("u", 404, "Not Found", None, None)
        with mock.patch("urllib.request.urlopen", side_effect=e404), self.assertRaises(RuntimeError) as e:
            cfbfast.pbp_path(2031)
        self.assertIn("2031", str(e.exception))


@unittest.skipUnless(os.environ.get("SPORTS_LIVE"), "set SPORTS_LIVE=1 to download sportsdataverse data")
class Live(unittest.TestCase):
    def test_texas_2024_season_from_the_release(self):  # same published totals as SeasonMatchesPublishedBox
        t = cfbfast.team_efficiency(cfbfast.read_csv(cfbfast.pbp_path(2024)), team="Texas")["Texas Longhorns"]
        self.assertEqual(t["off_plays"], 1108)
        self.assertAlmostEqual(t["off_epa"], 92.49, delta=0.08)
        self.assertAlmostEqual(t["off_success_rate"], 509 / 1108, places=3)

    def test_ewers_2024_official_line_from_the_release(self):
        line = cfbfast.passing_line(cfbfast.read_csv(cfbfast.box_path(2024), ("category",)), "4889929")
        self.assertEqual(line["ncaa_efficiency"], 148.98)


if __name__ == "__main__":
    unittest.main()
