"""Repository hygiene (SPEC section 3): no personal data, secrets or recordings in the repository.

The scan covers every file git would publish: tracked files plus untracked files that are not
ignored. Generated, downloaded and local-only paths are ignored by ``.gitignore`` and
``.git/info/exclude`` and therefore never reach a commit.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

TEXT_SUFFIXES = {
    ".py", ".js", ".mjs", ".css", ".html", ".md", ".json", ".jsonl", ".toml", ".txt", ".yml",
    ".yaml", ".ps1", ".cmd", ".bat", ".cfg", ".ini", ".svg", ".lock", "",
}  # fmt: skip

# The predecessor's Russian locale is gone (stage 1 removed the UI, prompts and data; stage 2
# replaced the pronunciation catalog): no file may contain Cyrillic.
CYRILLIC_ALLOWED: dict[str, str] = {}

CYRILLIC = re.compile(r"[\u0400-\u052f]")
# Assembled from parts so this file does not match its own patterns.
USER_PATH = re.compile(r"[A-Za-z]:[\\/]+" + "Us" + r"ers[\\/]+", re.IGNORECASE)
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
SK_KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{12,}")
SK_TEST = re.compile(r"\bsk-test-")
BASE64_RUN = re.compile(r"[A-Za-z0-9+/=]{31,}")
HEX = re.compile(r"[0-9a-fA-F]+")
SRI_PREFIX = re.compile(r"sha(?:256|384|512)-$")

# Public, non-secret long tokens that are not hashes: (path, token, reason).
BASE64_ALLOWED: set[tuple[str, str]] = set()


def published_files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=REPO,
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - git is required
        pytest.fail("git is needed to list the files of the repository")
    files = [REPO / f for f in out.split("\0") if f]
    return [f for f in files if f.is_file()]


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def text_files() -> list[tuple[str, str]]:
    result = []
    for path in published_files():
        if path.resolve() == SELF or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            result.append((rel(path), path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            continue
    return result


@pytest.fixture(scope="module")
def files() -> list[tuple[str, str]]:
    return text_files()


def test_scan_sees_the_repository(files: list[tuple[str, str]]) -> None:
    names = {name for name, _ in files}
    assert {"pyproject.toml", "voicetutor/__init__.py", "README.md"} <= names


def test_local_only_files_are_not_published() -> None:
    names = {rel(p) for p in published_files()}
    for local in ("docs/SPEC.md", "docs/BASELINE_REPORT.md", "CLAUDE.local.md"):
        assert local not in names, f"{local} must stay untracked"
    assert ".claude/settings.local.json" not in names
    assert not [n for n in names if n.startswith((".venv/", ".tools/", "test-results/"))]
    assert not [n for n in names if n.endswith((".db", ".db-wal", ".db-shm", ".lnk"))]


def test_no_user_profile_paths_or_user_name(files: list[tuple[str, str]]) -> None:
    problems = [name for name, text in files if USER_PATH.search(text)]
    user = os.environ.get("USERNAME", "")
    if len(user) >= 3 and user.lower() not in {"user", "admin", "runneradmin", "runner"}:
        word = re.compile(rf"\b{re.escape(user)}\b", re.IGNORECASE)
        problems += [f"{name}: user name" for name, text in files if word.search(text)]
    assert not problems, problems


def test_no_email_addresses(files: list[tuple[str, str]]) -> None:
    problems = [
        f"{name}: {m.group(0)}"
        for name, text in files
        if name != "uv.lock"
        for m in EMAIL.finditer(text)
    ]
    assert not problems, problems


def test_no_api_keys(files: list[tuple[str, str]]) -> None:
    problems = [
        f"{name}: {m.group(0)[:12]}…"
        for name, text in files
        for m in SK_KEY.finditer(text)
        if not SK_TEST.match(m.group(0))
    ]
    assert not problems, problems


def _suspicious(text: str, start: int, token: str) -> bool:
    stripped = token.strip("=/+")
    if len(stripped) <= 30:
        return False
    if HEX.fullmatch(stripped):
        return False  # commit ids and SHA digests are public
    if SRI_PREFIX.search(text[max(0, start - 7) : start]):
        return False  # Subresource Integrity hash of a downloaded file
    if text[max(0, start - 8) : start] == "sk-test-":
        return False  # fake key used by tests (never a real provider key)
    word_start = max(text.rfind(c, 0, start) for c in (" ", "(", "\n", '"', "'", "`"))
    if "/" in stripped and "://" in text[word_start + 1 : start + 1]:
        return False  # path segments of a URL (a secret in a query string still matches)
    has_digit = any(c.isdigit() for c in stripped)
    has_letter = any(c.isalpha() for c in stripped)
    return has_digit and has_letter


def test_no_long_base64_tokens(files: list[tuple[str, str]]) -> None:
    problems = []
    for name, text in files:
        if name == "uv.lock":
            continue  # machine-written: public package hashes and URLs only
        for m in BASE64_RUN.finditer(text):
            if (name, m.group(0)) in BASE64_ALLOWED:
                continue
            if _suspicious(text, m.start(), m.group(0)):
                problems.append(f"{name}: {m.group(0)[:16]}…")
    assert not problems, problems


def test_no_recordings_outside_generated_dirs() -> None:
    wavs = [rel(p) for p in published_files() if p.suffix.lower() in {".wav", ".mp3", ".flac"}]
    assert not wavs, wavs


def test_cyrillic_only_in_allowed_paths(files: list[tuple[str, str]]) -> None:
    problems = []
    for name, text in files:
        if name in CYRILLIC_ALLOWED:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if CYRILLIC.search(line):
                problems.append(f"{name}:{lineno}")
    assert not problems, problems[:20]


def test_cyrillic_allowlist_is_not_stale() -> None:
    stale = [p for p in CYRILLIC_ALLOWED if not (REPO / p).is_file()]
    assert not stale, stale
    unused = [
        p for p in CYRILLIC_ALLOWED if not CYRILLIC.search((REPO / p).read_text(encoding="utf-8"))
    ]
    assert not unused, unused
