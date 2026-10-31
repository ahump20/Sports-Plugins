#!/usr/bin/env python3
"""Build a source-attributed game packet from normalized observations. Python 3.9+."""

import argparse
import html
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

STATUSES = {"scheduled", "in_progress", "final", "postponed", "cancelled", "suspended"}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be nonblank text")
    return value.strip()


def stamp(value, label):
    try:
        parsed = datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timezone required")
        return parsed
    except (ValueError, TypeError) as error:
        raise ValueError(label + " must be an ISO timestamp with timezone") from error


def source_url(value):
    value = text(value, "source.url")
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or any(c.isspace() for c in value)
    ):
        raise ValueError(
            "source.url must be an HTTPS URL without credentials or whitespace"
        )
    return value


def build_packet(payload, now=None, max_age_hours=24):
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("source"), dict)
        or not isinstance(payload.get("games"), list)
    ):
        raise ValueError("Input requires source object and games array")
    if (
        isinstance(max_age_hours, bool)
        or not isinstance(max_age_hours, (int, float))
        or not math.isfinite(max_age_hours)
        or max_age_hours <= 0
    ):
        raise ValueError("max_age_hours must be positive and finite")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now requires a timezone")
    source = dict(payload["source"])
    source["url"] = source_url(source.get("url"))
    source["provider"] = text(source.get("provider"), "source.provider")
    fetched = stamp(source.get("fetched_at"), "source.fetched_at")
    age_hours = (now - fetched).total_seconds() / 3600
    freshness = (
        "future"
        if age_hours < -1 / 30
        else "stale" if age_hours > max_age_hours else "fresh"
    )
    warnings = []
    if freshness != "fresh":
        warnings.append(
            "Fetch timestamp is "
            + freshness
            + "; do not present this packet as current."
        )
    if source.get("data_as_of") is None:
        warnings.append(
            "Provider coverage time is unavailable; retrieval time does not establish season or game coverage."
        )
    else:
        coverage = stamp(source["data_as_of"], "source.data_as_of")
        if coverage > now:
            warnings.append(
                "Provider coverage time is in the future; verify the source clock."
            )
    games = []
    ids = set()
    for raw in payload["games"]:
        if not isinstance(raw, dict):
            raise ValueError("Each game must be an object")
        game_id = text(raw.get("id"), "game.id")
        if game_id in ids:
            raise ValueError("Duplicate game ID: " + game_id)
        ids.add(game_id)
        status = raw.get("status")
        if status not in STATUSES:
            raise ValueError("Unsupported game status: " + str(status))
        game = {"id": game_id, "status": status}
        for side in ("home", "away"):
            team = raw.get(side)
            if not isinstance(team, dict):
                raise ValueError(side + " must be an object")
            score = team.get("score")
            if score is not None and (type(score) is not int or score < 0):
                raise ValueError("Scores must be nonnegative integers or null")
            if status == "final" and score is None:
                raise ValueError("Final games require both scores")
            if status == "scheduled" and score is not None:
                raise ValueError(
                    "Scheduled games require null scores; do not convert missing scores to zero"
                )
            game[side] = {
                "name": text(team.get("name"), side + ".name"),
                "score": score,
            }
        if game["home"]["name"].casefold() == game["away"]["name"].casefold():
            raise ValueError("Home and away must be distinct teams")
        for field in ("venue", "start_time"):
            if raw.get(field) is not None:
                game[field] = text(raw[field], field)
                if field == "start_time":
                    stamp(raw[field], field)
        home, away = game["home"]["score"], game["away"]["score"]
        leader = (
            None
            if home is None or away is None or home == away
            else game["home" if home > away else "away"]["name"]
        )
        game.update(
            winner=leader if status == "final" else None,
            leader=leader if status == "in_progress" else None,
            margin=(
                abs(home - away)
                if status == "final" and home is not None and away is not None
                else None
            ),
        )
        games.append(game)
    return {
        "schema_version": "1.0.0",
        "generated_at": now.isoformat(),
        "source": source,
        "freshness": freshness,
        "warnings": warnings,
        "games": games,
    }


def render_markdown(packet):
    def safe(value):
        return html.escape(str(value)).replace("|", r"\|").replace("\n", " ")

    source = packet["source"]
    lines = [
        "# Game-day packet",
        "",
        "Provider: " + safe(source["provider"]),
        "Source: <" + source["url"] + ">",
        "Retrieved: " + safe(source["fetched_at"]),
        "Freshness: " + packet["freshness"],
        "",
    ]
    lines.extend("Notice: " + safe(w) for w in packet["warnings"])
    lines.append("")
    if not packet["games"]:
        lines.append("No games were returned in this source packet.")
    else:
        lines.extend(["| Away | Home | Status | Result |", "|---|---|---|---|"])
        for game in packet["games"]:

            def team(side):
                row = game[side]
                return safe(row["name"]) + (
                    ": " + str(row["score"])
                    if row["score"] is not None
                    else ": score unavailable"
                )

            result = (
                (safe(game["winner"]) + " won by " + str(game["margin"]))
                if game["winner"]
                else (
                    "Final tie"
                    if game["status"] == "final"
                    else (
                        safe(game["leader"]) + " leads; not final"
                        if game["leader"]
                        else "No final outcome"
                    )
                )
            )
            lines.append(
                "| "
                + " | ".join([team("away"), team("home"), game["status"], result])
                + " |"
            )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        help="Normalized JSON observations; no network calls are made",
    )
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output")
    parser.add_argument("--now", help="ISO time for reproducible offline checks")
    parser.add_argument("--max-age-hours", type=float, default=24)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        with Path(args.input).open(encoding="utf-8") as stream:
            raw = stream.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Input exceeds two million characters")

        def invalid_constant(value):
            raise ValueError("Nonfinite JSON number: " + value)

        payload = json.loads(raw, parse_constant=invalid_constant)
        packet = build_packet(
            payload, stamp(args.now, "--now") if args.now else None, args.max_age_hours
        )
        output = (
            json.dumps(packet, indent=2, allow_nan=False) + "\n"
            if args.format == "json"
            else render_markdown(packet)
        )
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 1 if args.strict and packet["freshness"] != "fresh" else 0
    except (OSError, ValueError, TypeError) as error:
        print("game-packet: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
