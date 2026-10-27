"""Checks against Basketball-Reference's published numbers."""
import contextlib
import csv
import io
import os
import socket
import sys
import tempfile
import time
import unittest
import urllib.error
from unittest import mock

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

    def test_warriors_2016_turnovers_include_team_turnovers(self):
        # Basketball-Reference team totals: TOV 1245, opponent TOV 1185. ESPN's `turnovers` column
        # leaves out team turnovers (shot-clock and 8-second violations); `total_turnovers` has them.
        t, o = gsw()
        self.assertEqual((t["TOV"], o["TOV"]), (1245, 1185))

    def test_warriors_2016_ratings_match_bbref(self):
        # Basketball-Reference team page: Off Rtg 114.5, Def Rtg 103.8, Net Rtg +10.7.
        r = hoops.team_ratings(*gsw())
        self.assertAlmostEqual(r["ORtg"], 114.5, delta=0.05)
        self.assertAlmostEqual(r["DRtg"], 103.8, delta=0.05)
        self.assertAlmostEqual(r["NRtg"], 10.7, delta=0.05)

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


def box(game, team, opp, team_id=None, season_type="2", tov="10", total_tov="12", **cols):
    row = {"game_id": game, "season_type": season_type, "team_abbreviation": team,
           "opponent_team_abbreviation": opp, "team_score": "100", "field_goals_made": "40",
           "field_goals_attempted": "85", "three_point_field_goals_made": "10",
           "three_point_field_goals_attempted": "30", "free_throws_made": "10",
           "free_throws_attempted": "15", "offensive_rebounds": "10", "defensive_rebounds": "30",
           "turnovers": tov, "total_turnovers": total_tov}
    if team_id is not None:
        row["team_id"] = team_id
        row["team_display_name"] = cols.pop("name", team)
        row["team_location"] = cols.pop("location", team)
    row.update(cols)
    return row


class TeamRows(unittest.TestCase):
    def test_blank_total_turnovers_falls_back_to_turnovers(self):
        # One CHI row in ESPN's 2025-26 NBA file has total_turnovers blank and turnovers 19.
        rows = [box("1", "CHI", "ORL", total_tov=""), box("1", "ORL", "CHI")]
        t, o = hoops.season_totals(rows, "CHI")
        self.assertEqual((t["TOV"], o["TOV"]), (10, 12))

    def test_nba_cup_final_is_not_a_regular_season_game(self):
        # ESPN files the NBA Cup final (2023-24 LAL-IND, game 401607495) as season_type 2;
        # Basketball-Reference and the NBA leave it out of regular-season totals (LAL: 82 games).
        rows = [box("401607495", "LAL", "IND"), box("401607495", "IND", "LAL"),
                box("2", "LAL", "DEN"), box("2", "DEN", "LAL")]
        t, _ = hoops.season_totals(rows, "LAL")
        self.assertEqual(t["G"], 1)

    def test_shared_abbreviation_does_not_merge_two_schools(self):
        # ESPN's 2023-24 men's file uses FSU for Florida State (33 games) and Framingham State (1).
        rows = [box("1", "FSU", "DUKE", team_id="52", name="Florida State Seminoles"),
                box("1", "DUKE", "FSU", team_id="150"),
                box("2", "FSU", "UNC", team_id="52", name="Florida State Seminoles"),
                box("2", "UNC", "FSU", team_id="153"),
                box("3", "FSU", "WPI", team_id="126956", name="Framingham State Rams"),
                box("3", "WPI", "FSU", team_id="999")]
        with contextlib.redirect_stderr(io.StringIO()) as err:
            t, _ = hoops.season_totals(rows, "FSU")
        self.assertEqual(t["G"], 2)
        self.assertIn("Framingham State", err.getvalue())

    def test_team_names_people_type(self):
        t, _ = hoops.season_totals(list(csv.DictReader(open(GSW_BOXES, newline=""))), "GSW")
        self.assertEqual(t["G"], 82)
        t, _ = hoops.season_totals(list(csv.DictReader(open(GSW_BOXES, newline=""))), "gs")
        self.assertEqual(t["G"], 82)
        rows = [box("1", "DUKE", "UNC", team_id="150", name="Duke Blue Devils", location="Duke"),
                box("1", "UNC", "DUKE", team_id="153")]
        for name in ("duke", "Duke Blue Devils", "150"):
            self.assertEqual(hoops.season_totals(rows, name)[0]["G"], 1)

    def test_all_games_adds_postseason(self):
        rows = [box("1", "GS", "LAL"), box("1", "LAL", "GS"),
                box("2", "GS", "HOU", season_type="3"), box("2", "HOU", "GS", season_type="3")]
        self.assertEqual(hoops.season_totals(rows, "GS", ("2", "3"))[0]["G"], 2)

    def test_blank_rebounds_raise_a_clear_error(self):
        rows = [box("1", "GS", "LAL", offensive_rebounds="", defensive_rebounds=""),
                box("1", "LAL", "GS", offensive_rebounds="", defensive_rebounds="")]
        with self.assertRaisesRegex(ValueError, "rebound"):
            hoops.team_ratings(*hoops.season_totals(rows, "GS"))


