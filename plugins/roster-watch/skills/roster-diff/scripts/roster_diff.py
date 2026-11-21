#!/usr/bin/env python3
"""Compare two attributed roster snapshots offline."""

import argparse
import copy
from datetime import datetime
from ipaddress import IPv6Address
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import unicodedata
from urllib.parse import urlsplit


SCOPE = ("sport", "team", "season", "identity_namespace")
TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)
HOST_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")
OBSERVATIONS = {
    "absent_from_before": "Absent from the earlier snapshot declared complete",
    "absent_from_after": "Absent from the later snapshot declared complete",
    "before_coverage_unresolved": "Earlier snapshot was partial. Coverage is unresolved",
    "after_coverage_unresolved": "Later snapshot was partial. Coverage is unresolved",
}


def require_keys(value, required, optional, where):
    if type(value) is not dict:
        raise ValueError(f"{where} must be an object")
    missing = set(required).difference(value)
    if missing:
        raise ValueError(f"{where} missing required field(s): {', '.join(sorted(missing))}")
    if set(value).difference(required, optional):
        raise ValueError(f"{where} has unexpected field(s)")


def require_text(value, where):
    if type(value) is not str or not value or value != value.strip():
        raise ValueError(f"{where} must be a nonempty string without surrounding whitespace")


def parse_timestamp(value, where):
    error = f"{where} must be a valid timestamp with an explicit timezone"
    if type(value) is not str or not TIMESTAMP.fullmatch(value):
        raise ValueError(error)
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%f%z" if "." in value else "%Y-%m-%dT%H:%M:%S%z"
    try:
        return datetime.strptime(value, timestamp_format)
    except ValueError:
        raise ValueError(error) from None


def validate_source_url(value, where):
    error = f"{where} must be an absolute HTTP(S) URL without credentials"
    if type(value) is not str or any(
        c.isspace() or ord(c) < 32 or ord(c) == 127 or c in '\\<>"{}|^`' for c in value
    ) or re.search(r"%(?![A-Fa-f0-9]{2})", value):
        raise ValueError(error)
    try:
        url = urlsplit(value)
        if url.scheme not in ("http", "https") or not url.hostname:
            raise ValueError(error)
        if not re.fullmatch(r"(?:\[[^\]]+\]|[^:@\[\]]+)(?::[0-9]+)?", url.netloc):
            raise ValueError(error)
        if url.port is not None and url.port == 0:
            raise ValueError(error)
        if url.netloc.startswith("["):
            IPv6Address(url.hostname)
        else:
            hostname = url.hostname.encode("idna").decode("ascii").removesuffix(".")
            if not all(HOST_LABEL.fullmatch(label) for label in hostname.split(".")):
                raise ValueError(error)
    except ValueError:
        raise ValueError(error) from None


def validate_json_value(value, where):
    if type(value) is dict:
        for key, member in value.items():
            if type(key) is not str:
                raise ValueError(f"{where} must contain only string keys")
            validate_json_value(member, where)
    elif type(value) is list:
        for member in value:
            validate_json_value(member, where)
    elif type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"{where} must contain only finite JSON numbers")
    elif type(value) not in (str, bool, int, type(None)):
        raise ValueError(f"{where} must contain only JSON values")


def validate_snapshot(snapshot, side):
    require_keys(snapshot, (*SCOPE, "observed_at", "source", "players"), (), side)
    for key in SCOPE:
        require_text(snapshot[key], f"{side}.{key}")
    observed_at = parse_timestamp(snapshot["observed_at"], f"{side}.observed_at")
    source = snapshot["source"]
    require_keys(source, ("url", "completeness"), ("synthetic",), f"{side}.source")
    validate_source_url(source["url"], f"{side}.source.url")
    completeness = source["completeness"]
    if type(completeness) is not str or completeness not in ("complete", "partial"):
        raise ValueError(f"{side}.source.completeness must be 'complete' or 'partial'")
    if "synthetic" in source and type(source["synthetic"]) is not bool:
        raise ValueError(f"{side}.source.synthetic must be a boolean")

    players = snapshot["players"]
    if type(players) is not list:
        raise ValueError(f"{side}.players must be an array")
    indexed = {}
    for index, player in enumerate(players):
        where = f"{side}.players[{index}]"
        require_keys(player, ("id", "name"), ("fields",), where)
        require_text(player["id"], f"{where}.id")
        require_text(player["name"], f"{where}.name")
        if player["id"] in indexed:
            raise ValueError(f"{where}.id is a duplicate player ID")
        if "fields" in player:
            if type(player["fields"]) is not dict:
                raise ValueError(f"{where}.fields must be an object")
            try:
                validate_json_value(player["fields"], f"{where}.fields")
            except RecursionError:
                raise ValueError(f"{where}.fields must be a finite JSON object") from None
        indexed[player["id"]] = player
    return observed_at, indexed


