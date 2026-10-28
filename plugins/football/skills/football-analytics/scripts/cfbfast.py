#!/usr/bin/env python3
"""College football efficiency from sportsdataverse play-by-play, plus official box-score passing lines.
Stdlib only.

Usage:
  cfbfast.py teams  --season 2024 [--team Texas] [--weeks 1-9] [--season-type ALL]
  cfbfast.py player --season 2024 --name "Quinn Ewers"     # ESPN full name or athlete id (4889929)
  --pbp FILE and --box FILE read local CSV/CSV.gz files instead of downloading.
Downloads go to ~/.cache/sports-plugins/sportsdataverse. The play-by-play file is about 550 MB a season;
only the columns used here are kept (a few MB). A finished season is kept for good; the current one is
refreshed after 24 hours.
"""
import argparse
import csv
import gzip
import io
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
import zlib
from collections import defaultdict

from nflfast import ncaa_passing_efficiency, parse_weeks

RELEASES = "https://github.com/sportsdataverse/sportsdataverse-data/releases/download"
PBP_URL = RELEASES + "/espn_cfb_pbp/play_by_play_{season}.csv"
BOX_URL = RELEASES + "/espn_cfb_player_box/player_box_{season}.csv"
CACHE = os.path.expanduser("~/.cache/sports-plugins/sportsdataverse")
DOWNLOAD_TIMEOUT = 60  # seconds a download may stall before it fails

PBP_COLUMNS = ("game_id", "season", "seasonType", "week", "pos_team_id", "pos_team", "def_pos_team_id",
               "def_pos_team", "homeTeamId", "awayTeamId", "homeTeamName", "awayTeamName", "homeTeamAbbrev",
               "awayTeamAbbrev", "type.text", "scrimmage_play", "rush", "pass", "sack", "EPA",
               "passer_player_id", "passer_player_name", "rusher_player_id", "rusher_player_name")
BOX_COLUMNS = ("game_id", "season", "category", "athlete_id", "athlete_name", "team_id",
               "completions/passingAttempts", "passingYards", "passingTouchdowns", "interceptions")
REQUIRED = ("seasonType", "week", "pos_team", "def_pos_team", "EPA", "scrimmage_play", "rush", "pass")
SEASON_TYPES = {"2": "REG", "3": "POST"}


def season_over(season):
    """When a season's files stop changing: February 1 after it, past every bowl and the title game."""
    return time.mktime((int(season) + 1, 2, 1, 0, 0, 0, 0, 0, -1))


