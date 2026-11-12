"""Prompts with a learner-language parameter (plan item 1.3, SPEC 5 "Prompts")."""

from __future__ import annotations

import json

from voicetutor import l1
from voicetutor.data_files import patterns, scenarios
from voicetutor.helpers import lang_fields
from voicetutor.lang_guard import classify
from voicetutor.prompts import corrector, helpers, summary, tutor


def test_corrector_prompt_names_the_language_and_marks_keys() -> None:
    es = corrector.build_system_prompt(patterns(), "es-419")
    pt = corrector.build_system_prompt(patterns(), "pt-BR")
    assert "first language is Latin American Spanish" in es
    assert "first language is Brazilian Portuguese" in pt
    assert "note_l1: one sentence in Latin American Spanish" in es
    assert "- there_is_have [pt]: In my city has a big park." in es
    assert "Keys marked [es] are typical" in es and "Keys marked [pt] are typical" in pt
    for text in (es, pt):
        assert "Russian" not in text and "note_ru" not in text
        assert "JSON" in text


def test_corrector_example_per_language() -> None:
    es = corrector.build_system_prompt(patterns(), "es-419")
    pt = corrector.build_system_prompt(patterns(), "pt-BR")
    assert "I have 30 years" in es and "In my city has a big park" not in es.split("EXAMPLE")[1]
    assert "In my city has a big park" in pt.split("EXAMPLE")[1]
    for lang, text in (("es-419", es), ("pt-BR", pt)):
        out = json.loads(text.split("Output:\n", 1)[1].split("\n", 1)[0])
        notes = [i["note_l1"] for i in out["items"]]
        assert all(classify(n).language == lang for n in notes), (lang, notes)


def test_helper_and_summary_prompts_take_the_language() -> None:
    for code in l1.codes():
        fields = lang_fields(code)
        name = l1.name_en(code)
        translate = helpers.TRANSLATE.format(tutor_text="Hi.", **fields)
        assert f"natural {name}" in translate and '"translation"' in translate
        how = helpers.HOW_TO_SAY.format(level="B1", tutor_text="Hi.", text_l1="x", **fields)
        assert f"first language is {name}" in how and f"Phrase in {name}" in how
        check = helpers.EXERCISE_CHECK.format(
            prompt_l1="x", answer_en="y", focus_title="z", learner_said="w", **fields
        )
        assert f"Task ({name})" in check
        s = summary.build_system_prompt(name, fields["l1_style"])
        assert f"first language is {name}" in s and "translation_l1" in s
        for text in (translate, how, check, s):
            assert "Russian" not in text and "JSON" in text


def test_tutor_prompt_is_language_neutral_and_stable() -> None:
    """The tutor speaks English only; its system prompt does not depend on the learner language,
    so the provider's context cache survives a language switch."""
    p = tutor.build_system_prompt(level="B1", scenario=scenarios()[0], recast=True, focus_lines=[])
    assert "Never use any language other than English" in p
    assert "Russian" not in p and "Spanish" not in p and "Portuguese" not in p


def test_style_rules_name_the_variety() -> None:
    assert "tú" in l1.meta("es-419")["style"] and "vosotros" in l1.meta("es-419")["style"]
    assert "você" in l1.meta("pt-BR")["style"]
