"""User documentation in three languages (CLAUDE.md: en primary, es, pt-BR, same structure).

Stage 3 adds ``docs/<lang>/hardware.md``: the first-run wizard and the installer's requirements
check link to its anchors (``hardware.md#<check id>``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.hw_fakes import card, machine
from voicetutor import profiles
from voicetutor.lang_guard import classify

DOCS = Path(__file__).resolve().parents[1] / "docs"
LANGS = ("en", "es", "pt-BR")
L1_OF = {"es": "es-419", "pt-BR": "pt-BR"}


def headings(text: str, level: int) -> list[str]:
    return re.findall(rf"^{'#' * level} (.+)$", text, flags=re.M)


def anchors(text: str) -> list[str]:
    return re.findall(r'<a id="([a-z_]+)"></a>', text)


@pytest.fixture(scope="module")
def hardware() -> dict[str, str]:
    return {lang: (DOCS / lang / "hardware.md").read_text(encoding="utf-8") for lang in LANGS}


def test_same_structure_in_every_language(hardware: dict[str, str]) -> None:
    ref = hardware["en"]
    for lang, text in hardware.items():
        assert len(headings(text, 2)) == len(headings(ref, 2)), lang
        assert len(headings(text, 3)) == len(headings(ref, 3)), lang
        assert anchors(text) == anchors(ref), lang
        assert text.count("|") == ref.count("|"), lang  # the same tables


def test_every_check_has_an_anchor(hardware: dict[str, str]) -> None:
    """Every check the wizard can show links to a section (profiles.Check.to_api 'doc')."""
    ids = {c.id for c in profiles.assess(machine(gpu=card()), measured=True).checks}
    ids |= {c.id for c in profiles.assess(machine(gpu=None), measured=True).checks}
    for lang, text in hardware.items():
        assert ids <= set(anchors(text)), (lang, ids - set(anchors(text)))
        assert "profiles" in anchors(text)


def test_installer_check_ids_have_anchors(hardware: dict[str, str]) -> None:
    script = (DOCS.parent / "scripts" / "requirements.ps1").read_text(encoding="ascii")
    ids = set(re.findall(r"New-VtCheck '([a-z]+)'", script))
    assert ids == {"gpu", "driver", "architecture", "vram", "disk", "ram", "windows"}
    for lang, text in hardware.items():
        assert ids <= set(anchors(text)), lang


def test_numbers_match_the_code(hardware: dict[str, str]) -> None:
    driver = ".".join(map(str, profiles.MIN_DRIVER))
    for lang, text in hardware.items():
        assert driver in text and "7.5" in text and "19045" in text, lang


def test_learner_docs_are_in_their_language(hardware: dict[str, str]) -> None:
    for lang, l1 in L1_OF.items():
        paragraphs = [
            p
            for p in hardware[lang].split("\n\n")
            if len(p.split()) >= 12 and not p.lstrip().startswith(("|", "<", "#"))
        ]
        assert len(paragraphs) >= 8, lang
        wrong = [p[:60] for p in paragraphs if classify(p).language not in (l1, None)]
        assert not wrong, (lang, wrong)
