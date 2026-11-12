"""Pronunciation catalogs and reading phrases per learner language (plan items 2.1, 2.3)."""

from __future__ import annotations

from collections import Counter

import pytest

from voicetutor import l1
from voicetutor.data_files import l1_catalog, reading_phrases
from voicetutor.lang_guard import classify
from voicetutor.pron import catalog
from voicetutor.pron.inventory import CONSONANTS, VOWELS
from voicetutor.pron.reference import build_reference

# SPEC 12 table: entry -> learner languages that include it.
SPEC_ENTRIES = {
    "short_i": {"es", "pt"},
    "ae_vowel": {"es", "pt"},
    "strut_vowel": {"es", "pt"},
    "schwa_reduction": {"es", "pt"},
    "short_u": {"es", "pt"},
    "nurse_vowel": {"es", "pt"},
    "b_v": {"es"},
    "th_voiceless": {"es", "pt"},
    "th_voiced": {"es", "pt"},
    "z_devoicing": {"es"},
    "sh_ch": {"es", "pt"},
    "j_sound": {"es"},
    "h_to_x": {"es"},
    "h_dropped": {"pt"},
    "r_initial": {"pt"},
    "r_tap_trill": {"es", "pt"},
    "s_cluster_epenthesis": {"es", "pt"},
    "final_epenthesis": {"pt"},
    "ed_suffix": {"es", "pt"},
    "t_d_palatal": {"pt"},
    "final_l": {"pt"},
    "final_m_nasal": {"pt"},
    "ng_ending": {"es", "pt"},
    "final_consonant_drop": {"es"},
    "w_gw": {"es"},
    "aspiration": {"es", "pt"},
}
FIELDS = {
    "id",
    "position",
    "detect",
    "default_level",
    "priority",
    "title",
    "tip",
    "examples",
    "pairs",
}
CLASSES = set(CONSONANTS) | set(VOWELS)


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_entry_sets_as_in_spec(lang: str) -> None:
    short = l1.short(lang)
    ids = {e["id"] for e in l1_catalog(lang)["entries"]}
    assert ids == {k for k, v in SPEC_ENTRIES.items() if short in v}, ids


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_schema(lang: str) -> None:
    for e in l1_catalog(lang)["entries"]:
        assert set(e) >= FIELDS, (e["id"], FIELDS - set(e))
        assert ("expected" in e) != ("expected_map" in e), e["id"]
        assert e["detect"] in {"substitution", "deletion", "insertion", "manual"}, e["id"]
        assert e["default_level"] in {"error", "approx"}, e["id"]
        assert e["priority"] in {1, 2, 3}, e["id"]
        assert e["title"].strip() and e["tip"].strip(), e["id"]
        assert len(e["examples"]) >= 3, e["id"]
        if e["detect"] == "insertion":
            assert e["insert"]["where"] in {"before", "after"}, e["id"]
            assert all(h.startswith("+") for h in e["heard"]), e["id"]
        if e["detect"] != "manual":
            assert len(e["pairs"]) >= 3, e["id"]
        for pair in e["pairs"]:
            assert len(pair["words"]) == 2 and pair["say"].strip(), (e["id"], pair)


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_symbols_are_scoring_classes(lang: str) -> None:
    for e in catalog.entries(lang):
        for exp in e.expected:
            assert exp == "*" or exp in CLASSES, (e.id, exp)
        for exp, heard in e.pairs:
            assert exp == "*" or exp in CLASSES, (e.id, exp)
            assert all(h in CLASSES for h in heard), (e.id, heard)
        assert all(s in CLASSES for s in e.insert_sounds), (e.id, e.insert_sounds)


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_tips_are_in_their_language(lang: str) -> None:
    for e in l1_catalog(lang)["entries"]:
        assert classify(e["tip"]).language == lang, (e["id"], e["tip"])


def test_spanish_tips_are_latin_american() -> None:
    text = " ".join(e["tip"] + e["title"] for e in l1_catalog("es-419")["entries"]).lower()
    for word in ("vosotros", "vuestro", "zapato en españa", "ordenador"):
        assert word not in text


def test_portuguese_tips_are_brazilian() -> None:
    text = " ".join(e["tip"] + e["title"] for e in l1_catalog("pt-BR")["entries"]).lower()
    assert "você" in text
    for word in ("ecrã", "utilizador", "facto"):
        assert word not in text


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_reading_coverage(lang: str) -> None:
    """Every automatic entry of the language occurs in at least two reading phrases."""
    phrases = reading_phrases()["phrases"]
    assert len(phrases) == 30
    seen: Counter[str] = Counter()
    for ph in phrases:
        assert 6 <= len(ph["text"].split()) <= 12, ph["id"]
        ref = build_reference(ph["text"].split(), lang=lang)
        for e in catalog.entries(lang):
            if any(
                p.scored and e.expects(p.cls) and catalog.position_ok(e.position, p)
                for p in ref.phones
            ):
                seen[e.id] += 1
    thin = {e.id: seen[e.id] for e in catalog.entries(lang) if seen[e.id] < 2}
    assert not thin, thin


def test_phrase_targets_exist() -> None:
    ids = {e["id"] for code in l1.codes() for e in l1_catalog(code)["entries"]}
    for ph in reading_phrases()["phrases"]:
        assert ph["targets"] and set(ph["targets"]) <= ids, ph["id"]


def test_insertions_only_where_the_catalog_says() -> None:
    """Plan item 2.2: an inserted vowel is tried only at catalog positions."""
    ref = build_reference(["I", "said", "speak", "and", "worked", "on", "my", "plan."], "es-419")
    inserted = {
        p.word_text: [v for v in p.competitors if len(v) > len(p.canonical)]
        for p in ref.phones
        if any(len(v) > len(p.canonical) for v in p.competitors)
    }
    assert ("ɛ", "s") in inserted["speak"]
    assert ("ɪ", "d") in inserted["worked"] and ("ɛ", "d") in inserted["worked"]
    assert "plan." not in inserted and "said" not in inserted  # es has no final epenthesis
    pt = build_reference(["big", "plan"], "pt-BR")
    final_g = next(p for p in pt.phones if p.word_text == "big" and p.word_final)
    assert ("ɡ", "iː") in final_g.competitors
    final_n = next(p for p in pt.phones if p.word_text == "plan" and p.word_final)
    assert ("n", "iː") not in final_n.competitors  # sonorants are left alone
