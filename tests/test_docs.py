"""Documentation (plan item 4.4): links resolve, three languages with the same structure.

- every relative link in the published Markdown files points to an existing file, and an
  ``#anchor`` to an ``<a id>`` or a heading of that file;
- every ``docs/en/*.md`` has ``docs/es`` and ``docs/pt-BR`` twins with the same number of
  second- and third-level headings, the same anchors and the same tables;
- the three READMEs have the same sections and images.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("en", "es", "pt-BR")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
LOCAL_ONLY = {"docs/SPEC.md", "docs/BASELINE_REPORT.md", "CLAUDE.local.md"}


def published_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return [ROOT / p for p in out if p not in LOCAL_ONLY and (ROOT / p).exists()]


def slug(heading: str) -> str:
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(text: str) -> set[str]:
    ids = set(re.findall(r'<a id="([^"]+)"></a>', text))
    ids |= {slug(h) for h in re.findall(r"^#{1,6} (.+)$", text, flags=re.M)}
    return ids


def strip_code(text: str) -> str:
    """Code blocks and inline code are not links (e.g. misaki's `[word](/phonemes/)`)."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]+`", "", text)


def test_relative_links_resolve() -> None:
    problems: list[str] = []
    for md in published_markdown():
        text = strip_code(md.read_text(encoding="utf-8"))
        for target in LINK.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("mailto:"):
                continue
            path_part, _, anchor = target.partition("#")
            dest = md if not path_part else (md.parent / path_part).resolve()
            rel = md.relative_to(ROOT).as_posix()
            if not dest.exists():
                problems.append(f"{rel}: missing {target}")
                continue
            if (
                anchor
                and dest.suffix == ".md"
                and anchor not in anchors(dest.read_text(encoding="utf-8"))
            ):
                problems.append(f"{rel}: no anchor {target}")
    assert not problems, problems


@pytest.mark.parametrize("name", sorted(p.name for p in (ROOT / "docs" / "en").glob("*.md")))
def test_user_docs_have_twins(name: str) -> None:
    texts = {lang: (ROOT / "docs" / lang / name).read_text(encoding="utf-8") for lang in LANGS}
    ref = texts["en"]
    for lang, text in texts.items():
        for level in ("## ", "### "):
            count = len(re.findall(rf"^{level}", text, flags=re.M))
            assert count == len(re.findall(rf"^{level}", ref, flags=re.M)), (name, lang, level)
        assert re.findall(r'<a id="([^"]+)"></a>', text) == re.findall(
            r'<a id="([^"]+)"></a>', ref
        ), (name, lang)
        assert text.count("|") == ref.count("|"), (name, lang)


def test_doc_sets_are_complete() -> None:
    sets = {lang: {p.name for p in (ROOT / "docs" / lang).glob("*.md")} for lang in LANGS}
    assert sets["en"] == sets["es"] == sets["pt-BR"]
    assert {
        "install.md",
        "hardware.md",
        "api-keys.md",
        "usage.md",
        "troubleshooting.md",
        "privacy.md",
    } <= sets["en"]


def test_readmes_match() -> None:
    names = ("README.md", "README.es.md", "README.pt-BR.md")
    texts = [(ROOT / n).read_text(encoding="utf-8") for n in names]
    heads = [len(re.findall(r"^## ", t, flags=re.M)) for t in texts]
    images = [re.findall(r"!\[[^\]]*\]\(([^)]+)\)", t) for t in texts]
    assert len(set(heads)) == 1, heads
    assert images[0] and images[0] == images[1] == images[2]


def test_repository_files_exist() -> None:
    for name in (
        "LICENSE",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "THIRD_PARTY_NOTICES.md",
        "CHANGELOG.md",
        "install.cmd",
        "uninstall.cmd",
    ):
        assert (ROOT / name).is_file(), name
