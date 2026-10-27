#!/usr/bin/env python3
"""Sabermetric calculations with published FanGraphs constants. Stdlib only.

Usage:
  saber.py batting  --season 2024 --stats '{"PA":731,"AB":636,...}'
  saber.py pitching --season 2024 --stats '{"IP":"192.0","HR":15,...}'
  saber.py league   --totals '{"AB":...,"H":...,"ERA":...}'   # constants for any league (NCAA, minors)
  saber.py batting  --season 2024 --mlb-person 660271           # pull counting stats from MLB Stats API
Stats keys: PA AB H 2B 3B HR BB IBB HBP SF SO (batting); IP HR BB IBB HBP SO ER (pitching).
"""
import argparse
import json
import sys
import urllib.request

# FanGraphs Guts! table, copied 2026-10-27 from https://www.fangraphs.com/guts.aspx?type=cn
# season: (lg_wOBA, wOBA_scale, wBB, wHBP, w1B, w2B, w3B, wHR, runSB, runCS, R_PA, R_W, cFIP)
GUTS = {
    2026: (.316, 1.238, .698, .729, .890, 1.261, 1.596, 2.049, .200, -.412, .118, 9.822, 3.100),
    2025: (.313, 1.232, .691, .722, .882, 1.252, 1.584, 2.037, .200, -.410, .118, 9.774, 3.135),
    2024: (.310, 1.242, .689, .720, .882, 1.254, 1.590, 2.050, .200, -.405, .117, 9.683, 3.166),
    2023: (.318, 1.204, .696, .726, .883, 1.244, 1.569, 2.004, .200, -.422, .122, 10.028, 3.255),
    2022: (.310, 1.259, .689, .720, .884, 1.261, 1.601, 2.072, .200, -.397, .114, 9.524, 3.112),
    2021: (.314, 1.209, .692, .722, .879, 1.242, 1.568, 2.007, .200, -.419, .121, 9.973, 3.170),
    2020: (.320, 1.185, .699, .728, .883, 1.238, 1.558, 1.979, .200, -.435, .125, 10.282, 3.191),
    2019: (.320, 1.157, .690, .719, .870, 1.217, 1.529, 1.940, .200, -.435, .126, 10.296, 3.214),
    2018: (.315, 1.226, .690, .720, .880, 1.247, 1.578, 2.031, .200, -.407, .117, 9.714, 3.160),
    2017: (.321, 1.185, .693, .723, .877, 1.232, 1.552, 1.980, .200, -.423, .122, 10.048, 3.158),
    2016: (.318, 1.212, .691, .721, .878, 1.242, 1.569, 2.015, .200, -.410, .118, 9.778, 3.147),
    2015: (.313, 1.251, .687, .718, .881, 1.256, 1.594, 2.065, .200, -.392, .112, 9.421, 3.134),
    2014: (.310, 1.304, .689, .722, .892, 1.283, 1.635, 2.135, .200, -.377, .107, 9.117, 3.132),
    2013: (.314, 1.277, .690, .722, .888, 1.271, 1.616, 2.101, .200, -.384, .110, 9.264, 3.048),
    2012: (.315, 1.245, .691, .722, .884, 1.257, 1.593, 2.058, .200, -.398, .114, 9.544, 3.094),
    2011: (.316, 1.264, .694, .726, .890, 1.270, 1.611, 2.086, .200, -.394, .112, 9.454, 3.025),
    2010: (.321, 1.251, .701, .732, .895, 1.270, 1.608, 2.072, .200, -.403, .115, 9.643, 3.078),
}
_FIELDS = ("lg_woba", "scale", "wBB", "wHBP", "w1B", "w2B", "w3B", "wHR",
           "runSB", "runCS", "r_pa", "r_w", "cfip")


def constants(season):
    if season not in GUTS:
        raise KeyError(f"no FanGraphs constants for {season}; have {min(GUTS)}-{max(GUTS)}. "
                       "Use league_constants() with that league's totals instead.")
    return dict(zip(_FIELDS, GUTS[season]))


