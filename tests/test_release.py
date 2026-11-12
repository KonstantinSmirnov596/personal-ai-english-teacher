"""Release archive (plan item 4.2): what a user gets, and nothing that must not ship."""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import make_release  # noqa: E402


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, list[str]]:
    out = tmp_path_factory.mktemp("dist")
    archive = make_release.build(out)
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
    return archive, names


def test_archive_name_and_checksum(built: tuple[Path, list[str]]) -> None:
    archive, names = built
    ver = make_release.version()
    assert archive.name == f"VoiceTutor-{ver}.zip"
    assert all(n.startswith(f"VoiceTutor-{ver}/") for n in names)
    sums = (archive.parent / "SHA256SUMS.txt").read_text(encoding="ascii").split()
    assert sums == [hashlib.sha256(archive.read_bytes()).hexdigest(), archive.name]
    assert (archive.parent / f"release-notes-v{ver}.md").exists()
    assert archive.stat().st_size < 5 * 2**20  # code and docs only


def test_everything_the_installer_needs(built: tuple[Path, list[str]]) -> None:
    _archive, names = built
    files = {n.split("/", 1)[1] for n in names}
    required = {
        "install.cmd",
        "uninstall.cmd",
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "README.es.md",
        "README.pt-BR.md",
        "LICENSE",
        "THIRD_PARTY_NOTICES.md",
        "CHANGELOG.md",
        "voicetutor/__init__.py",
        "voicetutor/launcher.py",
        "voicetutor/data/model_files.json",
        "web/index.html",
        "web/js/wizard.js",
        "assets/voicetutor.ico",
    }
    for lang in ("en", "es", "pt-BR"):
        required |= {f"docs/{lang}/{d}.md" for d in ("install", "hardware", "api-keys", "usage")}
    assert required <= files, sorted(required - files)
    # every script the installer and the shortcuts load is there
    for script in ("setup.ps1", "uninstall.ps1", "run.ps1", "collect_diagnostics.ps1"):
        text = (ROOT / "scripts" / script).read_text(encoding="ascii")
        for ref in [*re.findall(r"\$PSScriptRoot\\([\w.]+)", text), script]:
            assert f"scripts/{ref}" in files, (script, ref)
    for ref in re.findall(r"'([\w.]+\.json)'", (ROOT / "scripts" / "requirements.ps1").read_text()):
        assert f"scripts/{ref}" in files


def test_nothing_that_must_not_ship(built: tuple[Path, list[str]]) -> None:
    _archive, names = built
    files = [n.split("/", 1)[1] for n in names]
    for f in files:
        assert not f.startswith(("tests/", ".github/", ".venv/", ".tools/", "web/fonts/")), f
        assert not f.startswith(("web/vendor/", "models/", "dist/", "test-results/")), f
        assert not re.search(r"\.(bin|pth|pt|onnx|safetensors|dll|exe|db|lnk|wav)$", f), f
    for local in ("docs/SPEC.md", "docs/BASELINE_REPORT.md", "CLAUDE.local.md", "CLAUDE.md"):
        assert local not in files
    assert not [f for f in files if "espeak" in f.lower() and not f.endswith(".py")]
