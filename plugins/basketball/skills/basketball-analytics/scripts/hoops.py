#!/usr/bin/env python3
"""Basketball efficiency: possessions, pace, ratings, Four Factors, TS%, eFG%, usage. Stdlib only.

Usage:
  hoops.py player --stats '{"FG":805,"FGA":1598,"3P":402,"FT":363,"FTA":400,"PTS":2375}'
  hoops.py team   --league nba --season 2016 --team GS     # sums ESPN box scores (sportsdataverse releases)
  hoops.py team   --league mbb --season 2024 --team DUKE
  hoops.py team   --boxes FILE --team GS                     # a local team-box CSV in the same format
Seasons are named by the year they end: 2016 is 2015-16.
"""
import argparse
import csv
import io
import json
import os
import sys
import time
import urllib.request

BOX_URL = {
    "nba": "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
           "espn_nba_team_boxscores/team_box_{season}.csv",
    "mbb": "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
           "espn_mens_college_basketball_team_boxscores/team_box_{season}.csv",
    "wbb": "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
           "espn_womens_college_basketball_team_boxscores/team_box_{season}.csv",
}
CACHE = os.path.expanduser("~/.cache/sports-plugins/sportsdataverse")
_COLS = {"FG": "field_goals_made", "FGA": "field_goals_attempted", "3P": "three_point_field_goals_made",
         "3PA": "three_point_field_goals_attempted", "FT": "free_throws_made",
         "FTA": "free_throws_attempted", "ORB": "offensive_rebounds", "DRB": "defensive_rebounds",
         "AST": "assists", "STL": "steals", "BLK": "blocks", "TOV": "turnovers", "PF": "fouls"}
REGULAR_SEASON = "2"


def _g(s, k):
    return float(s.get(k, 0) or 0)


def ts_pct(s):
    """True shooting: points per two shooting possessions; 0.44 approximates FTA that end a possession."""
    den = 2 * (_g(s, "FGA") + 0.44 * _g(s, "FTA"))
    return _g(s, "PTS") / den if den else 0.0


def efg_pct(s):
    """Effective FG%: a made three counts 1.5 field goals."""
    return (_g(s, "FG") + 0.5 * _g(s, "3P")) / _g(s, "FGA") if _g(s, "FGA") else 0.0


def _half(t, o):
    orb_share = _g(t, "ORB") / (_g(t, "ORB") + _g(o, "DRB"))
    return (_g(t, "FGA") + 0.4 * _g(t, "FTA") - 1.07 * orb_share * (_g(t, "FGA") - _g(t, "FG"))
            + _g(t, "TOV"))


def possessions(t, o):
    """Basketball-Reference's estimate: the average of both teams' possession counts."""
    return 0.5 * (_half(t, o) + _half(o, t))


def simple_possessions(t, ft_weight=0.475):
    """One-team estimate, FGA - ORB + TOV + 0.475*FTA (KenPom's weight); no opponent needed."""
    return _g(t, "FGA") - _g(t, "ORB") + _g(t, "TOV") + ft_weight * _g(t, "FTA")


def four_factors(t, o):
    """Dean Oliver's Four Factors for the team in `t` (offense) given opponent `o`."""
    return {
        "eFG%": efg_pct(t),
        "TOV%": _g(t, "TOV") / (_g(t, "FGA") + 0.44 * _g(t, "FTA") + _g(t, "TOV")),
        "ORB%": _g(t, "ORB") / (_g(t, "ORB") + _g(o, "DRB")),
        "FT/FGA": _g(t, "FT") / _g(t, "FGA"),
    }


def team_ratings(t, o):
    """Per-100-possession ratings. possessions_per_game includes overtime; Basketball-Reference's
    Pace rescales by minutes played, so it runs slightly lower for teams that played overtime."""
    poss = possessions(t, o)
    games = _g(t, "G") or 1
    out = {"games": int(games), "possessions": round(poss, 1),
           "possessions_per_game": round(poss / games, 1),
           "ORtg": round(100 * _g(t, "PTS") / poss, 2), "DRtg": round(100 * _g(o, "PTS") / poss, 2)}
    out["NRtg"] = round(out["ORtg"] - out["DRtg"], 2)
    out["offense"] = {k: round(v, 3) for k, v in four_factors(t, o).items()}
    out["defense"] = {k: round(v, 3) for k, v in four_factors(o, t).items()}
    return out


def usage_rate(p, t, team_minutes):
    """Share of team plays a player used while on the floor (Basketball-Reference form)."""
    used = _g(p, "FGA") + 0.44 * _g(p, "FTA") + _g(p, "TOV")
    team_used = _g(t, "FGA") + 0.44 * _g(t, "FTA") + _g(t, "TOV")
    return used * (team_minutes / 5) / (_g(p, "MP") * team_used)


def player_line(s):
    out = {"TS%": round(ts_pct(s), 3), "eFG%": round(efg_pct(s), 3)}
    if _g(s, "3PA") and _g(s, "FGA"):
        out["3PAr"] = round(_g(s, "3PA") / _g(s, "FGA"), 3)
    if _g(s, "FGA"):
        out["FTr"] = round(_g(s, "FTA") / _g(s, "FGA"), 3)
    return out


def box_path(league, season, max_age_hours=12):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{league}_team_box_{int(season)}.csv")
    if not os.path.exists(path) or time.time() - os.path.getmtime(path) > max_age_hours * 3600:
        tmp = path + ".part"
        urllib.request.urlretrieve(BOX_URL[league].format(season=int(season)), tmp)
        os.replace(tmp, path)
    return path


def season_totals(rows, team, season_type=REGULAR_SEASON):
    """Sum a team's and its opponents' box scores. Pairs rows by game so the opponent's
    rebounds and turnovers come from the opponent's own line."""
    rows = [r for r in rows if r.get("season_type") == season_type]
    by_game = {}
    for r in rows:
        by_game.setdefault(r["game_id"], {})[r["team_abbreviation"]] = r
    t, o = {"G": 0, "PTS": 0}, {"PTS": 0}
    for game in by_game.values():
        if team not in game or len(game) != 2:
            continue
        mine = game[team]
        theirs = next(v for k, v in game.items() if k != team)
        t["G"] += 1
        for side, src in ((t, mine), (o, theirs)):
            side["PTS"] += int(src["team_score"])
            for k, col in _COLS.items():
                side[k] = side.get(k, 0) + int(float(src.get(col) or 0))
    if not t["G"]:
        raise LookupError(f"no {team} games found; team_abbreviation is ESPN's (GS, NY, SA, DUKE ...)")
    return t, o


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["player", "team"])
    p.add_argument("--stats")
    p.add_argument("--league", choices=sorted(BOX_URL), default="nba")
    p.add_argument("--season", type=int)
    p.add_argument("--team")
    p.add_argument("--boxes")
    p.add_argument("--postseason", action="store_true")
    a = p.parse_args(argv)
    if a.mode == "player":
        if not a.stats:
            p.error("player needs --stats")
        print(json.dumps(player_line(json.loads(a.stats)), indent=2))
        return 0
    if not a.team or not (a.boxes or a.season):
        p.error("team needs --team and --season (or --boxes)")
    with open(a.boxes or box_path(a.league, a.season), newline="") as f:
        rows = list(csv.DictReader(f))
    t, o = season_totals(rows, a.team, "3" if a.postseason else REGULAR_SEASON)
    print(json.dumps(team_ratings(t, o), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