def parse_ip(ip):
    """Box-score innings: '6.2' means 6 and 2/3, not 6.2."""
    whole, _, outs = str(ip).partition(".")
    outs = int(outs or 0)
    if outs not in (0, 1, 2):
        raise ValueError(f"innings {ip!r}: the digit after the dot counts outs (0-2)")
    return int(whole) + outs / 3


def _g(s, k):
    return s.get(k, 0) or 0


def singles(s):
    return _g(s, "H") - _g(s, "2B") - _g(s, "3B") - _g(s, "HR")


def slash(s):
    ab, h = _g(s, "AB"), _g(s, "H")
    obp_den = ab + _g(s, "BB") + _g(s, "HBP") + _g(s, "SF")
    tb = singles(s) + 2 * _g(s, "2B") + 3 * _g(s, "3B") + 4 * _g(s, "HR")
    avg = h / ab if ab else 0.0
    obp = (h + _g(s, "BB") + _g(s, "HBP")) / obp_den if obp_den else 0.0
    slg = tb / ab if ab else 0.0
    bip = ab - _g(s, "SO") - _g(s, "HR") + _g(s, "SF")
    pa = _g(s, "PA") or obp_den
    return {
        "AVG": avg, "OBP": obp, "SLG": slg, "OPS": obp + slg, "ISO": slg - avg,
        "BABIP": (h - _g(s, "HR")) / bip if bip else 0.0,
        "K%": _g(s, "SO") / pa if pa else 0.0,
        "BB%": _g(s, "BB") / pa if pa else 0.0,
    }


def woba(s, c):
    ubb = _g(s, "BB") - _g(s, "IBB")
    den = _g(s, "AB") + ubb + _g(s, "SF") + _g(s, "HBP")
    if not den:
        return 0.0
    num = (c["wBB"] * ubb + c["wHBP"] * _g(s, "HBP") + c["w1B"] * singles(s)
           + c["w2B"] * _g(s, "2B") + c["w3B"] * _g(s, "3B") + c["wHR"] * _g(s, "HR"))
    return num / den


def wraa(w, pa, c):
    return (w - c["lg_woba"]) / c["scale"] * pa


def wrc_plus(w, pa, c, park_factor=1.0, lg_wrc_pa=None):
    """FanGraphs wRC+. park_factor 1.00 = neutral (FanGraphs basic PF / 100).
    lg_wrc_pa defaults to league R/PA; FanGraphs uses the league's non-pitcher wRC/PA,
    so expect a few points of difference from the published number."""
    r_pa = c["r_pa"]
    lg = lg_wrc_pa or r_pa
    return ((wraa(w, pa, c) / pa + r_pa) + (r_pa - park_factor * r_pa)) / lg * 100


def fip(s, c):
    ip = parse_ip(_g(s, "IP"))
    return (13 * _g(s, "HR") + 3 * (_g(s, "BB") + _g(s, "HBP")) - 2 * _g(s, "SO")) / ip + c["cfip"]


def league_constants(t, reference_season=2024):
    """Constants for a league FanGraphs doesn't cover (NCAA, minors, a single conference).

    Keeps a reference MLB season's relative run values and rescales them so league wOBA
    equals league OBP (the same rule FanGraphs uses). The relative values are an MLB
    approximation; the scale, cFIP and R/PA come from the league's own totals.
    """
    ref = constants(reference_season)
    raw = {k: ref[k] / ref["scale"] for k in ("wBB", "wHBP", "w1B", "w2B", "w3B", "wHR")}
    unscaled = woba(t, raw)
    ubb = _g(t, "BB") - _g(t, "IBB")
    den = _g(t, "AB") + ubb + _g(t, "SF") + _g(t, "HBP")
    lg_obp = (_g(t, "H") + ubb + _g(t, "HBP")) / den
    scale = lg_obp / unscaled
    out = {k: v * scale for k, v in raw.items()}
    out.update(lg_woba=lg_obp, scale=scale, runSB=ref["runSB"], runCS=ref["runCS"],
               r_pa=_g(t, "R") / _g(t, "PA") if _g(t, "PA") else ref["r_pa"],
               r_w=ref["r_w"], cfip=ref["cfip"])
    if t.get("ERA") is not None and t.get("IP"):
        ip = parse_ip(t["IP"])
        out["cfip"] = float(t["ERA"]) - (13 * _g(t, "HR") + 3 * (_g(t, "BB") + _g(t, "HBP"))
                                         - 2 * _g(t, "SO")) / ip
    return out


