#!/usr/bin/env python3
"""NFL efficiency from nflverse play-by-play, plus passer rating formulas. Stdlib only.

Usage:
  nflfast.py teams  --season 2024 [--weeks 1-9] [--season-type REG]
  nflfast.py player --season 2024 --name "L.Jackson"        # nflverse short name or player id
  nflfast.py rating --cmp 343 --att 502 --yds 4643 --td 45 --int 6 [--ncaa]
  --pbp FILE reads a local CSV/CSV.gz instead of downloading.
Downloads go to ~/.cache/sports-plugins/nflverse (about 20 MB a season). A finished
season is kept for good; the current one is refreshed after 12 hours.
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

PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"
CACHE = os.path.expanduser("~/.cache/sports-plugins/nflverse")
DOWNLOAD_TIMEOUT = 60  # seconds a download may stall before it fails


def season_over(season):
    """When a season's play-by-play stops changing: March 1 after it, past every Super Bowl."""
    return time.mktime((int(season) + 1, 3, 1, 0, 0, 0, 0, 0, -1))


def pbp_path(season, max_age_hours=12):
    """Cached path to a season's play-by-play. A copy saved after the season ended is kept for good; any
    other copy is downloaded again once it is older than max_age_hours. A download is checked as a complete
    gzip before it replaces the cache; if it fails and an older copy exists, that copy is used with a
    warning on stderr."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"play_by_play_{int(season)}.csv.gz")
    if os.path.exists(path):
        saved = os.path.getmtime(path)
        if saved >= season_over(season) or time.time() - saved <= max_age_hours * 3600:
            return path
    tmp = path + ".part"
    try:
        old = socket.getdefaulttimeout()
        socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)  # a stalled server fails instead of hanging
        try:
            urllib.request.urlretrieve(PBP_URL.format(season=int(season)), tmp)
        finally:
            socket.setdefaulttimeout(old)
        with gzip.open(tmp, "rb") as f:
            while f.read(1 << 20):
                pass
        os.replace(tmp, path)
    except (OSError, EOFError, zlib.error) as e:  # URLError, HTTPError and BadGzipFile are OSErrors
        if os.path.exists(tmp):
            os.remove(tmp)
        if isinstance(e, urllib.error.HTTPError) and e.code == 404:
            reason = f"nflverse has no play-by-play file for {int(season)} yet (HTTP 404)"
        else:
            reason = f"downloading {int(season)} play-by-play failed: {e}"
        if os.path.exists(path):
            print(f"warning: {reason}; using the cached copy from "
                  f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(path)))}", file=sys.stderr)
            return path
        raise RuntimeError(reason) from e
    return path


REQUIRED = ("season_type", "week", "posteam", "defteam", "epa", "pass", "rush")


def read_pbp(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or ())]
        if missing:
            raise ValueError(f"{path} is missing play-by-play columns: {', '.join(missing)}")
        yield from reader


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
    """'1-9', '7', '1-3,7' -> set of weeks. Postseason weeks follow the regular season (19-22 since 2021)."""
    if not spec:
        return None
    weeks = set()
    for part in spec.split(","):
        lo, dash, hi = (x.strip() for x in part.partition("-"))
        if not lo.isdigit() or (dash and not hi.isdigit()):
            raise ValueError(f"bad --weeks {spec!r}: use weeks like 1-9 or 1-3,7")
        lo, hi = int(lo), int(hi) if dash else int(lo)
        if lo < 1 or hi < lo:
            raise ValueError(f"bad --weeks {spec!r}: weeks start at 1 and a range runs low-high")
        weeks.update(range(lo, hi + 1))
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
    return dict(sorted(out.items(), key=lambda kv: (kv[1]["net_epa_per_play"] is None,
                                                     -(kv[1]["net_epa_per_play"] or 0.0))))


def epa_success(r):
    epa = _num(r.get("epa"))
    return 1.0 if epa is not None and epa > 0 else 0.0


def player_summary(rows, who, weeks=None, season_type="REG"):
    """Totals that match nflverse's player stats, plus per-play rates.

    passing_epa: sum of qb_epa on pass and qb_spike plays with this passer (nflverse's definition;
    it leaves out nullified two-point tries and fakes on kicks).
    A short name shared by two players is refused; pass the GSIS id.
    rushing_epa: sum of epa on run and kneel plays with this rusher (nflverse's definition).
    qb_epa credits the passer only up to a receiver's fumble; epa charges the whole play.
    dropbacks: every qb_dropback play, sacks and scrambles included.
    """
    s = defaultdict(float)
    cpoe = []
    name = None
    ids = {}  # player id -> teams, for players matched by short name
    for r in rows:
        if not _keep(r, weeks, season_type):
            continue
        passer = who in (r.get("passer_player_id"), r.get("passer_player_name"))
        rusher = who in (r.get("rusher_player_id"), r.get("rusher_player_name"))
        for role, hit in (("passer", passer), ("rusher", rusher)):
            if hit and who == r.get(f"{role}_player_name"):
                ids.setdefault(r.get(f"{role}_player_id"), set()).add(r.get("posteam"))
        if passer or rusher:
            s["plays"] += 1
        if passer:
            name = r.get("passer_player_name") or name
        if passer and r.get("play_type") in ("pass", "qb_spike"):
            s["passing_epa"] += _num(r.get("qb_epa")) or 0.0
            c = _num(r.get("cpoe"))
            if c is not None:
                cpoe.append(c)
        # A scramble is a dropback with the quarterback in the rusher fields and no passer.
        if (passer or rusher) and _flag(r, "qb_dropback") and _num(r.get("epa")) is not None:
            s["dropbacks"] += 1
            s["dropback_epa"] += _num(r.get("qb_epa")) or 0.0
            s["dropback_success"] += epa_success(r)
        if rusher:
            name = r.get("rusher_player_name") or name
            if r.get("play_type") in ("run", "qb_kneel"):
                s["rushing_epa"] += _num(r.get("epa")) or 0.0
            if is_scrimmage(r) and _flag(r, "rush"):
                s["designed_and_scramble_rushes"] += 1
                s["rush_success"] += epa_success(r)
    if len(ids) > 1:
        found = "; ".join(f"{i} ({'/'.join(sorted(t))})" for i, t in sorted(ids.items()))
        raise ValueError(f"{who} matches more than one player: {found}. Pass the player id instead.")
    if not s["plays"]:
        raise ValueError(f"no passing or rushing plays for {who!r}; names are nflverse short names "
                         "(L.Jackson) and are case-sensitive, or use the GSIS id (00-0034796)")
    out = {"player": name or who, "passing_epa": round(s["passing_epa"], 3),
           "rushing_epa": round(s["rushing_epa"], 3)}
    if s["dropbacks"]:
        out.update(dropbacks=int(s["dropbacks"]),
                   epa_per_dropback=round(s["dropback_epa"] / s["dropbacks"], 3),
                   dropback_success_rate=round(s["dropback_success"] / s["dropbacks"], 3))
    if cpoe:
        out["cpoe"] = round(sum(cpoe) / len(cpoe), 2)
    return out


def _check_line(cmp_, att, yds, td, int_):
    if not att > 0:
        raise ValueError("attempts must be positive")
    if min(cmp_, td, int_) < 0 or cmp_ > att or td > cmp_ or cmp_ + int_ > att:
        raise ValueError("impossible line: need 0 <= TD <= Cmp and Cmp + Int <= Att")


def nfl_passer_rating(cmp_, att, yds, td, int_):
    """NFL/CFL formula: four components each capped to [0, 2.375]."""
    _check_line(cmp_, att, yds, td, int_)
    clamp = lambda v: max(0.0, min(2.375, v))  # noqa: E731
    a = clamp((cmp_ / att - 0.3) * 5)
    b = clamp((yds / att - 3) * 0.25)
    c = clamp(td / att * 20)
    d = clamp(2.375 - int_ / att * 25)
    return (a + b + c + d) / 6 * 100


def ncaa_passing_efficiency(cmp_, att, yds, td, int_):
    """NCAA formula: uncapped, so values above 200 and below 0 are possible."""
    _check_line(cmp_, att, yds, td, int_)
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
        try:
            print(json.dumps({"ncaa_efficiency" if a.ncaa else "passer_rating": round(f(*args), 1)}))
        except ValueError as e:
            p.error(str(e))
        return 0
    if not (a.pbp or a.season):
        p.error("give --season or --pbp")
    if a.mode == "player" and not a.name:
        p.error("player needs --name")
    st = None if a.season_type == "ALL" else a.season_type
    try:
        weeks = parse_weeks(a.weeks)
        path = a.pbp or pbp_path(a.season)
    except (ValueError, RuntimeError) as e:
        p.error(str(e))
    rows = read_pbp(path)
    try:
        if a.mode == "teams":
            out = team_efficiency(rows, weeks, st)
            if not out:
                raise ValueError(f"no plays match --season-type {a.season_type}"
                                 + (f" --weeks {a.weeks}" if a.weeks else "")
                                 + " (the regular season is weeks 1-18 since 2021; postseason weeks need --season-type POST)")
        else:
            out = player_summary(rows, a.name, weeks, st)
    except ValueError as e:
        p.error(str(e))
    except (OSError, EOFError, zlib.error, csv.Error) as e:  # truncated or corrupt file
        if not a.pbp:
            os.remove(path)
            p.error(f"cached play-by-play was unreadable ({e}) and has been removed; rerun to download it again")
        p.error(f"cannot read {path}: {e}")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
