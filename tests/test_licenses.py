"""License audit (plan item 0.7): docs/reports/licenses.md covers every shipped component."""

from __future__ import annotations

import importlib.util
import re
import sys
import tomllib
from pathlib import Path

from tests.test_hygiene import published_files, rel

REPO = Path(__file__).resolve().parent.parent
REPORT = REPO / "docs" / "reports" / "licenses.md"
START = "<!-- python-table:start -->"
END = "<!-- python-table:end -->"

# Components outside uv.lock that must have a reviewed row (primary source link) in the report.
NON_PYTHON = (
    "faster-whisper-large-v3-turbo",
    "whisper-large-v3-turbo",
    "Kokoro-82M",
    "wav2vec2-lv-60-espeak-cv-ft",
    "espeak-ng",
    "Inter",
    "JetBrains Mono",
    "vad-web",
    "Silero VAD",
    "onnxruntime-web",
    "en_core_web_sm",
    "NVIDIA CUDA",
    "Microsoft Edge",
)

WEIGHT_SUFFIXES = {".bin", ".pt", ".pth", ".safetensors", ".onnx", ".ckpt", ".gguf", ".npz"}
BINARY_SUFFIXES = {".dll", ".exe", ".so", ".dylib", ".pyd", ".wasm"}


def _audit_module():
    spec = importlib.util.spec_from_file_location(
        "license_audit", REPO / "scripts" / "license_audit.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["license_audit"] = module
    spec.loader.exec_module(module)
    return module


def _report() -> str:
    assert REPORT.is_file(), "docs/reports/licenses.md is missing"
    return REPORT.read_text(encoding="utf-8")


def _table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and not re.fullmatch(r"\|[\s:|-]+\|", s):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


def test_every_locked_package_has_a_license_row() -> None:
    lock = tomllib.loads((REPO / "uv.lock").read_text(encoding="utf-8"))
    packages = {
        (p["name"], p["version"])
        for p in lock["package"]
        if p.get("source", {}).get("editable") != "."
    }
    text = _report()
    assert START in text and END in text
    section = text.split(START, 1)[1].split(END, 1)[0]
    found = {}
    for cells in _table_rows(section)[1:]:
        name = re.sub(r"^\[([^\]]+)\].*$", r"\1", cells[0])
        found[(name, cells[1])] = cells[3]
    missing = sorted(packages - set(found))
    assert not missing, missing
    unlicensed = sorted(k for k, v in found.items() if not v or v == "not found")
    assert not unlicensed, unlicensed


def test_python_table_is_current() -> None:
    """The embedded table equals a fresh run of scripts/license_audit.py (rerun after relock)."""
    audit = _audit_module()
    section = _report().split(START, 1)[1].split(END, 1)[0].strip()
    assert section == audit.markdown(audit.rows()).strip()


def test_non_python_components_reviewed() -> None:
    text = _report()
    rows = _table_rows(text)
    for component in NON_PYTHON:
        hits = [r for r in rows if component.lower() in r[0].lower()]
        assert hits, f"no row for {component}"
        assert any("https://" in " ".join(r) for r in hits), f"no source link for {component}"


def test_no_weights_or_gpl_binaries_tracked() -> None:
    names = [rel(p) for p in published_files()]
    weights = [n for n in names if Path(n).suffix.lower() in WEIGHT_SUFFIXES]
    binaries = [n for n in names if Path(n).suffix.lower() in BINARY_SUFFIXES]
    espeak = [n for n in names if "espeak-ng-data" in n or "libespeak" in n.lower()]
    assert not weights, weights
    assert not binaries, binaries
    assert not espeak, espeak
