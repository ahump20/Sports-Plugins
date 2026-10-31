#!/usr/bin/env python3
"""Audit an evidence ledger without claiming to verify source truth. Python 3.9+."""

import argparse
import html
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

KINDS = {"fact", "quote", "calculation", "opinion"}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be nonblank text")
    return value.strip()


def stamp(value):
    try:
        result = datetime.fromisoformat(text(value, "timestamp").replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("timezone required")
        return result
    except (ValueError, TypeError) as error:
        raise ValueError(
            "Source timestamps require ISO date/time and timezone"
        ) from error


def calculate(spec):
    if not isinstance(spec, dict):
        raise ValueError("calculation object required")
    inputs = spec.get("inputs")
    expected = spec.get("value")
    operation = spec.get("operation")

    def finite(value):
        return type(value) in (int, float) and math.isfinite(value)

    if (
        not isinstance(inputs, list)
        or not inputs
        or not all(finite(v) for v in inputs)
        or not finite(expected)
    ):
        raise ValueError("Calculation values must be finite numbers")
    if operation == "sum":
        actual = sum(inputs)
    elif operation in ("difference", "ratio", "percentage") and len(inputs) == 2:
        if operation == "difference":
            actual = inputs[0] - inputs[1]
        elif inputs[1] == 0:
            raise ValueError("Division by zero is undefined, not zero")
        else:
            actual = inputs[0] / inputs[1] * (100 if operation == "percentage" else 1)
    else:
        raise ValueError(
            "Supported operations: sum, two-input difference, ratio, percentage"
        )
    precision = spec.get("precision", 6)
    if type(precision) is not int or not 0 <= precision <= 6:
        raise ValueError("precision must be an integer from zero to six")
    if not math.isfinite(actual) or not math.isclose(
        actual, expected, rel_tol=0, abs_tol=0.5 * 10**-precision + 1e-12
    ):
        raise ValueError("Claimed result does not match the supplied arithmetic")
    return actual


def audit_ledger(payload, now=None, max_age_hours=24):
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("sources"), list)
        or not isinstance(payload.get("claims"), list)
    ):
        raise ValueError("Input requires sources and claims arrays")
    if (
        type(max_age_hours) not in (int, float)
        or not math.isfinite(max_age_hours)
        or max_age_hours <= 0
    ):
        raise ValueError("max_age_hours must be positive and finite")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now requires a timezone")
    sources = {}
    dates = {}
    for raw in payload["sources"]:
        if not isinstance(raw, dict):
            raise ValueError("Each source must be an object")
        source_id = text(raw.get("id"), "source.id")
        if source_id in sources:
            raise ValueError("Duplicate source ID: " + source_id)
        url = text(raw.get("url"), "source.url")
        parsed = urlparse(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or any(c.isspace() for c in url)
        ):
            raise ValueError(
                "Source URLs require HTTPS without credentials or whitespace"
            )
        text(raw.get("title"), "source.title")
        dates[source_id] = stamp(raw.get("retrieved_at"))
        if raw.get("published_at") is not None:
            stamp(raw["published_at"])
        if raw.get("excerpt") is not None and not isinstance(raw["excerpt"], str):
            raise ValueError("Source excerpt must be text")
        sources[source_id] = dict(raw)
    issues = []
    claims = []
    ids = set()
    for raw in payload["claims"]:
        if not isinstance(raw, dict):
            raise ValueError("Each claim must be an object")
        claim_id = text(raw.get("id"), "claim.id")
        statement = text(raw.get("text"), "claim.text")
        if claim_id in ids:
            raise ValueError("Duplicate claim ID: " + claim_id)
        ids.add(claim_id)
        kind = raw.get("kind")
        scope = raw.get("temporal_scope", "current")
        if kind not in KINDS or scope not in ("current", "historical"):
            raise ValueError("Unsupported claim kind or temporal_scope")
        source_ids = raw.get("source_ids", [])
        if not isinstance(source_ids, list) or not all(
            isinstance(s, str) for s in source_ids
        ):
            raise ValueError("source_ids must be strings in an array")
        problems = []
        if kind != "opinion" and not source_ids:
            problems.append("Factual claims require source IDs")
        for source_id in source_ids:
            if source_id not in sources:
                problems.append("Unknown source ID: " + source_id)
                continue
            age = (now - dates[source_id]).total_seconds() / 3600
            if age < -1 / 30:
                problems.append(
                    "Source retrieval timestamp is in the future: " + source_id
                )
            elif kind != "opinion" and scope == "current" and age > max_age_hours:
                problems.append(
                    "Current claim relies on a stale retrieval: " + source_id
                )
        if kind == "quote" and not any(
            statement in sources[s].get("excerpt", "")
            for s in source_ids
            if s in sources
        ):
            problems.append("Quote does not appear exactly in any cited source excerpt")
        computed = None
        if kind == "calculation":
            try:
                computed = calculate(raw.get("calculation"))
            except (ValueError, OverflowError) as error:
                problems.append(str(error))
        for message in problems:
            issues.append({"claim_id": claim_id, "message": message})
        claim = dict(raw)
        claim.update(
            text=statement,
            status=(
                "unresolved"
                if problems
                else "opinion" if kind == "opinion" else "documented"
            ),
        )
        if computed is not None:
            claim["computed_result"] = computed
        claims.append(claim)
    if not claims:
        issues.append(
            {
                "claim_id": None,
                "message": "No claims supplied; an empty ledger is not complete",
            }
        )
    return {
        "schema_version": "1.0.0",
        "generated_at": now.isoformat(),
        "complete": not issues,
        "limitation": "Documentation and arithmetic checks only; this tool does not verify source truth, quote authenticity, or whether a citation entails a claim. Retrieval freshness does not prove data coverage. Human source review is required before publication.",
        "sources": list(sources.values()),
        "claims": claims,
        "issues": issues,
    }