def cached(url, name, season, columns, max_age_hours=24):
    """Cached gzip CSV of `columns` from `url`. The download is streamed, trimmed to those columns, checked
    as a complete gzip and only then replaces the cache; if it fails and an older copy exists, that copy is
    used with a warning on stderr."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{name}_{int(season)}.csv.gz")
    if os.path.exists(path):
        saved = os.path.getmtime(path)
        if saved >= season_over(season) or time.time() - saved <= max_age_hours * 3600:
            return path
    tmp = path + ".part"
    try:
        old = socket.getdefaulttimeout()
        socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)  # a stalled server fails instead of hanging
        try:
            with urllib.request.urlopen(url.format(season=int(season))) as resp, \
                    gzip.open(tmp, "wt", newline="") as out:
                reader = csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8", newline=""))
                missing = [c for c in columns if c not in (reader.fieldnames or ())]
                if missing:
                    raise ValueError(f"{name} {int(season)} is missing columns: {', '.join(missing)}")
                writer = csv.writer(out)
                writer.writerow(columns)
                for r in reader:
                    writer.writerow([r[c] for c in columns])
        finally:
            socket.setdefaulttimeout(old)
        with gzip.open(tmp, "rb") as f:
            while f.read(1 << 20):
                pass
        os.replace(tmp, path)
    except (OSError, EOFError, zlib.error, csv.Error, ValueError) as e:  # URLError and HTTPError are OSErrors
        if os.path.exists(tmp):
            os.remove(tmp)
        if isinstance(e, urllib.error.HTTPError) and e.code == 404:
            reason = f"sportsdataverse has no {name} file for {int(season)} yet (HTTP 404)"
        else:
            reason = f"downloading {int(season)} {name} failed: {e}"
        if os.path.exists(path):
            print(f"warning: {reason}; using the cached copy from "
                  f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(path)))}", file=sys.stderr)
            return path
        raise RuntimeError(reason) from e
    return path


def pbp_path(season):
    return cached(PBP_URL, "play_by_play", season, PBP_COLUMNS)


def box_path(season):
    return cached(BOX_URL, "player_box", season, BOX_COLUMNS)


def read_csv(path, required=REQUIRED):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or ())]
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(missing)}")
        yield from reader


def _num(x):
    return None if x in (None, "", "NA") else float(x)


def _flag(r, k):
    return r.get(k) in ("true", "True", "TRUE", "1")


def is_scrimmage(r):
    """The publisher's own filter (sportsdataverse's advanced box scores): every scrimmage play with an EPA
    value. That keeps sacks and scrambles, drops kneels, spikes, special teams and plays wiped out by a
    penalty (ESPN files those as penalties), and keeps the rare scrimmage play that is neither a run nor a
    pass, such as a fumble returned for a touchdown, in the totals."""
    return _flag(r, "scrimmage_play") and _num(r.get("EPA")) is not None and r.get("pos_team") not in ("", "NA", None)


def epa_success(r):
    epa = _num(r.get("EPA"))
    return 1.0 if epa is not None and epa > 0 else 0.0


def _keep(r, weeks, season_type):
    kind = SEASON_TYPES.get(r.get("seasonType"), r.get("seasonType"))
    if season_type and kind != season_type:
        return False
    if weeks is None:
        return True
    return kind == "REG" and int(r["week"]) in weeks  # every postseason game is week 1 in ESPN's files


def team_names(rows):
    """team id -> (full name, school, abbreviation), from the home and away columns."""
    out = {}
    for r in rows:
        for side in ("home", "away"):
            tid = r.get(f"{side}TeamId")
            if tid and tid not in out:
                out[tid] = (None, r.get(f"{side}TeamName"), r.get(f"{side}TeamAbbrev"))
        for k in ("pos_team", "def_pos_team"):
            tid = r.get(f"{k}_id")
            if tid in out and out[tid][0] is None:
                out[tid] = (r.get(k),) + out[tid][1:]
    return out


def team_efficiency(rows, weeks=None, season_type=None, team=None):
    rows = [r for r in rows if _keep(r, weeks, season_type)]
    names = team_names(rows)
    acc = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if not is_scrimmage(r):
            continue
        epa, good = _num(r["EPA"]), epa_success(r)
        for side, tid in (("off", r.get("pos_team_id") or r["pos_team"]),
                          ("def", r.get("def_pos_team_id") or r["def_pos_team"])):
            a = acc[tid]
            a[f"{side}_plays"] += 1
            a[f"{side}_epa"] += epa
            a[f"{side}_success"] += good
            for kind in ("pass", "rush"):
                if _flag(r, kind):
                    a[f"{side}_{kind}_plays"] += 1
                    a[f"{side}_{kind}_epa"] += epa
    out = {}
    for tid, a in acc.items():
        full, school, abbr = names.get(tid, (None, None, None))
        if not full:
            full = next((r[k] for r in rows for k in ("pos_team", "def_pos_team")
                         if (r.get(f"{k}_id") or r[k]) == tid), tid)
        if team and team.lower() not in {str(x).lower() for x in (tid, full, school, abbr) if x}:
            continue
        row = {"team_id": tid, "abbr": abbr}
        for side in ("off", "def"):
            n = a[f"{side}_plays"]
            row[f"{side}_plays"] = int(n)
            row[f"{side}_epa"] = round(a[f"{side}_epa"], 2)
            row[f"{side}_epa_per_play"] = round(a[f"{side}_epa"] / n, 3) if n else None
            row[f"{side}_success_rate"] = round(a[f"{side}_success"] / n, 3) if n else None
            for kind in ("pass", "rush"):
                k = a[f"{side}_{kind}_plays"]
                row[f"{side}_{kind}_plays"] = int(k)
                row[f"{side}_{kind}_epa_per_play"] = round(a[f"{side}_{kind}_epa"] / k, 3) if k else None
        row["net_epa_per_play"] = (round(row["off_epa_per_play"] - row["def_epa_per_play"], 3)
                                   if row["off_epa_per_play"] is not None and row["def_epa_per_play"] is not None
                                   else None)
        out[full] = row
    return dict(sorted(out.items(), key=lambda kv: (kv[1]["net_epa_per_play"] is None,
                                                     -(kv[1]["net_epa_per_play"] or 0.0))))


def _who(rows, who, role, ids):
    """Rows where `who` (ESPN id or exact full name) is in the role's fields; records ids seen by name."""
    for r in rows:
        pid, name = r.get(f"{role}_player_id"), r.get(f"{role}_player_name")
        if who == pid or who == name:
            if who == name:
                ids.setdefault(pid, set()).add(r.get("pos_team"))
            yield r