class Cli(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = hoops.main(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def test_unknown_team_is_an_error_message_not_a_traceback(self):
        code, _, err = self.run_cli("team", "--boxes", GSW_BOXES, "--team", "XYZ")
        self.assertNotEqual(code, 0)
        self.assertIn("XYZ", err)
        self.assertNotIn("Traceback", err)

    def test_empty_csv_is_an_error_message(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("")
        code, _, err = self.run_cli("team", "--boxes", f.name, "--team", "GS")
        os.unlink(f.name)
        self.assertNotEqual(code, 0)
        self.assertIn("no box scores", err)

    def test_missing_season_file_is_an_error_message(self):
        def gone(url, path):
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hoops, "CACHE", d), \
                mock.patch.object(hoops.urllib.request, "urlretrieve", gone):
            code, _, err = self.run_cli("team", "--league", "nba", "--season", "2030", "--team", "GS")
            self.assertEqual(os.listdir(d), [])
        self.assertNotEqual(code, 0)
        self.assertIn("2030", err)

    def test_stale_cache_is_used_when_the_download_fails(self):
        def offline(url, path):
            raise urllib.error.URLError("network is unreachable")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hoops, "CACHE", d), \
                mock.patch.object(hoops.urllib.request, "urlretrieve", offline):
            cached = os.path.join(d, "nba_team_box_2016.csv")
            with open(GSW_BOXES) as src, open(cached, "w") as dst:
                dst.write(src.read())
            os.utime(cached, (0, 0))
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(hoops.box_path("nba", 2016), cached)

    def test_finished_season_is_cached_for_good(self):
        def refetch(url, path):
            raise AssertionError(f"re-downloaded {url}")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hoops, "CACHE", d), \
                mock.patch.object(hoops.urllib.request, "urlretrieve", refetch):
            cached = os.path.join(d, "nba_team_box_2016.csv")
            with open(GSW_BOXES) as src, open(cached, "w") as dst:
                dst.write(src.read())
            t = time.mktime((2016, 9, 1, 0, 0, 0, 0, 0, -1))  # after the 2016 Finals
            os.utime(cached, (t, t))
            self.assertEqual(hoops.box_path("nba", 2016), cached)

    def test_season_in_progress_refreshes_after_12_hours(self):
        season = time.localtime().tm_year + 1  # 2027 is 2026-27: not over until June 2027
        calls = []

        def fresh(url, path):
            calls.append(url)
            with open(GSW_BOXES) as src, open(path, "w") as dst:
                dst.write(src.read())
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hoops, "CACHE", d), \
                mock.patch.object(hoops.urllib.request, "urlretrieve", fresh):
            cached = os.path.join(d, f"nba_team_box_{season}.csv")
            with open(GSW_BOXES) as src, open(cached, "w") as dst:
                dst.write(src.read())
            t = time.time() - 13 * 3600
            os.utime(cached, (t, t))
            hoops.box_path("nba", season)
        self.assertEqual(len(calls), 1)

    def test_corrupt_download_does_not_replace_the_cache(self):
        def html(url, path):
            with open(path, "w") as f:
                f.write("<html>rate limited</html>")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hoops, "CACHE", d), \
                mock.patch.object(hoops.urllib.request, "urlretrieve", html):
            with self.assertRaisesRegex(OSError, "not a sportsdataverse CSV"):
                hoops.box_path("nba", 2016)
            self.assertEqual(os.listdir(d), [])

    def test_usage_from_the_command_line(self):
        code, out, _ = self.run_cli("player", "--stats", '{"FGA":16,"FTA":4,"TO":2.4,"MP":48}',
                                    "--team-stats", '{"FGA":80,"FTA":20,"TOV":12,"MP":240}')
        self.assertEqual(code, 0)
        self.assertIn('"USG%": 0.2', out)

    def test_bad_json_is_an_error_message(self):
        code, _, err = self.run_cli("player", "--stats", "{FG: 5}")
        self.assertNotEqual(code, 0)
        self.assertNotIn("Traceback", err)


