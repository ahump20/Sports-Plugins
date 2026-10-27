#!/usr/bin/env python3
"""Basketball efficiency: possessions, pace, ratings, Four Factors, TS%, eFG%, usage. Stdlib only.

Usage:
  hoops.py player --stats '{"FG":805,"FGA":1598,"3P":402,"FT":363,"FTA":400,"PTS":2375}'
  hoops.py player --stats '{"FGA":1598,"FTA":400,"TOV":262,"MP":2700}' --team-stats '{"FGA":7159,"FTA":1790,"TOV":1245,"MP":19830}'
  hoops.py team   --league nba --season 2016 --team GS     # sums ESPN box scores (sportsdataverse releases)
  hoops.py team   --league mbb --season 2024 --team DUKE
  hoops.py team   --boxes FILE --team GS                     # a local team-box CSV in the same format
Seasons are named by the year they end: 2016 is 2015-16. --team takes ESPN's abbreviation (GS, DUKE),
Basketball-Reference's (GSW), the school or city ("Duke"), the full name or ESPN's team_id, in any case.
"""
import argparse
import collections
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

BOX_URL = {
    "nba": "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
           "espn_nba_team_boxscores/team_box_{season}.csv",
    "mbb": "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
           "espn_mens_college_basketball_team_boxscores/team_box_{season}.csv",
    "wbb": "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
           "espn_womens_college_basketball_team_boxscores/team_box_{season}.csv",
}
NBA_SCHEDULE_URL = ("https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
                    "espn_nba_schedules/nba_schedule_{season}.csv")
CACHE = os.path.expanduser("~/.cache/sports-plugins/sportsdataverse")
# total_turnovers includes team turnovers (shot-clock and 8-second violations), as Basketball-Reference's
# TOV does; plain `turnovers` is the players' sum. Blank total_turnovers falls back to turnovers.
_COLS = {"FG": "field_goals_made", "FGA": "field_goals_attempted", "3P": "three_point_field_goals_made",
         "3PA": "three_point_field_goals_attempted", "FT": "free_throws_made",
         "FTA": "free_throws_attempted", "ORB": "offensive_rebounds", "DRB": "defensive_rebounds",
         "AST": "assists", "STL": "steals", "BLK": "blocks", "TOV": "total_turnovers", "PF": "fouls"}
_REQUIRED = ("game_id", "season_type", "team_abbreviation", "team_score")
REGULAR_SEASON = "2"
POSTSEASON = "3"
# ESPN files the NBA Cup final as a regular-season game; it counts in no season totals. Later finals
# are read from ESPN's schedule (type CC); these cover --boxes files and an unreachable schedule.
NBA_CUP_FINALS = {"401607495", "401734908", "401809839"}  # 2023-24, 2024-25, 2025-26
# Basketball-Reference / NBA.com abbreviations that ESPN spells differently.
NBA_ALIASES = {"GSW": "GS", "NYK": "NY", "SAS": "SA", "NOP": "NO", "NOH": "NO", "UTA": "UTAH",
               "WAS": "WSH", "PHO": "PHX", "BRK": "BKN", "CHO": "CHA", "NJN": "NJ"}
_STAT_ALIASES = {"FGM": "FG", "3PM": "3P", "FG3M": "3P", "3FG": "3P", "3FGM": "3P", "FG3A": "3PA",
                 "3FGA": "3PA", "FTM": "FT", "TO": "TOV", "MIN": "MP", "OREB": "ORB", "DREB": "DRB"}
_STATS = {"FG", "FGA", "3P", "3PA", "FT", "FTA", "PTS", "TOV", "MP", "ORB", "DRB", "AST", "STL", "BLK",
          "PF", "G"}


def _g(s, k):
    return float(s.get(k, 0) or 0)


def ts_pct(s):
    """True shooting: points per two shooting possessions; 0.44 approximates FTA that end a possession."""
    den = 2 * (_g(s, "FGA") + 0.44 * _g(s, "FTA"))
    return _g(s, "PTS") / den if den else 0.0


def efg_pct(s):
    """Effective FG%: a made three counts 1.5 field goals."""
    return (_g(s, "FG") + 0.5 * _g(s, "3P")) / _g(s, "FGA") if _g(s, "FGA") else 0.0


