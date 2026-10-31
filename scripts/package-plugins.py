#!/usr/bin/env python3
"""Create deterministic one-plugin ZIPs outside source packages. Python 3.9+."""

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {"plugin.json", "mcp.json", ".mcp.json", "README.md", "LICENSE"}
DIRECTORIES = {
    ".claude-plugin",
    ".codex-plugin",
    "skills",
    "commands",
    "agents",
    "assets",
}
EXCLUDED = {"__pycache__", ".git", "node_modules", ".DS_Store"}


def package_plugin(name, output):
    source = ROOT / "plugins" / name
    if output == source or source in output.parents:
        raise ValueError("Archive output must be outside the plugin source")
    metadata = json.loads((source / "plugin.json").read_text(encoding="utf-8"))
    version = metadata["version"]
    if metadata["name"] != name or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", version
    ):
        raise ValueError("Invalid package identity or version")
    selected = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in EXCLUDED for part in relative.parts) or path.suffix in {
            ".pyc",
            ".pyo",
        }:
            continue
        if relative.parts[0] not in DIRECTORIES and relative.as_posix() not in FILES:
            continue
        if path.is_symlink():
            raise ValueError("Symlinks are not accepted in release archives")
        if path.is_file():
            selected.append((path, relative.as_posix()))
    names = {relative for _, relative in selected}
    required = {
        "plugin.json",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "LICENSE",
    }
    if not required.issubset(names) or not any(
        n.startswith("skills/") and n.endswith("/SKILL.md") for n in names
    ):
        raise ValueError("Package is missing required release components")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{name}-{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path, relative in selected:
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes())
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("Archive integrity check failed")
    return {
        "plugin": name,
        "version": version,
        "file": archive.name,
        "files": len(selected),
        "bytes": archive.stat().st_size,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin",
        action="append",
        help="Catalog name; repeat to select several, omit for all",
    )
    parser.add_argument("--output", default=str(ROOT / "dist" / "plugin-packages"))
    args = parser.parse_args(argv)
    try:
        catalog = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        known = {entry["name"] for entry in catalog["plugins"]}
        selected = args.plugin or sorted(known)
        for name in selected:
            if name not in known:
                raise ValueError("Unknown plugin: " + name)
        output = Path(args.output).resolve()
        result = [package_plugin(name, output) for name in sorted(set(selected))]
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print("package-plugins: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