def render_markdown(result):
    def safe(value):
        return html.escape(str(value)).replace("|", r"\|").replace("\n", " ")

    lines = [
        "# Editorial evidence ledger",
        "",
        "Documentation status: " + ("complete" if result["complete"] else "unresolved"),
        "",
        result["limitation"],
        "",
        "| Claim | Kind | Status | Sources |",
        "|---|---|---|---|",
    ]
    for claim in result["claims"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    safe(claim["id"] + ": " + claim["text"]),
                    claim["kind"],
                    claim["status"],
                    safe(", ".join(claim.get("source_ids", []))),
                ]
            )
            + " |"
        )
    if result["issues"]:
        lines.extend(["", "## Unresolved"])
        lines.extend(
            "- " + safe(issue["claim_id"] or "ledger") + ": " + safe(issue["message"])
            for issue in result["issues"]
        )
    lines.extend(["", "## Sources"])
    for source in result["sources"]:
        lines.append(
            safe(source["id"] + ": " + source["title"])
            + " <"
            + source["url"]
            + "> | retrieved "
            + safe(source["retrieved_at"])
        )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-age-hours", type=float, default=24)
    parser.add_argument("--now")
    args = parser.parse_args(argv)
    try:
        with Path(args.input).open(encoding="utf-8") as stream:
            raw = stream.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Input exceeds two million characters")

        def invalid_constant(value):
            raise ValueError("Nonfinite JSON number: " + value)

        result = audit_ledger(
            json.loads(raw, parse_constant=invalid_constant),
            stamp(args.now) if args.now else None,
            args.max_age_hours,
        )
        output = (
            json.dumps(result, indent=2, allow_nan=False) + "\n"
            if args.format == "json"
            else render_markdown(result)
        )
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 1 if args.strict and not result["complete"] else 0
    except (OSError, ValueError, TypeError) as error:
        print("evidence-ledger: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