def _orb_share(t, o):
    available = _g(t, "ORB") + _g(o, "DRB")
    if not available:
        raise ValueError("offensive_rebounds and defensive_rebounds are blank or zero in every game; "
                         "possessions and ORB% need them")
    return _g(t, "ORB") / available


def _half(t, o):
    orb_share = _orb_share(t, o)
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
        "ORB%": _orb_share(t, o),
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


def normalize_stats(s):
    """Accept box-score spellings (FGM, FG3M, 3PM, FTM, TO, MIN, any case); reject keys we can't place,
    because an unread key would silently count as 0. Derive PTS when it is missing."""
    out, unknown = {}, []
    for k, v in s.items():
        key = str(k).strip().upper()
        key = _STAT_ALIASES.get(key, key)
        if key not in _STATS:
            unknown.append(k)
            continue
        out[key] = float(v or 0)
    if unknown:
        raise ValueError(f"unknown stat keys {unknown}; use {sorted(_STATS)} (FGM, FG3M, FTM, TO also work)")
    if "PTS" not in out and "FG" in out:
        out["PTS"] = 2 * out["FG"] + out.get("3P", 0) + out.get("FT", 0)
    return out


def player_line(s):
    out = {"TS%": round(ts_pct(s), 3), "eFG%": round(efg_pct(s), 3)}
    if _g(s, "3PA") and _g(s, "FGA"):
        out["3PAr"] = round(_g(s, "3PA") / _g(s, "FGA"), 3)
    if _g(s, "FGA"):
        out["FTr"] = round(_g(s, "FTA") / _g(s, "FGA"), 3)
    return out


def _check_csv(path, columns):
    with open(path, newline="") as f:
        header = next(csv.reader(f), [])
    missing = [c for c in columns if c not in header]
    if missing:
        raise ValueError(f"{path} is not a sportsdataverse CSV (missing {', '.join(missing)})")


