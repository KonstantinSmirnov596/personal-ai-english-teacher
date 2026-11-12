"""Window strings per learner language (plan item 1.2): complete, non-empty, consistent."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.i18n_parse import flatten, parse_file
from voicetutor import l1
from voicetutor.lang_guard import classify

REPO = Path(__file__).resolve().parent.parent
I18N = REPO / "web" / "i18n"
# Strings that are the same in every language on purpose (brand, units, codes).
LANGUAGE_NEUTRAL = {"appTitle", "talk.tutor", "panel.manual", "connections.colModel"}


def strings(code: str) -> dict[str, tuple[str, object]]:
    return flatten(parse_file(I18N / f"{code}.js"))


@pytest.fixture(scope="module")
def all_strings() -> dict[str, dict[str, tuple[str, object]]]:
    return {code: strings(code) for code in l1.codes()}


def test_every_learner_language_has_a_string_file() -> None:
    files = {p.stem for p in I18N.glob("*.js")}
    assert files == set(l1.codes()), files ^ set(l1.codes())


def test_key_sets_are_identical(all_strings) -> None:
    reference = set(next(iter(all_strings.values())))
    for code, table in all_strings.items():
        assert set(table) == reference, (code, sorted(set(table) ^ reference)[:20])


def test_values_have_the_same_shape(all_strings) -> None:
    codes = list(all_strings)
    base = all_strings[codes[0]]
    for code in codes[1:]:
        for key, (kind, val) in all_strings[code].items():
            ref_kind, ref_val = base[key]
            assert kind == ref_kind, (code, key)
            if kind == "fn":
                assert val == ref_val, (code, key, "parameter count")
            if kind == "list":
                assert len(val) == len(ref_val), (code, key)


def test_no_empty_strings(all_strings) -> None:
    for code, table in all_strings.items():
        empty = [k for k, (kind, v) in table.items() if kind == "str" and not str(v).strip()]
        lists = [k for k, (kind, v) in table.items() if kind == "list" and not all(v)]
        assert not empty and not lists, (code, empty, lists)


def test_completeness_is_100_percent(all_strings) -> None:
    """Every key referenced by the window code exists in every language file."""
    used: set[str] = set()
    for js in (REPO / "web" / "js").glob("*.js"):
        text = js.read_text(encoding="utf-8")
        used.update(re.findall(r"\bL\.([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", text))
        # section aliases such as `const R = L.connections;` then `R.title`, each one up to the
        # next assignment of the same alias name
        assigns = list(re.finditer(r"const (\w+) = L\.(\w+);", text))
        for n, m in enumerate(assigns):
            alias, section = m.group(1), m.group(2)
            later = [a.start() for a in assigns[n + 1 :] if a.group(1) == alias]
            scope = text[m.end() : later[0] if later else len(text)]
            used.update(f"{section}.{x}" for x in re.findall(rf"\b{alias}\.(\w+)", scope))
    for code, table in all_strings.items():
        keys = set(table)
        prefixes = {k.rsplit(".", 1)[0] for k in keys if "." in k} | {k.split(".")[0] for k in keys}
        missing = sorted(u for u in used if u not in keys and u not in prefixes)
        assert not missing, (code, missing)
        coverage = 1 - len(missing) / max(len(used), 1)
        assert coverage == 1.0


def test_strings_are_in_their_language(all_strings) -> None:
    """Long sentences read as the file's own language, never as another learner language.

    The guard is tuned to never call English text Spanish or Portuguese, so it misses some short
    sentences without function words; at least 85 % must be recognized, none as the wrong one.
    """
    for code, table in all_strings.items():
        checked, own, wrong = 0, 0, []
        for key, (kind, val) in table.items():
            if kind != "str" or key in LANGUAGE_NEUTRAL or len(str(val).split()) < 6:
                continue
            checked += 1
            got = classify(str(val)).language
            own += got == code
            if got is not None and got != code:
                wrong.append((key, got))
        assert checked >= 20, code
        assert not wrong, (code, wrong)
        assert own / checked >= 0.85, (code, own, checked)


def test_spanish_variety_is_latin_american() -> None:
    """SPEC 5: tú, no vosotros or voseo, no Spain-only words."""
    text = (I18N / "es-419.js").read_text(encoding="utf-8").lower()
    for word in (
        "vosotros",
        "vuestro",
        "vuestra",
        "ordenador",
        "móvil",
        "tenéis",
        "podéis",
        "vale,",
    ):
        assert word not in text, word
    for voseo in ("tenés", "podés", "querés", "sabés"):
        assert voseo not in text, voseo


def test_portuguese_variety_is_brazilian() -> None:
    """SPEC 5: você, Brazilian spelling (no European forms such as ecrã, utilizador, facto)."""
    text = (I18N / "pt-BR.js").read_text(encoding="utf-8").lower()
    for word in ("ecrã", "utilizador", "facto", "telemóvel", "registo", "ficheiro", "tu "):
        assert word not in text, word
    assert "você" in text
