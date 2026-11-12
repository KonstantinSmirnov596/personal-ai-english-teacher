"""License audit of the Python dependencies pinned in uv.lock.

Usage: python scripts/license_audit.py [--write docs/reports/licenses_python.md]

For every package in ``uv.lock`` the installed distribution's own metadata is read
(``License-Expression``, ``License``, trove classifiers, bundled license files). The result is a
Markdown table; ``docs/reports/licenses.md`` embeds it and adds the primary-source review of
models, fonts, browser assets and binaries. Run after every change of ``uv.lock``.
"""

from __future__ import annotations

import argparse
import importlib.metadata as md
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Classifier -> SPDX id for the classifiers that occur in this dependency tree.
CLASSIFIER_SPDX = {
    "License :: OSI Approved :: MIT License": "MIT",
    "License :: OSI Approved :: BSD License": "BSD",
    "License :: OSI Approved :: Apache Software License": "Apache-2.0",
    "License :: OSI Approved :: Python Software Foundation License": "PSF-2.0",
    "License :: OSI Approved :: ISC License (ISCL)": "ISC",
    "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)": "LGPL-3.0",
    "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)": (
        "LGPL-2.0-or-later"
    ),
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)": "GPL-3.0",
    "License :: OSI Approved :: The Unlicense (Unlicense)": "Unlicense",
    "License :: Public Domain": "Public domain",
    "License :: OSI Approved :: Historical Permission Notice and Disclaimer (HPND)": "HPND",
    "License :: OSI Approved :: Zope Public License": "ZPL",
}

# Packages whose metadata declares no license, reviewed by hand against the primary source
# (docs/reports/licenses.md, "Models, binaries and browser assets").
REVIEWED: dict[str, tuple[str, str]] = {
    "espeakng-loader": (
        "MIT (loader); bundles espeak-ng GPL-3.0-or-later",
        "reviewed: GitHub LICENSE and wheel content",
    ),
}

SHORT_LICENSE = re.compile(r"^[A-Za-z0-9 .,+()\-/]{2,60}$")


@dataclass
class Row:
    name: str
    version: str
    license: str
    evidence: str
    group: str


def lock_packages() -> list[tuple[str, str, str]]:
    data = tomllib.loads((REPO / "uv.lock").read_text(encoding="utf-8"))
    project = data["package"]
    root = next(p for p in project if p.get("source", {}).get("editable") == ".")
    by_name = {p["name"]: p for p in project}

    def edges(pkg: dict) -> list[str]:
        deps = [d["name"] for d in pkg.get("dependencies", [])]
        for extra in pkg.get("optional-dependencies", {}).values():
            deps += [d["name"] for d in extra]
        return deps

    # Everything reachable from the project's runtime dependencies ships to users; the rest is
    # only needed for development (tests, linting).
    runtime: set[str] = set()
    stack = [d["name"] for d in root.get("dependencies", [])]
    while stack:
        name = stack.pop()
        if name in runtime or name not in by_name:
            continue
        runtime.add(name)
        stack.extend(edges(by_name[name]))
    result = []
    for pkg in project:
        if pkg is root:
            continue
        group = "runtime" if pkg["name"] in runtime else "dev"
        result.append((pkg["name"], pkg["version"], group))
    return sorted(result)


def license_of(dist: md.Distribution) -> tuple[str, str]:
    meta = dist.metadata
    expr = meta.get("License-Expression")
    if expr:
        return expr.strip(), "License-Expression"
    classifiers = [c for c in meta.get_all("Classifier") or [] if c.startswith("License ::")]
    spdx = [CLASSIFIER_SPDX.get(c, c.split("::")[-1].strip()) for c in classifiers]
    raw = (meta.get("License") or "").strip()
    if raw and SHORT_LICENSE.match(raw) and raw.upper() not in {"UNKNOWN", "OTHER"}:
        return raw, "License field" + (f" ({', '.join(spdx)})" if spdx else "")
    if spdx:
        return " / ".join(dict.fromkeys(spdx)), "classifier"
    files = [
        f for f in (dist.files or []) if any(s in str(f).lower() for s in ("licen", "copying"))
    ]
    for f in files:
        try:
            text = Path(dist.locate_file(f)).read_text(encoding="utf-8", errors="replace")[:600]
        except OSError:
            continue
        for needle, name in (
            ("MIT License", "MIT"),
            ("Apache License", "Apache-2.0"),
            ("BSD 3-Clause", "BSD-3-Clause"),
            ("Redistribution and use in source and binary forms", "BSD"),
            ("Permission is hereby granted, free of charge", "MIT"),
        ):
            if needle in text:
                return name, f"license file {Path(str(f)).name}"
    return "", "not found in metadata"


def rows() -> list[Row]:
    result = []
    for name, version, group in lock_packages():
        try:
            dist = md.distribution(name)
        except md.PackageNotFoundError:
            result.append(Row(name, version, "", "not installed", group))
            continue
        lic, evidence = license_of(dist)
        if not lic and name in REVIEWED:
            lic, evidence = REVIEWED[name]
        if dist.version != version:
            evidence += f"; installed {dist.version}"
        result.append(Row(name, version, lic, evidence, group))
    return result


def markdown(table: list[Row]) -> str:
    lines = [
        "| Package | Version | Group | License | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in table:
        lic = r.license.replace("|", "/") or "not found"
        lines.append(
            f"| [{r.name}](https://pypi.org/project/{r.name}/{r.version}/) | {r.version} | "
            f"{r.group} | {lic} | {r.evidence} |"
        )
    return "\n".join(lines) + "\n"


def notices_table(table: list[Row]) -> str:
    """Runtime packages for THIRD_PARTY_NOTICES.md (installed on the user's machine)."""
    lines = ["| Package | Version | License |", "| --- | --- | --- |"]
    for r in table:
        if r.group != "runtime":
            continue
        lic = r.license.replace("|", "/") or "not found"
        lines.append(
            f"| [{r.name}](https://pypi.org/project/{r.name}/{r.version}/) | {r.version} | {lic} |"
        )
    return "\n".join(lines) + "\n"


NOTICES_START = "<!-- runtime-packages:start -->"
NOTICES_END = "<!-- runtime-packages:end -->"


def write_notices(path: Path, table: list[Row]) -> None:
    text = path.read_text(encoding="utf-8")
    head, rest = text.split(NOTICES_START, 1)
    _old, tail = rest.split(NOTICES_END, 1)
    body = f"{NOTICES_START}\n{notices_table(table)}{NOTICES_END}"
    path.write_text(head + body + tail, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", type=Path, help="write the table to this file")
    ap.add_argument("--notices", type=Path, help="refresh the package list in THIRD_PARTY_NOTICES")
    args = ap.parse_args()
    table = rows()
    if args.notices:
        write_notices(args.notices, table)
    text = markdown(table)
    if args.write:
        args.write.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    missing = [r.name for r in table if not r.license]
    if missing:
        print(f"license not found for: {', '.join(missing)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