def field_value(fields, key):
    return {"present": True, "value": fields[key]} if key in fields else {"present": False}


def field_changes(before, after):
    changes = []
    if before["name"] != after["name"]:
        changes.append({
            "path": ["name"],
            "before": field_value(before, "name"),
            "after": field_value(after, "name"),
        })
    old_fields = before.get("fields", {})
    new_fields = after.get("fields", {})
    for key in sorted(old_fields.keys() | new_fields.keys()):
        old = field_value(old_fields, key)
        new = field_value(new_fields, key)
        # JSON serialization compares nested values without Python's bool/int coercion.
        if json.dumps(old, sort_keys=True) != json.dumps(new, sort_keys=True):
            changes.append({"path": ["fields", key], "before": old, "after": new})
    return changes


def compare_rosters(before, after):
    """Return an observation report from two JSON-compatible snapshot dictionaries."""
    earlier, before_players = validate_snapshot(before, "before")
    later, after_players = validate_snapshot(after, "after")
    for key in SCOPE:
        if before[key] != after[key]:
            raise ValueError(f"before and after {key} must match")
    if later < earlier:
        raise ValueError("after.observed_at is earlier than before.observed_at")

    before_ids, after_ids = before_players.keys(), after_players.keys()
    shared_ids = before_ids & after_ids
    changed = []
    for player_id in sorted(shared_ids):
        old, new = before_players[player_id], after_players[player_id]
        fields = field_changes(old, new)
        if fields:
            changed.append({"id": player_id, "before": old, "after": new, "fields": fields})

    before_partial = before["source"]["completeness"] == "partial"
    after_partial = after["source"]["completeness"] == "partial"
    before_only = [
        {
            "record": before_players[player_id],
            "comparison": "after_coverage_unresolved" if after_partial else "absent_from_after",
        }
        for player_id in sorted(before_ids - after_ids)
    ]
    after_only = [
        {
            "record": after_players[player_id],
            "comparison": "before_coverage_unresolved" if before_partial else "absent_from_before",
        }
        for player_id in sorted(after_ids - before_ids)
    ]
    limitations = [
        "Counts describe supplied snapshots and their declared coverage. Claims of transfer, "
        "injury, eligibility, departure or cause require independent evidence.",
        "Different IDs are separate source records, including identical names. A source ID change "
        "can produce two observed-only records for one player.",
    ]
    if before_partial:
        limitations.append("The earlier snapshot is partial. Coverage for IDs observed only later is unresolved.")
    if after_partial:
        limitations.append("The later snapshot is partial. Coverage for IDs observed only earlier is unresolved.")
    if any(change["fields"][0]["path"] == ["name"] for change in changed):
        limitations.append("Confirm a name change under the same ID with the source in case the ID was reused.")

    return copy.deepcopy({
        "scope": {key: before[key] for key in SCOPE},
        "snapshots": {
            side: {key: snapshot[key] for key in ("observed_at", "source")}
            for side, snapshot in (("before", before), ("after", after))
        },
        "counts": {
            "before": len(before_ids),
            "after": len(after_ids),
            "observed_only_before": len(before_only),
            "observed_only_after": len(after_only),
            "changed": len(changed),
            "unchanged": len(shared_ids) - len(changed),
        },
        "observed_only_before": before_only,
        "observed_only_after": after_only,
        "changed": changed,
        "limitations": limitations,
    })


