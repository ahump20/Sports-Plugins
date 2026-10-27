#!/usr/bin/env python3
"""NFL efficiency from nflverse play-by-play, plus passer rating formulas. Stdlib only.

Usage:
  nflfast.py teams  --season 2024 [--weeks 1-9] [--season-type REG]
  nflfast.py player --season 2024 --name "L.Jackson"        # nflverse short name or player id
  nflfast.py rating --cmp 343 --att 502 --yds 4643 --td 45 --int 6 [--ncaa]
  --pbp FILE reads a local CSV/CSV.gz instead of downloading.
Downloads go to ~/.cache/sports-plugins/nflverse (about 20 MB a season, refreshed after 12 hours).
"""
import argparse
import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict

PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"
CACHE = os.path.expanduser("~/.cache/sports-plugins/nflverse")


def pbp_path(season, max_age_hours=12):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"play_by_play_{int(season)}.csv.gz")
    if not os.path.exists(path) or time.time() - os.path.getmtime(path) > max_age_hours * 3600:
        tmp = path + ".part"
        urllib.request.urlretrieve(PBP_URL.format(season=int(season)), tmp)
        os.replace(tmp, path)
    return path


def read_pbp(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", newline="") as f:
        yield from csv.DictReader(f)


def _num(x):
    return None if x in (None, "", "NA") else float(x)


def _flag(r, k):
    return r.get(k) == "1"


def is_scrimmage(r):
    """The filter most public EPA work uses: a real pass or run with an EPA value.
    pass==1 includes sacks and scrambles; rush==1 excludes kneels and spikes. Plays wiped out
    by a penalty (play_type no_play) stay in: nflverse keeps the pass/rush flag on them, and an
    offensive holding call is part of how an offense performed."""
    return _num(r.get("epa")) is not None and r.get("posteam") not in ("", "NA", None) and (
        _flag(r, "pass") or _flag(r, "rush"))


def parse_weeks(spec):
    if not spec:
        return None
    weeks = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        weeks.update(range(int(lo), int(hi or lo) + 1))
    return weeks


def _keep(r, weeks, season_type):
    if season_type and r.get("season_type") != season_type:
        return False
    return weeks is None or int(r["week"]) in weeks


def team_efficiency(rows, weeks=None, season_type="REG"):
    acc = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if not _keep(r, weeks, season_type) or not is_scrimmage(r):
            continue
        epa, good = _num(r["epa"]), epa_success(r)
        for side, team in (("off", r["posteam"]), ("def", r["defteam"])):
            a = acc[team]
            a[f"{side}_plays"] += 1
            a[f"{side}_epa"] += epa
            a[f"{side}_success"] += good
            kind = "pass" if _flag(r, "pass") else "rush"
            a[f"{side}_{kind}_plays"] += 1
            a[f"{side}_{kind}_epa"] += epa
    out = {}
    for team, a in acc.items():
        row = {}
        for side in ("off", "def"):
            n = a[f"{side}_plays"]
            row[f"{side}_plays"] = int(n)
            row[f"{side}_epa_per_play"] = round(a[f"{side}_epa"] / n, 3) if n else None
            row[f"{side}_success_rate"] = round(a[f"{side}_success"] / n, 3) if n else None
            for kind in ("pass", "rush"):
                k = a[f"{side}_{kind}_plays"]
                row[f"{side}_{kind}_epa_per_play"] = round(a[f"{side}_{kind}_epa"] / k, 3) if k else None
        row["net_epa_per_play"] = (round(row["off_epa_per_play"] - row["def_epa_per_play"], 3)
                                   if row["off_epa_per_play"] is not None and row["def_epa_per_play"] is not None
                                   else None)
        out[team] = row
    return dict(sorted(out.items(), key=lambda kv: -(kv[1]["net_epa_per_play"] or -99)))


def epa_success(r):
    epa = _num(r.get("epa"))
    return 1.0 if epa is not None and epa > 0 else 0.0


def player_summary(rows, who, weeks=None, season_type="REG"):
    """Totals that match nflverse's player stats, plus per-play rates.

    passing_epa: sum of qb_epa on every play with this passer (nflverse's definition).
    rushing_epa: sum of epa on run and kneel plays with this rusher (nflverse's definition).
    qb_epa credits the passer only up to a receiver's fumble; epa charges the whole play.
    """
    s = defaultdict(float)
    cpoe = []
    name = None
    for r in rows:
        if not _keep(r, weeks, season_type):
            continue
        passer = who in (r.get("passer_player_id"), r.get("passer_player_name"))
        rusher = who in (r.get("rusher_player_id"), r.get("rusher_player_name"))
        if passer:
            name = r.get("passer_player_name") or name
            s["passing_epa"] += _num(r.get("qb_epa")) or 0.0
            if _flag(r, "qb_dropback") and _num(r.get("epa")) is not None:
                s["dropbacks"] += 1
                s["dropback_epa"] += _num(r["qb_epa"]) or 0.0
                s["dropback_success"] += epa_success(r)
            c = _num(r.get("cpoe"))
            if c is not None:
                cpoe.append(c)
        if rusher:
            name = r.get("rusher_player_name") or name
            if r.get("play_type") in ("run", "qb_kneel"):
                s["rushing_epa"] += _num(r.get("epa")) or 0.0
            if is_scrimmage(r) and _flag(r, "rush"):
                s["designed_and_scramble_rushes"] += 1
                s["rush_success"] += epa_success(r)
    out = {"player": name or who, "passing_epa": round(s["passing_epa"], 3),
           "rushing_epa": round(s["rushing_epa"], 3)}
    if s["dropbacks"]:
        out.update(dropbacks=int(s["dropbacks"]),
                   epa_per_dropback=round(s["dropback_epa"] / s["dropbacks"], 3),
                   dropback_success_rate=round(s["dropback_success"] / s["dropbacks"], 3))
    if cpoe:
        out["cpoe"] = round(sum(cpoe) / len(cpoe), 2)
    return out


def nfl_passer_rating(cmp_, att, yds, td, int_):
    """NFL/CFL formula: four components each capped to [0, 2.375]."""
    clamp = lambda v: max(0.0, min(2.375, v))  # noqa: E731
    a = clamp((cmp_ / att - 0.3) * 5)
    b = clamp((yds / att - 3) * 0.25)
    c = clamp(td / att * 20)
    d = clamp(2.375 - int_ / att * 25)
    return (a + b + c + d) / 6 * 100


def ncaa_passing_efficiency(cmp_, att, yds, td, int_):
    """NCAA formula: uncapped, so values above 200 and below 0 are possible."""
    return (8.4 * yds + 330 * td + 100 * cmp_ - 200 * int_) / att


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["teams", "player", "rating"])
    p.add_argument("--season", type=int)
    p.add_argument("--weeks")
    p.add_argument("--season-type", default="REG", choices=["REG", "POST", "ALL"])
    p.add_argument("--name")
    p.add_argument("--pbp")
    for k in ("cmp", "att", "yds", "td", "int"):
        p.add_argument(f"--{k}", type=float)
    p.add_argument("--ncaa", action="store_true")
    a = p.parse_args(argv)

    if a.mode == "rating":
        args = (a.cmp, a.att, a.yds, a.td, getattr(a, "int"))
        if None in args:
            p.error("rating needs --cmp --att --yds --td --int")
        f = ncaa_passing_efficiency if a.ncaa else nfl_passer_rating
        print(json.dumps({"ncaa_efficiency" if a.ncaa else "passer_rating": round(f(*args), 1)}))
        return 0
    if not (a.pbp or a.season):
        p.error("give --season or --pbp")
    rows = read_pbp(a.pbp or pbp_path(a.season))
    st = None if a.season_type == "ALL" else a.season_type
    weeks = parse_weeks(a.weeks)
    if a.mode == "teams":
        out = team_efficiency(rows, weeks, st)
    else:
        if not a.name:
            p.error("player needs --name")
        out = player_summary(rows, a.name, weeks, st)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