class PlayerKeys(unittest.TestCase):
    def test_box_score_spellings_are_accepted(self):
        # nba_api and most box scores say FGM/FG3M/FTM; a silent 0 for FG gave eFG% .126 for Curry.
        alt = {"FGM": 805, "FGA": 1598, "FG3M": 402, "FTM": 363, "FTA": 400, "PTS": 2375}
        self.assertEqual(hoops.player_line(hoops.normalize_stats(alt))["eFG%"], 0.63)
        lower = {"fg": 805, "fga": 1598, "3pm": 402, "ft": 363, "fta": 400, "pts": 2375}
        self.assertEqual(hoops.player_line(hoops.normalize_stats(lower))["TS%"], 0.669)

    def test_unknown_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "FG_MADE"):
            hoops.normalize_stats({"FG_MADE": 805, "FGA": 1598})

    def test_points_derived_when_missing(self):
        s = hoops.normalize_stats({"FG": 805, "FGA": 1598, "3P": 402, "FT": 363, "FTA": 400})
        self.assertEqual(s["PTS"], 2375)

    def test_jokic_2024(self):
        # Basketball-Reference 2023-24 totals: 822 FG, 1411 FGA, 83 3P, 358 FT, 438 FTA, 2085 PTS; eFG% .612.
        s = {"FG": 822, "FGA": 1411, "3P": 83, "FT": 358, "FTA": 438, "PTS": 2085}
        self.assertEqual(round(hoops.efg_pct(s), 3), 0.612)

    def test_no_attempts(self):
        self.assertEqual(hoops.player_line({"PTS": 0}), {"TS%": 0.0, "eFG%": 0.0})


class Usage(unittest.TestCase):
    def test_usage_equals_share_when_player_plays_every_minute(self):
        team = {"FGA": 80, "FTA": 20, "TOV": 12}
        player = {"FGA": 16, "FTA": 4, "TOV": 2.4, "MP": 48}
        self.assertAlmostEqual(hoops.usage_rate(player, team, 240), 0.2)


class BadInput(unittest.TestCase):
    run_cli = Cli.run_cli

    def test_json_that_is_not_an_object_is_an_error_message(self):
        for stats in ("[1]", "5", '"FG"'):
            code, _, err = self.run_cli("player", "--stats", stats)
            self.assertNotEqual(code, 0, stats)
            self.assertNotIn("Traceback", err)
            self.assertIn("object", err)

    def test_values_that_are_not_finite_numbers_are_rejected(self):
        for value in ("NaN", "Infinity", "1e999", "[1]", "true"):
            code, _, err = self.run_cli("player", "--stats", '{"FG": %s, "FGA": 10}' % value)
            self.assertNotEqual(code, 0, value)
            self.assertIn("FG", err)

    def test_usage_without_team_possessions_is_an_error_message(self):  # divided by zero
        code, _, err = self.run_cli("player", "--stats", '{"FGA":16,"MP":48}', "--team-stats", '{"MP":240}')
        self.assertNotEqual(code, 0)
        self.assertNotIn("Traceback", err)
        self.assertIn("FGA", err)

    def test_college_abbreviation_is_not_read_as_an_nba_alias(self):
        # ESPN's men's file: UTA is UT Arlington, UTAH is Utah. The NBA alias UTA -> UTAH took Utah.
        rows = [box("1", "UTA", "TCU", team_id="250", name="UT Arlington Mavericks"),
                box("1", "TCU", "UTA", team_id="2628"),
                box("2", "UTAH", "BYU", team_id="254", name="Utah Utes"),
                box("2", "BYU", "UTAH", team_id="252")]
        self.assertEqual(hoops.resolve_team(rows, "UTA"), ("250", "UT Arlington Mavericks"))
        nba = [box("3", "UTAH", "DEN", team_id="26", name="Utah Jazz"), box("3", "DEN", "UTAH", team_id="7")]
        self.assertEqual(hoops.resolve_team(nba, "UTA")[1], "Utah Jazz")


class Download(unittest.TestCase):
    def test_download_cannot_hang(self):
        seen = []

        def fetch(url, path):
            seen.append(socket.getdefaulttimeout())
            with open(GSW_BOXES) as src, open(path, "w") as dst:
                dst.write(src.read())
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hoops, "CACHE", d), \
                mock.patch.object(hoops.urllib.request, "urlretrieve", fetch):
            hoops.box_path("nba", 2016)
        self.assertIsNotNone(seen[0])
        self.assertIsNone(socket.getdefaulttimeout())


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
