"""Learner-language registry (plan item 1.1, SPEC 5)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from voicetutor import l1

L1_DIR = Path(__file__).resolve().parent.parent / "voicetutor" / "data" / "l1"


def test_two_languages_are_discovered() -> None:
    assert l1.codes() == ["es-419", "pt-BR"]
    assert l1.name_en("es-419") == "Latin American Spanish"
    assert l1.name_en("pt-BR") == "Brazilian Portuguese"
    assert l1.html_lang("pt-BR") == "pt-BR"
    assert l1.short("es-419") == "es" and l1.short("pt-BR") == "pt"


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("es-MX", "es-419"),
        ("es-ES", "es-419"),
        ("es-419", "es-419"),
        ("pt-BR", "pt-BR"),
        ("pt-PT", "pt-BR"),
        ("en-US", "es-419"),
        ("ru-RU", "es-419"),
        ("", "es-419"),
    ],
)
def test_windows_locale_suggests_a_language(locale: str, expected: str) -> None:
    """SPEC 5: es-* -> Spanish, pt-* -> Portuguese, anything else -> Spanish."""
    assert l1.for_locale(locale) == expected


def test_windows_locale_is_read() -> None:
    assert isinstance(l1.windows_locale(), str)
    assert l1.default_code() in l1.codes()


def test_a_third_language_is_added_by_files_only(tmp_path: Path) -> None:
    """A new learner language needs files, not code: copy one, rename it, it is discovered."""
    root = tmp_path / "l1"
    for code in l1.codes():
        shutil.copytree(L1_DIR / code, root / code)
    shutil.copytree(L1_DIR / "es-419", root / "it-IT")
    meta = json.loads((root / "it-IT" / "meta.json").read_text(encoding="utf-8"))
    meta.update(
        code="it-IT",
        name_native="Italiano",
        name_en="Italian",
        html_lang="it",
        catalog_l1="it",
        windows_locales=["it"],
    )
    (root / "it-IT" / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    found = l1.discover(root)
    assert list(found) == ["es-419", "it-IT", "pt-BR"]
    assert l1.for_locale("it-IT", found) == "it-IT"
    assert l1.for_locale("de-DE", found) == "es-419"


def test_meta_code_must_match_directory(tmp_path: Path) -> None:
    shutil.copytree(L1_DIR / "es-419", tmp_path / "xx")
    with pytest.raises(ValueError, match="differs"):
        l1.discover(tmp_path)


def test_every_language_has_its_files() -> None:
    for code in l1.codes():
        d = L1_DIR / code
        for name in ("meta.json", "messages.json", "patterns.json", "corrector_eval.jsonl"):
            assert (d / name).is_file(), (code, name)
        assert (Path(__file__).resolve().parent.parent / "web" / "i18n" / f"{code}.js").is_file()


def test_core_messages_complete() -> None:
    reference = l1.messages("es-419")
    for code in l1.codes():
        msg = l1.messages(code)
        assert set(msg) == set(reference), code
        assert set(msg["errors"]) == set(reference["errors"]), code
        assert all(str(v).strip() for v in msg["errors"].values()), code


def test_unknown_language_falls_back() -> None:
    assert l1.resolve("ru") == "es-419"
    assert l1.resolve("") == "es-419"
    assert l1.resolve("pt-BR") == "pt-BR"