def player_summary(rows, who, weeks=None, season_type=None):
    """Passing and rushing EPA the way the publisher's advanced box scores count them.

    passing_epa: sum of EPA on scrimmage pass plays with this passer, sacks included.
    rushing_epa: sum of EPA on scrimmage runs with this rusher, scrambles included.
    A full name shared by two players is refused; pass the ESPN athlete id.
    """
    rows = [r for r in rows if _keep(r, weeks, season_type) and is_scrimmage(r)]
    ids = {}
    passes = [r for r in _who(rows, who, "passer", ids) if _flag(r, "pass")]
    runs = [r for r in _who(rows, who, "rusher", ids) if _flag(r, "rush")]
    ids.pop("", None)
    if len(ids) > 1:
        found = "; ".join(f"{i} ({'/'.join(sorted(t))})" for i, t in sorted(ids.items()))
        raise ValueError(f"{who} matches more than one player: {found}. Pass the athlete id instead.")
    if not passes and not runs:
        raise ValueError(f"no passing or rushing plays for {who!r}; use the ESPN full name exactly "
                         "(Quinn Ewers) or the athlete id (4889929)")
    name = next((r[f"{k}_player_name"] for r, k in [(x, "passer") for x in passes] + [(x, "rusher") for x in runs]
                 if r.get(f"{k}_player_name")), who)
    out = {"player": name}
    if passes:
        e = sum(_num(r["EPA"]) for r in passes)
        out.update(dropbacks=len(passes), sacks=sum(1 for r in passes if _flag(r, "sack")),
                   passing_epa=round(e, 2), epa_per_dropback=round(e / len(passes), 3),
                   dropback_success_rate=round(sum(epa_success(r) for r in passes) / len(passes), 3))
    if runs:
        e = sum(_num(r["EPA"]) for r in runs)
        out.update(rushes=len(runs), rushing_epa=round(e, 2), epa_per_rush=round(e / len(runs), 3),
                   rush_success_rate=round(sum(epa_success(r) for r in runs) / len(runs), 3))
    return out


def passing_line(box_rows, who, games=None):
    """Official passing line summed from ESPN box scores, with NCAA passing efficiency.
    `games` limits it to those game ids (the play-by-play filter's games)."""
    line = defaultdict(int)
    ids = set()
    for r in box_rows:
        if r.get("category") != "passing" or who not in (r.get("athlete_id"), r.get("athlete_name")):
            continue
        if games is not None and r.get("game_id") not in games:
            continue
        ids.add(r.get("athlete_id"))
        cmp_, _, att = (r.get("completions/passingAttempts") or "").partition("/")
        if not (cmp_.isdigit() and att.isdigit()):
            continue
        line["games"] += 1
        line["cmp"] += int(cmp_)
        line["att"] += int(att)
        for k, col in (("yds", "passingYards"), ("td", "passingTouchdowns"), ("int", "interceptions")):
            line[k] += int(float(r.get(col) or 0))
    if len(ids) > 1:
        raise ValueError(f"{who} matches more than one player in the box scores: {', '.join(sorted(ids))}. "
                         "Pass the athlete id instead.")
    if not line["att"]:
        return None
    out = dict(line)
    out["ncaa_efficiency"] = round(ncaa_passing_efficiency(line["cmp"], line["att"], line["yds"],
                                                           line["td"], line["int"]), 2)
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["teams", "player"])
    p.add_argument("--season", type=int)
    p.add_argument("--weeks")
    p.add_argument("--season-type", default="ALL", choices=["REG", "POST", "ALL"])
    p.add_argument("--team")
    p.add_argument("--name")
    p.add_argument("--pbp")
    p.add_argument("--box")
    a = p.parse_args(argv)

    if not (a.pbp or a.season):
        p.error("give --season or --pbp")
    if a.mode == "player" and not a.name:
        p.error("player needs --name")
    st = None if a.season_type == "ALL" else a.season_type
    try:
        weeks = parse_weeks(a.weeks)
        if weeks is not None and st == "POST":
            raise ValueError("--weeks counts regular-season weeks; ESPN files every postseason game as week 1")
        path = a.pbp or pbp_path(a.season)
    except (ValueError, RuntimeError) as e:
        p.error(str(e))
    reading, local = path, bool(a.pbp)
    try:
        rows = list(read_csv(path))
        if a.mode == "teams":
            out = team_efficiency(rows, weeks, st, a.team)
            if not out:
                raise ValueError(("no team matches --team " + repr(a.team) + " (try the school, full name, "
                                  "abbreviation or ESPN id: Texas, Texas Longhorns, TEX, 251)") if a.team else
                                 f"no plays match --season-type {a.season_type}"
                                 + (f" --weeks {a.weeks}" if a.weeks else ""))
        else:
            out = player_summary(rows, a.name, weeks, st)
            if a.box or a.season:
                games = {r["game_id"] for r in rows if _keep(r, weeks, st)}
                bpath = a.box or box_path(a.season)
                reading, local = bpath, bool(a.box)
                line = passing_line(read_csv(bpath, ("category", "athlete_id", "athlete_name")), a.name, games)
                if line:
                    out["box_score_passing"] = line
    except ValueError as e:
        p.error(str(e))
    except RuntimeError as e:
        p.error(str(e))
    except (OSError, EOFError, zlib.error, csv.Error) as e:  # truncated or corrupt file
        if not local:
            os.remove(reading)
            p.error(f"cached {os.path.basename(reading)} was unreadable ({e}) and has been removed; "
                    "rerun to download it again")
        p.error(f"cannot read {reading}: {e}")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
