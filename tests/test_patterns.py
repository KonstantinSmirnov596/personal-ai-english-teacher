"""Recurring-mistake keys (plan item 1.7, SPEC 12)."""

from __future__ import annotations

from voicetutor import l1
from voicetutor.data_files import patterns
from voicetutor.lang_guard import classify

# SPEC 12 table: key -> learner languages for which it is typical.
SPEC_KEYS = {
    "subject_missing": {"es", "pt"},
    "there_is_have": {"pt"},
    "age_have": {"es", "pt"},
    "adjective_order": {"es", "pt"},
    "adjective_plural": {"es", "pt"},
    "possessive_of": {"es", "pt"},
    "do_auxiliary": {"es", "pt"},
    "explain_to": {"es", "pt"},
    "false_friends": {"es", "pt"},
    "article_general": {"es", "pt"},
    "people_plural": {"es", "pt"},
    "gerund_after_preposition": {"es", "pt"},
    **{
        k: {"es", "pt"}
        for k in (
            "make_do",
            "say_tell",
            "for_since",
            "present_perfect_vs_past_simple",
            "third_person_s",
            "prepositions",
            "word_order_questions",
            "double_negative",
            "countable_uncountable",
            "comparative_superlative",
            "much_many",
            "calque",
            "collocation",
            "word_choice",
            "other",
        )
    },
}


def test_key_set_equals_spec() -> None:
    keys = {p["key"] for p in patterns()}
    assert keys == set(SPEC_KEYS), sorted(keys ^ set(SPEC_KEYS))


def test_language_marks_match_spec() -> None:
    for p in patterns():
        assert set(p["l1"]) == SPEC_KEYS[p["key"]], p["key"]


def test_every_key_marked_for_a_language_has_a_name_and_hint_in_it() -> None:
    for code in l1.codes():
        names = l1.patterns(code)
        short = l1.short(code)
        for p in patterns():
            if short not in p["l1"]:
                continue
            entry = names.get(p["key"])
            assert entry and entry["title"].strip(), (code, p["key"])
            if p["key"] != "other":
                assert entry["hint"].strip(), (code, p["key"])


def test_hints_are_in_their_language() -> None:
    for code in l1.codes():
        hints = [v["hint"] for v in l1.patterns(code).values() if len(v["hint"].split()) >= 6]
        wrong = [h for h in hints if classify(h).language not in (None, code)]
        assert not wrong, (code, wrong)


def test_focus_lines_are_english() -> None:
    for p in patterns():
        if p["elicit_en"] is not None:
            assert classify(p["elicit_en"]).language is None, p["key"]