def batting_line(s, c, park_factor=1.0):
    w = woba(s, c)
    pa = _g(s, "PA") or (_g(s, "AB") + _g(s, "BB") + _g(s, "HBP") + _g(s, "SF"))
    line = {k: round(v, 3) for k, v in slash(s).items()}
    line.update(wOBA=round(w, 3), wRAA=round(wraa(w, pa, c), 1),
                **{"wRC+": round(wrc_plus(w, pa, c, park_factor))})
    return line


def pitching_line(s, c):
    ip = parse_ip(_g(s, "IP"))
    bf = _g(s, "BF")
    line = {"IP": round(ip, 3), "FIP": round(fip(s, c), 2),
            "K/9": round(9 * _g(s, "SO") / ip, 2), "BB/9": round(9 * _g(s, "BB") / ip, 2),
            "HR/9": round(9 * _g(s, "HR") / ip, 2)}
    if _g(s, "ER"):
        line["ERA"] = round(9 * _g(s, "ER") / ip, 2)
    if bf:
        line["K%"] = round(_g(s, "SO") / bf, 3)
        line["BB%"] = round(_g(s, "BB") / bf, 3)
    return line


_MLB_KEYS = {"plateAppearances": "PA", "atBats": "AB", "hits": "H", "doubles": "2B",
             "triples": "3B", "homeRuns": "HR", "baseOnBalls": "BB", "intentionalWalks": "IBB",
             "hitByPitch": "HBP", "sacFlies": "SF", "strikeOuts": "SO", "inningsPitched": "IP",
             "earnedRuns": "ER", "battersFaced": "BF", "runs": "R"}


def mlb_stat_to_counts(stat):
    """Map an MLB Stats API stat object (stats[0].splits[0].stat) to this module's keys."""
    return {v: stat[k] for k, v in _MLB_KEYS.items() if k in stat}


def fetch_mlb(person_id, season, group):
    url = (f"https://statsapi.mlb.com/api/v1/people/{int(person_id)}/stats"
           f"?stats=season&season={int(season)}&group={group}&sportId=1")
    with urllib.request.urlopen(url, timeout=20) as r:
        data = json.load(r)
    splits = data["stats"][0]["splits"] if data.get("stats") else []
    if not splits:
        raise LookupError(f"no {group} stats for person {person_id} in {season}")
    # Traded players get one split per team plus a combined one; the combined split has no team.
    combined = [s for s in splits if "team" not in s] or splits
    return mlb_stat_to_counts(combined[0]["stat"])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["batting", "pitching", "league"])
    p.add_argument("--season", type=int)
    p.add_argument("--stats", help="JSON counting stats")
    p.add_argument("--totals", help="JSON league totals (league mode, or to override --season)")
    p.add_argument("--mlb-person", type=int, help="MLB Stats API person id")
    p.add_argument("--park-factor", type=float, default=1.0)
    a = p.parse_args(argv)

    if a.mode == "league":
        if not a.totals:
            p.error("league mode needs --totals")
        print(json.dumps({k: round(v, 4) for k, v in league_constants(json.loads(a.totals)).items()}, indent=2))
        return 0
    if a.totals:
        c = league_constants(json.loads(a.totals))
    elif a.season:
        c = constants(a.season)
    else:
        p.error("give --season (MLB) or --totals (any other league)")
    if a.mlb_person:
        if not a.season:
            p.error("--mlb-person needs --season")
        s = fetch_mlb(a.mlb_person, a.season, "hitting" if a.mode == "batting" else "pitching")
    elif a.stats:
        s = json.loads(a.stats)
    else:
        s = json.load(sys.stdin)
    out = batting_line(s, c, a.park_factor) if a.mode == "batting" else pitching_line(s, c)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