def markdown_value(value):
    """Wrap serialized data in a code span too long for its contents to close."""
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    visible = "".join(
        json.dumps(c)[1:-1] if unicodedata.category(c) in {"Cc", "Cf", "Cs", "Zl", "Zp"} else c
        for c in serialized
    )
    fence = "`" * (1 + max((len(run) for run in re.findall(r"`+", visible)), default=0))
    return f"{fence} {visible} {fence}" if "`" in visible else f"{fence}{visible}{fence}"


def markdown_field(value):
    return markdown_value(value["value"]) if value["present"] else "(missing)"


def render_markdown(report):
    scope = report["scope"]
    lines = [
        "# Roster comparison", "",
        " · ".join(markdown_value(scope[key]) for key in ("team", "sport", "season")),
        f"Identity namespace {markdown_value(scope['identity_namespace'])}", "",
    ]
    for side, label in (("before", "Earlier"), ("after", "Later")):
        snapshot = report["snapshots"][side]
        source = snapshot["source"]
        synthetic = " · **SYNTHETIC**" if source.get("synthetic") else ""
        lines.append(
            f"- **{label}** {markdown_value(snapshot['observed_at'])} · "
            f"{source['completeness']}{synthetic} · {markdown_value(source['url'])}"
        )
    counts = report["counts"]
    lines.extend([
        "", f"{counts['before']} earlier records, {counts['after']} later records, "
        f"{counts['unchanged']} unchanged.",
    ])
    for side, label in (("before", "earlier"), ("after", "later")):
        rows = report[f"observed_only_{side}"]
        lines.extend(["", f"## Observed only in the {label} snapshot ({len(rows)})", ""])
        if not rows:
            lines.append("None observed.")
        for row in rows:
            record = row["record"]
            lines.append(
                f"- {markdown_value(record['name'])} (ID {markdown_value(record['id'])}). "
                f"{OBSERVATIONS[row['comparison']]}."
            )
            if record.get("fields"):
                lines.append(f"  - Fields {markdown_value(record['fields'])}")
    lines.extend(["", f"## Changed records ({counts['changed']})", ""])
    if not report["changed"]:
        lines.append("None observed.")
    for change in report["changed"]:
        lines.append(f"- {markdown_value(change['after']['name'])} (ID {markdown_value(change['id'])})")
        for field in change["fields"]:
            path = field["path"]
            label = "Player name" if path == ["name"] else f"Field {markdown_value(path[1])}"
            lines.append(f"  - {label}. {markdown_field(field['before'])} → {markdown_field(field['after'])}")
    lines.extend(["", "## Limits", "", *(f"- {item}" for item in report["limitations"])])
    return "\n".join(lines) + "\n"


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON number {value}")


def read_snapshot(path, side):
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    except (OSError, ValueError, RecursionError) as error:
        raise ValueError(f"{side} snapshot: {error}") from None


def write_report(output, content, inputs):
    output = output.parent.resolve() / output.name
    for source in inputs:
        if output.resolve() == source.resolve() or (output.exists() and output.samefile(source)):
            raise ValueError("--output must differ from both input snapshots")
    try:
        mode = output.lstat().st_mode
    except FileNotFoundError:
        mode = None
    if mode is not None and not stat.S_ISREG(mode):
        raise ValueError("--output must be a regular file or a new path")
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".roster-report-") as directory:
        temporary = Path(directory) / "report"
        temporary.write_text(content, encoding="utf-8")
        if mode is not None:
            temporary.chmod(mode & 0o777)
        os.replace(temporary, output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path, help="earlier roster snapshot JSON")
    parser.add_argument("--after", required=True, type=Path, help="later roster snapshot JSON")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path, help="write to a separate file instead of stdout")
    args = parser.parse_args(argv)
    try:
        before = read_snapshot(args.before, "before")
        after = read_snapshot(args.after, "after")
        report = compare_rosters(before, after)
        if args.format == "json":
            content = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        else:
            content = render_markdown(report)
        if args.output is None:
            sys.stdout.write(content)
        else:
            write_report(args.output, content, (args.before, args.after))
    except (OSError, ValueError, RuntimeError) as error:
        print(f"roster-diff: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
