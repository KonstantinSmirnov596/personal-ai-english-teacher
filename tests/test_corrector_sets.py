"""Corrector evaluation sets per learner language (plan item 1.8, SPEC 12)."""

from __future__ import annotations

import pytest

from voicetutor import l1
from voicetutor.data_files import corrector_eval, pattern_keys, patterns
from voicetutor.lang_guard import not_english


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_set_composition(lang: str) -> None:
    cases = corrector_eval(lang)
    assert len(cases) == 40
    assert len({c["id"] for c in cases}) == 40
    low_conf = [c for c in cases if c["asr_unsure"]]
    correct = [c for c in cases if not c["expect"] and not c["asr_unsure"]]
    errors = [c for c in cases if c["expect"] and not c["asr_unsure"]]
    assert (len(errors), len(correct), len(low_conf)) == (28, 8, 4)


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_cases_are_well_formed(lang: str) -> None:
    keys = set(pattern_keys())
    short = l1.short(lang)
    typical = {p["key"] for p in patterns() if short in p["l1"]}
    for c in corrector_eval(lang):
        assert c["level"] in {"A2", "B1", "B2", "C1"}, c["id"]
        assert set(c["expect"]) <= keys, c["id"]
        assert not not_english(c["learner_said"]), c["id"]
        assert not not_english(c["tutor_said"]), c["id"]
        for w in c.get("forbid_quote", []):
            assert w in c["learner_said"].split(), c["id"]
            assert w in c["asr_unsure"], c["id"]
        if c["expect"]:
            assert set(c["expect"]) & typical, c["id"]  # typical mistakes of this language


def test_correct_cases_include_colloquial_forms_and_fillers() -> None:
    for lang in ("es-419", "pt-BR"):
        clean = " ".join(c["learner_said"].lower() for c in corrector_eval(lang) if not c["expect"])
        assert "gonna" in clean
        assert any(f in clean for f in ("um,", "like,", "you know"))
