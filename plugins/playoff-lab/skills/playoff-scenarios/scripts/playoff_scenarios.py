#!/usr/bin/env python3
"""Enumerate playoff qualification paths from one supplied league snapshot. Python 3.9+."""

import argparse
from copy import deepcopy
from datetime import datetime
import html
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile


MAX_UNFORCED = 16
POLICY = {
    "standings": "overall",
    "ranking": "win_percentage",
    "existing_ties": "half_win",
    "future_ties": "excluded",
    "median_games": False,
}
COVERAGE = "The supplier declared the remaining schedule complete. Provider completeness is unverified."
INTERPRETATION = "Counts are unweighted scenario shares. Forecast probabilities require a separate model."


def fields(value, keys, path):
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    missing = sorted(set(keys) - value.keys())
    unknown = sorted(value.keys() - set(keys))
    if missing:
        raise ValueError(f"{path} missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} unsupported field(s): {', '.join(unknown)}")


def integer(value, field, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def label(value, field):
    if not isinstance(value, str) or not value or value != value.strip() or not value.isprintable():
        raise ValueError(f"{field} needs a nonempty single-line string without surrounding whitespace")
    return value


def identifier(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", value):
        raise ValueError(f"{field} needs an ID using letters, digits, dots, underscores, colons or hyphens")
    return value


def validate_scope(data):
    fields(data, ("league", "season", "source", "as_of", "completed_week", "regular_season_weeks",
                  "remaining_schedule_complete", "settings", "teams", "remaining_games"), "snapshot")
    for field in ("league", "season", "source"):
        label(data[field], field)
    stamp = label(data["as_of"], "as_of")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", stamp):
        raise ValueError("as_of must be an ISO timestamp with an explicit UTC offset")
    # Python 3.9 accepts millisecond and microsecond fractions. Normalize for parsing only.
    iso = re.sub(r"\.(\d+)", lambda match: "." + match[1].ljust(6, "0"), stamp)
    try:
        datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("as_of contains an invalid date or time") from None
    completed = integer(data["completed_week"], "completed_week")
    season_end = integer(data["regular_season_weeks"], "regular_season_weeks", 1)
    if completed > season_end:
        raise ValueError("completed_week exceeds regular_season_weeks")
    if data["remaining_schedule_complete"] is not True:
        raise ValueError("remaining_schedule_complete must be true for this calculation")


def validate_weekly_capacity(appearances, weeks, kind):
    """Check necessary pairing bounds using only each team's appearance count."""
    games = sum(appearances) // 2
    group_appearances = 0
    # The busiest k teams give the strongest bound for any group of size k.
    for size, count in enumerate(sorted(appearances, reverse=True), 1):
        group_appearances += count
        # Each game can account for one group appearance; any excess requires
        # both opponents within the group. At most floor(k / 2) can pair per week.
        required_internal_games = group_appearances - games
        if required_internal_games > weeks * (size // 2):
            raise ValueError(f"{kind} records require more games among {size} team(s) "
                             "than the completed weeks allow")


def validate_teams(data):
    teams = data["teams"]
    if not isinstance(teams, list) or len(teams) < 2:
        raise ValueError("teams must list at least two teams in the league")
    by_id = {}
    for i, team in enumerate(teams):
        path = f"teams[{i}]"
        fields(team, ("id", "name", "wins", "losses", "ties", "season_games"), path)
        team_id = identifier(team["id"], path + ".id")
        if team_id in by_id:
            raise ValueError(f"duplicate team ID: {team_id}")
        label(team["name"], path + ".name")
        played = sum(integer(team[f], path + "." + f) for f in ("wins", "losses", "ties"))
        season_games = integer(team["season_games"], path + ".season_games", 1)
        if played > data["completed_week"] or not played <= season_games <= data["regular_season_weeks"]:
            raise ValueError(f"{team_id} record or season_games conflicts with the regular-season weeks")
        by_id[team_id] = team
    wins, losses, ties = (sum(t[k] for t in teams) for k in ("wins", "losses", "ties"))
    if wins != losses or ties % 2:
        raise ValueError("league records must have equal wins and losses and an even tie total")
    decisive = [t["wins"] + t["losses"] for t in teams]
    tied = [t["ties"] for t in teams]
    all_appearances = [d + t for d, t in zip(decisive, tied)]
    for kind, appearances in (("overall", all_appearances), ("decisive", decisive), ("tied", tied)):
        validate_weekly_capacity(appearances, data["completed_week"], kind)
    return by_id


def validate_settings(settings, teams):
    fields(settings, (*POLICY, "playoff_slots", "tiebreak"), "settings")
    for key, expected in POLICY.items():
        actual = settings[key]
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError(f"settings.{key} must be {expected!r}")
    if integer(settings["playoff_slots"], "playoff_slots", 1) > len(teams):
        raise ValueError("playoff_slots exceeds the number of teams")
    tie = settings["tiebreak"]
    if not isinstance(tie, dict) or tie.get("mode") not in ("unresolved", "fixed_order"):
        raise ValueError("tiebreak.mode must be unresolved or fixed_order")
    if tie["mode"] == "unresolved":
        fields(tie, ("mode",), "tiebreak")
        return
    fields(tie, ("mode", "order"), "tiebreak")
    order = tie["order"]
    if (not isinstance(order, list) or len(order) != len(teams)
            or not all(isinstance(x, str) for x in order) or set(order) != teams.keys()):
        raise ValueError("fixed tiebreak order must contain every team ID exactly once")


def validate_schedule(data, teams):
    games = data["remaining_games"]
    if not isinstance(games, list):
        raise ValueError("remaining_games must be a list")
    game_ids = set()
    appearances = {team_id: set() for team_id in teams}
    for i, game in enumerate(games):
        path = f"remaining_games[{i}]"
        fields(game, ("id", "week", "home", "away"), path)
        game_id = identifier(game["id"], path + ".id")
        if game_id in game_ids:
            raise ValueError(f"duplicate game ID: {game_id}")
        game_ids.add(game_id)
        week = integer(game["week"], path + ".week", 1)
        if not data["completed_week"] < week <= data["regular_season_weeks"]:
            raise ValueError(f"{game_id} week must be after completed_week and within the regular season")
        home = identifier(game["home"], path + ".home")
        away = identifier(game["away"], path + ".away")
        if home == away or home not in teams or away not in teams:
            raise ValueError(f"{game_id} must name two different teams in this league")
        for team_id in (home, away):
            if week in appearances[team_id]:
                raise ValueError(f"{team_id} appears twice in week {week}")
            appearances[team_id].add(week)
    for team_id, team in teams.items():
        played = team["wins"] + team["losses"] + team["ties"]
        if played + len(appearances[team_id]) != team["season_games"]:
            raise ValueError(f"{team_id} record plus remaining schedule must equal its declared season_games")


def validate_winners(games, winners):
    matchups = {g["id"]: (g["home"], g["away"]) for g in games}
    forced = {}
    for game_id, winner in winners:
        if game_id not in matchups:
            raise ValueError(f"unknown remaining game in winner constraint: {game_id}")
        if winner not in matchups[game_id]:
            raise ValueError(f"{winner} is not playing in {game_id}")
        if game_id in forced and forced[game_id] != winner:
            raise ValueError(f"contradictory winner constraints for {game_id}")
        forced[game_id] = winner
    return forced


def analyze_scenarios(data, winners=()):
    """Return exact per-team bounds. A winner constraint is a (game ID, team ID) pair."""
    validate_scope(data)
    teams = validate_teams(data)
    validate_settings(data["settings"], teams)
    settings = deepcopy(data["settings"])
    validate_schedule(data, teams)
    games = data["remaining_games"]
    forced = validate_winners(games, winners)
    open_games = [g for g in games if g["id"] not in forced]
    if len(open_games) > MAX_UNFORCED:
        raise ValueError(f"at most {MAX_UNFORCED} unforced games can be enumerated; supply winner constraints")

    order = settings["tiebreak"].get("order", sorted(teams))
    index = {team_id: i for i, team_id in enumerate(order)}
    # A common denominator makes win percentages comparable as exact integers.
    denominator = math.lcm(*(team["season_games"] for team in teams.values()))
    scale = [denominator // teams[t]["season_games"] for t in order]
    scores = [(2 * teams[t]["wins"] + teams[t]["ties"]) * scale[i] for i, t in enumerate(order)]
    for winner in forced.values():
        scores[index[winner]] += 2 * scale[index[winner]]
    choices = [(index[g["home"]], index[g["away"]]) for g in open_games]
    slots = settings["playoff_slots"]
    fixed = settings["tiebreak"]["mode"] == "fixed_order"
    counts = [dict(id=t, name=teams[t]["name"], best_seed=len(teams), worst_seed=1,
                   guaranteed_qualifications=0, possible_qualifications=0) for t in order]

    for outcome in itertools.product(*choices):
        final = scores.copy()
        for winner in outcome:
            final[winner] += 2 * scale[winner]
        # Stable sorting preserves the declared priority within each equal-score group.
        ranked = sorted(range(len(order)), key=final.__getitem__, reverse=True)
        start = 1
        for _, group in itertools.groupby(ranked, key=final.__getitem__):
            tied = list(group)
            end = start + len(tied) - 1
            for rank, team in enumerate(tied, start):
                best, worst = (rank, rank) if fixed else (start, end)
                row = counts[team]
                row["best_seed"] = min(row["best_seed"], best)
                row["worst_seed"] = max(row["worst_seed"], worst)
                row["guaranteed_qualifications"] += int(worst <= slots)
                row["possible_qualifications"] += int(best <= slots)
            start = end + 1

    scenarios = 2 ** len(open_games)
    for row in counts:
        if row["guaranteed_qualifications"] == scenarios:
            row["status"] = "clinched"
        elif row["possible_qualifications"] == 0:
            row["status"] = "eliminated"
        else:
            row["status"] = "alive"

    return {
        **{k: data[k] for k in ("league", "season", "source", "as_of", "completed_week",
                                 "regular_season_weeks", "remaining_schedule_complete")},
        "coverage": COVERAGE, "settings": settings,
        "remaining_game_count": len(games), "unforced_game_count": len(open_games),
        "forced_winners": dict(sorted(forced.items())), "scenarios": scenarios,
        "interpretation": INTERPRETATION,
        "teams": sorted(counts, key=lambda row: (row["best_seed"], row["worst_seed"], row["id"])),
    }


def cell(value):
    """Keep user-supplied names, IDs and attribution readable as literal Markdown."""
    return re.sub(r"([\\|`*_\[\]~])", r"\\\1", html.escape(value, quote=False))


def render_markdown(report):
    settings = report["settings"]
    tie = settings["tiebreak"]
    tie_label = "unresolved"
    if tie["mode"] == "fixed_order":
        tie_label = "fixed scenario order, highest first — " + ", ".join(cell(t) for t in tie["order"])
    lines = [
        f"# {cell(report['league'])} · {cell(report['season'])} playoff scenarios", "",
        f"Through week {report['completed_week']} of {report['regular_season_weeks']}. "
        f"As of {cell(report['as_of'])}. Source: {cell(report['source'])}.", "",
        f"{report['remaining_game_count']} remaining games. {report['coverage']}", "",
        f"Top {settings['playoff_slots']} teams by overall win percentage. "
        "Past ties count as half a win. Every remaining game has one winner. "
        f"No median games. Tiebreak: {tie_label}.",
    ]
    if report["forced_winners"]:
        lines.extend(["", "Assumed winners: " + ", ".join(f"{cell(g)} = {cell(t)}"
                     for g, t in report["forced_winners"].items()) + "."])
    total = report["scenarios"]
    lines.extend(["", f"**{total} outcome scenarios.** {report['interpretation']}", "",
                  "| Team (ID) | Best seed | Worst seed | Guaranteed in | Possible in | Status |",
                  "|---|---:|---:|---:|---:|---|"])
    for row in report["teams"]:
        lines.append(f"| {cell(row['name'])} ({cell(row['id'])}) | {row['best_seed']} | {row['worst_seed']} "
                     f"| {row['guaranteed_qualifications']}/{total} | {row['possible_qualifications']}/{total} "
                     f"| {row['status']} |")
    lines.extend(["", "Guaranteed counts each outcome where every permitted tiebreak puts the team in. "
                  "Possible counts each outcome where at least one does. Status uses the declared assumptions."])
    return "\n".join(lines) + "\n"


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def reject_nonfinite(value):
    raise ValueError(f"invalid JSON number: {value}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="league snapshot JSON")
    parser.add_argument("--winner", action="append", default=[], metavar="GAME=TEAM",
                        help="force this game's winner; repeat for more games")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="write report to this file (default: stdout)")
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.exists() and args.output.samefile(args.input):
            raise ValueError("output must be different from the input snapshot")
        data = json.loads(args.input.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                          parse_constant=reject_nonfinite)
        winners = []
        for value in args.winner:
            if value.count("=") != 1:
                raise ValueError("--winner must use GAME=TEAM")
            winners.append(value.split("="))
        report = analyze_scenarios(data, winners)
        content = json.dumps(report, indent=2, ensure_ascii=False) + "\n" if args.format == "json" else render_markdown(report)
        if args.output is None:
            sys.stdout.write(content)
        else:
            if args.output.is_symlink() or (args.output.exists() and not args.output.is_file()):
                raise ValueError("output must be a regular file")
            temp = None
            try:
                with NamedTemporaryFile(mode="w", dir=args.output.parent, encoding="utf-8", delete=False) as f:
                    temp = Path(f.name)
                    f.write(content)
                os.replace(temp, args.output)
            finally:
                if temp is not None:
                    temp.unlink(missing_ok=True)
        return 0
    except (ValueError, OSError, RecursionError) as exc:
        print(f"playoff-scenarios: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