def _fetch(url, path, columns, max_age_hours=12):
    """Download url to path unless a cached copy is fresh. A failed or bad download never replaces the
    cache; if a stale copy exists it is used, with a warning."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) <= max_age_hours * 3600:
        return path
    tmp = path + ".part"
    try:
        urllib.request.urlretrieve(url, tmp)
        _check_csv(tmp, columns)
    except (OSError, ValueError) as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        if isinstance(e, urllib.error.HTTPError) and e.code == 404:
            raise LookupError(f"{url} does not exist (HTTP 404); that season isn't published") from None
        if os.path.exists(path):
            print(f"warning: download failed ({e}); using the cached copy from "
                  f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(path)))}", file=sys.stderr)
            return path
        raise OSError(f"could not download {url}: {e}") from None
    os.replace(tmp, path)
    return path


def box_path(league, season, max_age_hours=12):
    path = os.path.join(CACHE, f"{league}_team_box_{int(season)}.csv")
    return _fetch(BOX_URL[league].format(season=int(season)), path, _REQUIRED, max_age_hours)


def nba_excluded_games(season):
    """Regular-season NBA games that count in no season totals: the NBA Cup final (since 2023-24)."""
    games = set(NBA_CUP_FINALS)
    if int(season) < 2024:
        return games
    try:
        path = _fetch(NBA_SCHEDULE_URL.format(season=int(season)),
                      os.path.join(CACHE, f"nba_schedule_{int(season)}.csv"), ("game_id", "type_abbreviation"))
        with open(path, newline="") as f:
            games |= {r["game_id"] for r in csv.DictReader(f) if r.get("type_abbreviation") == "CC"}
    except (OSError, LookupError, ValueError) as e:
        print(f"warning: no NBA schedule ({e}); an NBA Cup final after 2025-26 may be counted", file=sys.stderr)
    return games


def _key(r):
    return r.get("team_id") or r["team_abbreviation"]


def _num(v):
    return int(float(v or 0))


def resolve_team(rows, team):
    """Return the row key (ESPN team_id, else abbreviation) and display name for what the user typed.
    ESPN reuses abbreviations across schools (FSU is Florida State and Framingham State); when several
    teams match, take the one with the most games and say so."""
    q = team.strip().upper()
    q = NBA_ALIASES.get(q, q)
    games, names = collections.Counter(), {}
    for r in rows:
        fields = ("team_abbreviation", "team_id", "team_location", "team_display_name",
                  "team_short_display_name", "team_name")
        if any((r.get(c) or "").strip().upper() == q for c in fields):
            games[_key(r)] += 1
            names[_key(r)] = r.get("team_display_name") or r["team_abbreviation"]
    if not games:
        raise LookupError(f"no team matches {team!r}; use ESPN's abbreviation (GS, NY, SA, DUKE ...), "
                          f"the school or city, or ESPN's team_id")
    (best, _), *others = games.most_common()
    if others:
        print(f"warning: {team!r} also matches " + ", ".join(f"{names[k]} (--team {k})" for k, _ in others)
              + f"; using {names[best]}", file=sys.stderr)
    return best, names[best]


def season_totals(rows, team, season_type=REGULAR_SEASON, exclude=frozenset(NBA_CUP_FINALS)):
    """Sum a team's and its opponents' box scores. Pairs rows by game so the opponent's
    rebounds and turnovers come from the opponent's own line. season_type is one code or several."""
    if not rows:
        raise LookupError("no box scores in the file")
    types = {season_type} if isinstance(season_type, str) else set(season_type)
    key, name = resolve_team(rows, team)
    by_game = {}
    for r in rows:
        if r.get("season_type") in types and r["game_id"] not in exclude:
            by_game.setdefault(r["game_id"], {})[_key(r)] = r
    t, o = {"G": 0, "PTS": 0}, {"PTS": 0}
    for game in by_game.values():
        if key not in game or len(game) != 2:
            continue
        mine = game[key]
        theirs = next(v for k, v in game.items() if k != key)
        t["G"] += 1
        for side, src in ((t, mine), (o, theirs)):
            side["PTS"] += _num(src["team_score"])
            for k, col in _COLS.items():
                v = src.get(col)
                if k == "TOV" and (v or "") == "":
                    v = src.get("turnovers")
                side[k] = side.get(k, 0) + _num(v)
    if not t["G"]:
        raise LookupError(f"{name} has no games with season_type {'/'.join(sorted(types))} "
                          f"(2 regular season, 3 postseason)")
    if not (t["ORB"] + o["DRB"]) or not (o["ORB"] + t["DRB"]):
        raise ValueError(f"{name}: offensive_rebounds/defensive_rebounds are blank or zero in every game")
    return t, o


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["player", "team"])
    p.add_argument("--stats")
    p.add_argument("--team-stats", help="player mode: team FGA, FTA, TOV and MP (team minutes) for usage")
    p.add_argument("--league", choices=sorted(BOX_URL), default="nba")
    p.add_argument("--season", type=int)
    p.add_argument("--team")
    p.add_argument("--boxes")
    p.add_argument("--postseason", action="store_true", help="postseason games only")
    p.add_argument("--all", action="store_true",
                   help="regular season plus postseason (how Sports-Reference and KenPom total a college season)")
    a = p.parse_args(argv)
    try:
        if a.mode == "player":
            if not a.stats:
                p.error("player needs --stats")
            stats = normalize_stats(json.loads(a.stats))
            out = player_line(stats)
            if a.team_stats:
                team = normalize_stats(json.loads(a.team_stats))
                if not (stats.get("MP") and team.get("MP")):
                    p.error("usage needs MP in --stats and team minutes (MP) in --team-stats")
                out["USG%"] = round(usage_rate(stats, team, team["MP"]), 3)
            print(json.dumps(out, indent=2))
            return 0
        if not a.team or not (a.boxes or a.season):
            p.error("team needs --team and --season (or --boxes)")
        path = a.boxes or box_path(a.league, a.season)
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        if rows:
            _check_csv(path, _REQUIRED)
        complete = [r for r in rows if None not in r.values()]
        if len(complete) < len(rows):
            print(f"warning: skipped {len(rows) - len(complete)} incomplete rows (truncated file?)", file=sys.stderr)
        types = (REGULAR_SEASON, POSTSEASON) if a.all else POSTSEASON if a.postseason else REGULAR_SEASON
        exclude = nba_excluded_games(a.season) if a.league == "nba" and a.season and not a.boxes \
            else NBA_CUP_FINALS
        t, o = season_totals(complete, a.team, types, exclude)
        print(json.dumps(team_ratings(t, o), indent=2))
        return 0
    except (LookupError, ValueError, OSError) as e:
        print(f"hoops.py: error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
