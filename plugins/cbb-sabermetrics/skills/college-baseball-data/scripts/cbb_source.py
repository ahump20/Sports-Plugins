#!/usr/bin/env python3
"""Inspect season-specific college baseball HTML without inventing missing data.

Python 3.9+, standard library only. This retrieves source observations, not a
complete NCAA database. The caller must choose an authentic official source.
"""

import argparse
import hashlib
import http.client
import ipaddress
import json
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


MAX_BYTES = 8 * 1024 * 1024
MAX_COLUMNS = 128
MAX_ROWS = 10000
MAX_TABLES = 80
MAX_NODES = 150000
DOWNLOAD_SECONDS = 30
KINDS = ("stats", "roster", "schedule", "standings")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_TEXT = {"script", "style", "template", "noscript", "svg"}
BLOCK_TEXT = {"address", "article", "aside", "blockquote", "caption", "dd", "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul"}
KIND_TERMS = {
    "stats": r"\b(?:stats|statistics)\b",
    "roster": r"\broster\b",
    "schedule": r"\bschedule\b",
    "standings": r"\bstandings\b",
}


class SourceError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def clean(text):
    return " ".join(text.split())


class Element:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.parent = parent
        self.children = []

    def _text(self):
        if self.tag in SKIP_TEXT:
            return ""
        if self.tag == "br":
            return "\n"
        text = "".join(c if isinstance(c, str) else c._text() for c in self.children)
        return "\n" + text + "\n" if self.tag in BLOCK_TEXT else text

    def text(self):
        return clean(self._text())

    def descendants(self, tag=None):
        for child in self.children:
            if not isinstance(child, str):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.descendants(tag)

    def ancestor(self, tag):
        node = self.parent
        while node is not None:
            if node.tag == tag:
                return node
            node = node.parent
        return None


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        if len(self.nodes) >= MAX_NODES or len(self.stack) > 256:
            raise SourceError("unsupported_markup", "HTML exceeds the supported structural limits")
        node = Element(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not any(node.tag in SKIP_TEXT for node in self.stack):
            self.stack[-1].children.append(data)


def validate_url(url, resolve=False):
    """Allow ordinary public HTTP(S) sources, including checked redirects."""
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise SourceError("invalid_url", "Invalid source URL") from error
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SourceError("invalid_url", "Source URL must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or port not in (None, 80, 443):
        raise SourceError("invalid_url", "Credentials and nonstandard ports are not accepted in source URLs")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise SourceError("invalid_url", "Source must use a public internet host")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None and not literal.is_global:
        raise SourceError("invalid_url", "Source must use a public internet address")
    # A configured outbound proxy resolves remote names itself. Some managed
    # environments intentionally provide no direct public DNS; keep their normal
    # urllib route rather than bypassing the proxy or claiming local DNS checked it.
    proxies = urllib.request.getproxies()
    through_proxy = bool(proxies.get(parsed.scheme)) and not urllib.request.proxy_bypass(host)
    if resolve and not through_proxy:
        try:
            addresses = socket.getaddrinfo(host, port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
        except socket.gaierror as error:
            raise SourceError("source_unavailable", "Source host could not be resolved") from error
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            raise SourceError("invalid_url", "Source host resolves to a non-public address")
    return url


class PublicRedirects(urllib.request.HTTPRedirectHandler):
    max_redirections = 3
    max_repeats = 2

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        validate_url(newurl, resolve=True)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def read_body(response, deadline):
    """Bound even a trickled read/chunk header by shutting down its HTTP socket."""
    def finish(chunks):
        body = b"".join(chunks)
        remaining_length = getattr(response, "length", None)
        if isinstance(remaining_length, int) and remaining_length > 0:
            raise http.client.IncompleteRead(body, remaining_length)
        return body

    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise SourceError("source_unavailable", "Source exceeded the bounded download time")
    if response.fp is None:
        return finish([])
    transport = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
    if transport is None or not callable(getattr(transport, "shutdown", None)):
        raise SourceError("source_unavailable", "Source response cannot enforce a bounded HTTP read")
    expired = threading.Event()

    def abort():
        expired.set()
        try:
            transport.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    timer = threading.Timer(remaining, abort)
    timer.daemon = True
    timer.start()
    try:
        chunks, total = [], 0
        while True:
            remaining = deadline - time.monotonic()
            if expired.is_set() or remaining <= 0:
                raise SourceError("source_unavailable", "Source exceeded the bounded download time")
            # HTTPResponse closes its file/socket as soon as a Content-Length
            # body is consumed, before a subsequent read can return EOF.
            if response.fp is None:
                return finish(chunks)
            transport.settimeout(min(10, remaining))
            try:
                # read1 returns after one buffered/socket read, rather than
                # waiting to accumulate 64 KiB while a peer trickles bytes.
                chunk = response.read1(min(65536, MAX_BYTES + 1 - total))
            except (OSError, http.client.HTTPException):
                if expired.is_set() or time.monotonic() >= deadline:
                    raise SourceError("source_unavailable", "Source exceeded the bounded download time")
                raise
            if expired.is_set() or time.monotonic() >= deadline:
                raise SourceError("source_unavailable", "Source exceeded the bounded download time")
            if not chunk:
                return finish(chunks)
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_BYTES:
                raise SourceError("source_too_large", "Source exceeds the 8 MiB download limit")
    finally:
        timer.cancel()


def fetch_source(url):
    validate_url(url, resolve=True)
    request = urllib.request.Request(url, headers={
        "User-Agent": "Sports-Plugins/college-baseball-source (read-only source inspection)",
        "Accept": "text/html, application/xhtml+xml",
        "Accept-Encoding": "identity",
    })
    started = time.monotonic()
    try:
        with urllib.request.build_opener(PublicRedirects()).open(request, timeout=10) as response:
            final_url = validate_url(response.geturl(), resolve=True)
            media_type = response.headers.get_content_type()
            if media_type not in ("text/html", "application/xhtml+xml"):
                raise SourceError("unsupported_format", "Source is %s; this helper supports HTML, not PDFs or JSON" % media_type)
            length = response.headers.get("Content-Length")
            if length and length.isdigit() and int(length) > MAX_BYTES:
                raise SourceError("source_too_large", "Source exceeds the 8 MiB download limit")
            raw = read_body(response, started + DOWNLOAD_SECONDS)
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                html = raw.decode(charset)
            except (LookupError, UnicodeError) as error:
                raise SourceError("unsupported_encoding", "Source HTML could not be decoded without replacing characters") from error
            return html, {
                "requested_url": url,
                "final_url": final_url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "http_status": response.status,
                "content_type": media_type,
                "content_sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "input_mode": "http",
            }
    except urllib.error.HTTPError as error:
        raise SourceError("source_unavailable", "Source returned HTTP %s; no data was inferred" % error.code) from error
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as error:
        raise SourceError("source_unavailable", "Source request failed: %s" % error) from error


def season_observations(document):
    evidence = []
    for node in document.nodes:
        if node.tag not in ("title", "h1", "h2"):
            continue
        text = node.text()
        if not re.search(r"\bbaseball\b", text, re.I):
            continue
        # Academic-year labels are preserved and explicitly resolve to end year.
        ranges = list(re.finditer(r"\b((?:18|19|20|21)\d{2})\s*[-–/]\s*(\d{2}|(?:18|19|20|21)\d{2})\b", text))
        covered = set()
        for match in ranges:
            start = int(match.group(1))
            end_text = match.group(2)
            end = int(end_text) if len(end_text) == 4 else (start // 100) * 100 + int(end_text)
            if len(end_text) == 2 and end < start:
                end += 100
            # Never reinterpret an invalid range as its standalone first year.
            covered.update(range(match.start(), match.end()))
            if end == start + 1:
                evidence.append({"element": node.tag, "text": text, "season": end, "interpretation": "academic-year end"})
            else:
                evidence.append({"element": node.tag, "text": text, "season": None, "interpretation": "ambiguous-year-range"})
        for match in re.finditer(r"\b(?:18|19|20|21)\d{2}\b", text):
            if match.start() not in covered:
                evidence.append({"element": node.tag, "text": text, "season": int(match.group())})
    return evidence


def source_links(node, base):
    links, seen = [], set()
    for anchor in node.descendants("a"):
        href = anchor.attrs.get("href")
        if not href:
            continue
        url = urllib.parse.urljoin(base, href)
        if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
            continue
        label = anchor.text() or anchor.attrs.get("aria-label") or anchor.attrs.get("title") or None
        item = (url, label)
        if item not in seen:
            links.append({"url": url, "label": label})
            seen.add(item)
    return links


def expand_table(table, index, heading, base):
    if any(True for _ in table.descendants("table")):
        raise SourceError("unsupported_markup", "Nested table requires separate source review")
    raw_rows = list(table.descendants("tr"))
    if len(raw_rows) > MAX_ROWS:
        raise SourceError("unsupported_markup", "Table exceeds supported row limit")
    matrix, sections, spans, links, pending = [], [], [], [], {}
    for row_index, row in enumerate(raw_rows):
        if row.ancestor("tr") is not None:
            raise SourceError("unsupported_markup", "Nested or implicitly closed table rows require browser parsing")
        cells = [n for n in row.descendants() if n.tag in ("th", "td") and n.ancestor("tr") is row]
        if any(cell.ancestor("td") is not None or cell.ancestor("th") is not None for cell in cells):
            raise SourceError("unsupported_markup", "Nested or implicitly closed table cells require browser parsing")
        grid = {}
        next_pending = {}
        for column, (value, remaining) in pending.items():
            grid[column] = value
            if remaining > 1:
                next_pending[column] = (value, remaining - 1)
        column = 0
        for cell in cells:
            while column in grid:
                column += 1
            try:
                colspan, rowspan = int(cell.attrs.get("colspan", 1)), int(cell.attrs.get("rowspan", 1))
            except (ValueError, TypeError) as error:
                raise SourceError("unsupported_markup", "Invalid table span") from error
            if colspan < 1 or rowspan < 1 or column + colspan > MAX_COLUMNS or row_index + rowspan > len(raw_rows):
                raise SourceError("unsupported_markup", "Unsupported or out-of-bounds table span")
            value = cell.text() or None
            for target in range(column, column + colspan):
                if target in grid:
                    raise SourceError("unsupported_markup", "Overlapping table spans cannot be aligned safely")
                grid[target] = value
                if rowspan > 1:
                    next_pending[target] = (value, rowspan - 1)
            if colspan != 1 or rowspan != 1:
                spans.append({"row": row_index, "column": column, "rowspan": rowspan, "colspan": colspan})
            for link in source_links(cell, base):
                links.append(dict(link, row=row_index, column=column))
            column += colspan
        pending = next_pending
        width = max(grid, default=-1) + 1
        if width > MAX_COLUMNS:
            raise SourceError("unsupported_markup", "Table exceeds supported column limit")
        matrix.append([grid.get(c) for c in range(width)])
        if row.ancestor("thead") is not None:
            sections.append("header")
        elif row.ancestor("tfoot") is not None:
            sections.append("footer")
        elif cells and all(c.tag == "th" for c in cells) and all(s == "header" for s in sections):
            sections.append("header")
        elif "s-table-body__row--ad" in row.attrs.get("class", "").split() or any(n.attrs.get("data-test-id") == "s-advert__root" for n in row.descendants()):
            sections.append("advertisement")
        elif len(cells) == 1 and int(cells[0].attrs.get("colspan", 1)) > 1:
            sections.append("section")
        else:
            sections.append("body")
    width = max((len(row) for row in matrix), default=0)
    if width == 0:
        raise SourceError("unsupported_markup", "Table contains no source cells")
    ragged = any(len(row) != width for row in matrix)
    for row in matrix:
        row.extend([None] * (width - len(row)))
    captions = [n.text() for n in table.descendants("caption")]
    headers = [row for row, section in zip(matrix, sections) if section == "header"]
    group_heading = headers[0][0] if len(headers) > 1 and headers[0][0] and len(set(headers[0])) == 1 else None
    return {
        "source_table_index": index,
        "heading": group_heading or heading,
        "heading_source": "column_group_header" if group_heading else "nearest_preceding_heading",
        "caption": " ".join(captions) or None,
        "column_count": width,
        "header_rows": headers,
        "rows": [row for row, section in zip(matrix, sections) if section != "header"],
        "row_sections": [section for section in sections if section != "header"],
        "spans": spans,
        "links": links,
        "warnings": ["Ragged source rows were padded with null; confirm alignment before calculations."] if ragged else [],
    }


def sidearm_schedule(document, base):
    games, reported_record = [], {}
    fields = {
        "opponent": "s-game-card-standard__header-team-opponent-link",
        "date_text": "s-game-card-standard__header-game-date-details",
        "result_text": "s-game-card-standard__header-game-team-score",
        "result_note": "s-game-card-standard__header-game-post-score",
        "facility": "s-game-card-facility-and-location__standard-facility-title",
        "location": "s-game-card-facility-and-location__standard-location-details",
    }
    for node in document.nodes:
        marker = node.attrs.get("data-test-id", "")
        if marker == "s-game-card-standard__root":
            descendants = list(node.descendants())
            game = {}
            for name, test_id in fields.items():
                values = list(dict.fromkeys(n.text() for n in descendants if n.attrs.get("data-test-id") == test_id and n.text()))
                game[name] = values[0] if len(values) == 1 else None
                if len(values) > 1:
                    game[name + "_conflicting_values"] = values
            game["links"] = source_links(node, base)
            games.append(game)
        match = re.fullmatch(r"schedule-record__(overall|conference|home|away|neutral)-(win|loss|tie)-value", marker)
        if match:
            category, value_kind = match.groups()
            text = node.text()
            entry = reported_record.setdefault(category, {"wins": None, "losses": None, "ties": None})
            key = {"win": "wins", "loss": "losses", "tie": "ties"}[value_kind]
            label = {"win": "Wins", "loss": "Losses", "tie": "Ties"}[value_kind]
            number = re.fullmatch(r"(?:%s\s*)?(\d+)" % label, text, re.I)
            value = int(number.group(1)) if number else None
            if entry[key] is not None and entry[key] != value:
                raise SourceError("source_conflict", "Conflicting reported record values on source page")
            entry[key] = value
    return games, reported_record


def inspect_html(html, source, season, kind, team=None, division=None):
    document = Document()
    document.feed(html)
    document.close()
    titles = [node.text() for node in document.nodes if node.tag in ("title", "h1")]
    evidence = season_observations(document)
    observed = sorted({item["season"] for item in evidence if item["season"] is not None})
    packet = {
        "schema_version": 1,
        "status": "ok",
        "source": dict(source, title=next((n.text() for n in document.nodes if n.tag == "title"), None),
                       as_of=None, authority="Caller must verify this is the relevant official school, conference or association source."),
        "requested_scope": {"season": season, "kind": kind, "team": team, "division": division},
        "season": {"requested": season, "observed": observed, "evidence": evidence},
        "identity_verification": "Team and division arguments are requested scope, not source-verified identifiers.",
        "coverage": {"completeness": "unknown", "population": "HTML tables and supported schedule cards on this one page",
                     "includes_all_tabs": False, "includes_all_pages": False},
        "tables": [],
        "schedule_games": [],
        "reported_record": {},
        "rejected_tables": [],
        "warnings": [
            "Retrieval time is not a statistical cutoff. Source cutoff is unknown unless separately established.",
            "Source values are transcribed, not independently authenticated; conflicting summary panels must be checked against detailed totals.",
            "Empty cells are null; other source tokens, including zero, dash and baseball innings notation, are preserved as text.",
        ],
    }
    if any(item["season"] is None for item in evidence):
        packet.update(status="season_ambiguous", error="Source has a nonconsecutive or invalid baseball season range")
        return packet
    if not observed:
        packet.update(status="season_unverified", error="No explicit baseball season in the page title or main headings; URL/request year is insufficient")
        return packet
    if len(observed) != 1:
        packet.update(status="season_ambiguous", error="Page headings identify conflicting baseball seasons")
        return packet
    if observed[0] != season:
        packet.update(status="season_mismatch", error="Source identifies season %s, not requested season %s" % (observed[0], season))
        return packet
    matching_titles = [text for text in titles if re.search(r"\bbaseball\b", text, re.I)]
    declared_kinds = {k for k, pattern in KIND_TERMS.items() if any(re.search(pattern, text, re.I) for text in matching_titles)}
    if declared_kinds and kind not in declared_kinds:
        packet.update(status="source_kind_mismatch", error="Source title describes %s, not %s" % (", ".join(sorted(declared_kinds)), kind))
        return packet
    heading, table_count = None, 0
    for node in document.nodes:
        if node.tag in ("h1", "h2", "h3", "h4"):
            heading = node.text() or heading
        if node.tag == "table":
            if table_count >= MAX_TABLES:
                raise SourceError("unsupported_markup", "Source exceeds supported table limit")
            try:
                packet["tables"].append(expand_table(node, table_count, heading, source["final_url"]))
            except SourceError as error:
                packet["rejected_tables"].append({"source_table_index": table_count, "reason": str(error)})
            table_count += 1
    packet["coverage"]["observed_table_count"] = table_count
    if kind == "schedule":
        packet["schedule_games"], packet["reported_record"] = sidearm_schedule(document, source["final_url"])
    if packet["rejected_tables"]:
        packet["status"] = "partial"
    has_record = any(value is not None for record in packet["reported_record"].values() for value in record.values())
    if not packet["tables"] and not packet["schedule_games"] and not has_record:
        packet.update(status="needs_browser", error="No usable HTML tables or supported schedule cards; inspect the source in a browser or its official PDF")
    return packet


def markdown(packet):
    def value(item):
        return "unavailable" if item is None else str(item).replace("|", "\\|").replace("\n", " ")
    scope, source = packet.get("requested_scope", {}), packet.get("source", {})
    lines = ["# College baseball source observations", "", "Status: **%s**" % packet["status"], "",
             "Source: %s" % source.get("final_url", source.get("requested_url", "unavailable")),
             "", "Requested season: %s. Source cutoff: %s. Retrieved: %s." %
             (scope.get("season", "unavailable"), value(source.get("as_of")), value(source.get("retrieved_at"))), ""]
    if packet.get("error"):
        lines.extend([packet["error"], ""])
    for warning in packet.get("warnings", []):
        lines.append("- " + warning)
    for category, record in packet.get("reported_record", {}).items():
        lines.extend(["", "Reported %s record: %s wins, %s losses; ties %s." %
                      (category, value(record["wins"]), value(record["losses"]), value(record["ties"]))])
    for table in packet.get("tables", []):
        lines.extend(["", "## %s (source table %s)" % (table["caption"] or table["heading"] or "Table", table["source_table_index"]), ""])
        headers = table["header_rows"]
        columns = [" / ".join(dict.fromkeys(str(row[i]) for row in headers if row[i] is not None)) or "Column %s" % (i + 1)
                   for i in range(table["column_count"])]
        lines.append("| " + " | ".join(value(c) for c in columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")
        lines.extend("| " + " | ".join(value(c) for c in row) + " |" for row, section in zip(table["rows"], table["row_sections"]) if section != "advertisement")
        if table["warnings"]:
            lines.extend(["", " ".join(table["warnings"])])
    if packet.get("schedule_games"):
        lines.extend(["", "## Schedule observations", "", "| Source date | Opponent | Source result | Location |", "| --- | --- | --- | --- |"])
        for game in packet["schedule_games"]:
            lines.append("| " + " | ".join(value(game[k]) for k in ("date_text", "opponent", "result_text", "location")) + " |")
    if packet.get("rejected_tables"):
        lines.extend(["", "## Tables requiring source review", ""])
        lines.extend("- Table %s: %s" % (t["source_table_index"], t["reason"]) for t in packet["rejected_tables"])
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog="Exit 0: observations retrieved (coverage may be partial); 2: invalid input/output; 3: source unavailable, unverified or unsupported.")
    origin = parser.add_mutually_exclusive_group(required=True)
    origin.add_argument("--url", help="Discovered official season-specific HTML source")
    origin.add_argument("--input", help="Saved HTML file; requires --source-url and does not make a network request")
    parser.add_argument("--source-url", help="Original source attribution for --input; does not authenticate the file")
    parser.add_argument("--season", type=int, required=True, help="Requested spring baseball season; verified against page headings")
    parser.add_argument("--kind", choices=KINDS, required=True)
    parser.add_argument("--team", help="Requested team label, kept separate from verified source identity")
    parser.add_argument("--division", help="Requested association/division label, kept separate from verified source identity")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", help="Create a new output file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        if not 1800 <= args.season <= 2199:
            raise ValueError("season must be a four-digit year from 1800 through 2199")
        if bool(args.input) != bool(args.source_url):
            raise ValueError("--input and --source-url must be supplied together; --source-url is not used with --url")
        output = Path(args.output).resolve() if args.output else None
        if output is not None and output.exists():
            raise ValueError("Output already exists; choose a new path (inputs are never overwritten)")
        if args.input:
            path = Path(args.input).resolve()
            if output == path:
                raise ValueError("Input and output paths must differ")
            validate_url(args.source_url)
            if path.stat().st_size > MAX_BYTES:
                raise ValueError("Input exceeds the 8 MiB limit")
            raw = path.read_bytes()
            html = raw.decode("utf-8-sig")
            source = {"requested_url": args.source_url, "final_url": args.source_url,
                      "retrieved_at": None, "inspected_at": datetime.now(timezone.utc).isoformat(),
                      "http_status": None, "content_type": "text/html", "input_mode": "supplied_html",
                      "content_sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                      "file_name": path.name}
        else:
            html, source = fetch_source(args.url)
        packet = inspect_html(html, source, args.season, args.kind, args.team, args.division)
        code = 0 if packet["status"] in ("ok", "partial") else 3
    except SourceError as error:
        packet = {"schema_version": 1, "status": error.code, "error": str(error),
                  "source": {"requested_url": args.url or args.source_url, "retrieved_at": None, "as_of": None},
                  "requested_scope": {"season": args.season, "kind": args.kind},
                  "tables": [], "schedule_games": [], "reported_record": {}}
        code = 2 if error.code == "invalid_url" else 3
    except (OSError, ValueError, UnicodeError) as error:
        print("cbb_source: " + str(error), file=sys.stderr)
        return 2
    rendered = json.dumps(packet, indent=2, ensure_ascii=False) + "\n" if args.format == "json" else markdown(packet)
    if args.output:
        try:
            with Path(args.output).open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        except OSError as error:
            print("cbb_source: " + str(error), file=sys.stderr)
            return 2
    else:
        print(rendered, end="")
    return code


if __name__ == "__main__":
    sys.exit(main())
