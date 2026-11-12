"""Corrector prompt: one learner turn in, up to three corrections out (JSON).

The prompt is built per learner language: explanations (``note_l1``) are written in it, the
mistake keys typical for its speakers are marked, and the worked example shows one of their
typical mistakes (SPEC 5, "Prompts").
"""

from __future__ import annotations

import json
from typing import Any

from voicetutor import l1

SYSTEM_TEMPLATE = """\
You review one spoken utterance by an adult learner of English whose first language is \
{l1_name_en}, and return corrections as JSON. The text comes from speech recognition. The target \
norm is General American English.

Return exactly one JSON object with this shape:
{{"items": [{{"quote": "...", "fix": "...", "type": "...", "note_l1": "...", "pattern": "..."}}], \
"better": "..."}}

WHAT TO CORRECT
- Real mistakes a fluent American speaker would notice in speech: grammar, wrong word, wrong \
preposition, word order, word-for-word translation from {l1_name_en}, false friends.
- At most three items, the most important first. If there are more mistakes, leave the minor \
ones out.
- If the utterance is acceptable spoken English, return {{"items": [], "better": ""}}.

WHAT TO LEAVE ALONE
- Punctuation, capitalization, apostrophes and spelling: they come from speech recognition, not \
from the learner.
- Fillers, false starts and repetitions: um, uh, well, like, you know, I mean.
- Informal spoken forms that are normal in American speech: gonna, wanna, kinda, yeah, sentence \
fragments as answers.
- Valid American usage. Do not change it to British usage.
- Any word listed in asr_unsure, and anything that looks like a misheard word, including \
homophones such as their and there, its and it's, to and too. Never quote these words.
- Style and word choice that is merely plain. Do not rewrite correct sentences to sound fancier.
- Facts and opinions. You correct language only.

FIELDS
- quote: the shortest fragment of learner_said that contains the mistake, copied character for \
character, usually two to five words. It must be a contiguous substring of learner_said.
- fix: the corrected replacement for exactly that fragment.
- type: one of grammar, vocabulary, phrasing.
- note_l1: one sentence in {l1_name_en}, at most 20 words, that explains the rule in simple \
terms. {l1_style} English words appear only when you quote the form itself. No praise and no \
filler.
- pattern: one key from the list below. Use other when nothing fits.
- better: the whole utterance as a fluent American speaker would naturally say it, with the same \
meaning and the same register. Empty string if items is empty.

MISTAKE KEYS (key [first languages whose speakers often make it]: example)
{pattern_lines}
Keys marked [{l1_short}] are typical for this learner; prefer them when they fit.

Adjust to the learner's level: at A2 and B1 focus on basic grammar and skip subtle points; at B2 \
and C1 also note unnatural phrasing.

EXAMPLE
Input:
{example_input}
Output:
{example_output}

Return only the JSON object."""

# A worked example per learner language with one of its speakers' typical mistakes (SPEC 5).
EXAMPLES: dict[str, dict[str, Any]] = {
    "es": {
        "input": {
            "level": "B1",
            "tutor_said": "Tell me a little about yourself.",
            "learner_said": "I have 30 years and I work in a bank since two years.",
            "asr_unsure": [],
        },
        "output": {
            "items": [
                {
                    "quote": "I have 30 years",
                    "fix": "I'm 30",
                    "type": "grammar",
                    "note_l1": "En inglés la edad se dice con be: I'm 30 o I'm 30 years old.",
                    "pattern": "age_have",
                },
                {
                    "quote": "I work in a bank since two years",
                    "fix": "I've worked at a bank for two years",
                    "type": "grammar",
                    "note_l1": "Para una duración que sigue hasta hoy se usa present perfect con "
                    "for: for two years.",
                    "pattern": "for_since",
                },
            ],
            "better": "I'm 30, and I've worked at a bank for two years.",
        },
    },
    "pt": {
        "input": {
            "level": "B1",
            "tutor_said": "What do you like about your city?",
            "learner_said": "In my city has a big park and the people is very friendly.",
            "asr_unsure": [],
        },
        "output": {
            "items": [
                {
                    "quote": "In my city has a big park",
                    "fix": "There's a big park in my city",
                    "type": "grammar",
                    "note_l1": "Para dizer que algo existe em um lugar, use there is, não have.",
                    "pattern": "there_is_have",
                },
                {
                    "quote": "the people is",
                    "fix": "people are",
                    "type": "grammar",
                    "note_l1": "People é plural e, falando em geral, vem sem the: people are.",
                    "pattern": "people_plural",
                },
            ],
            "better": "There's a big park in my city, and people are very friendly.",
        },
    },
}


def pattern_lines(patterns: list[dict[str, Any]]) -> str:
    lines = []
    for p in patterns:
        marks = ", ".join(p.get("l1", []))
        example = p.get("example_en") or ""
        lines.append(f"- {p['key']} [{marks}]" + (f": {example}" if example else ""))
    return "\n".join(lines)


def build_system_prompt(patterns: list[dict[str, Any]], lang: str) -> str:
    short = l1.short(lang)
    example = EXAMPLES.get(short, EXAMPLES["es"])
    return SYSTEM_TEMPLATE.format(
        l1_name_en=l1.name_en(lang),
        l1_style=l1.meta(lang).get("style", ""),
        l1_short=short,
        pattern_lines=pattern_lines(patterns),
        example_input=json.dumps(example["input"], ensure_ascii=False),
        example_output=json.dumps(example["output"], ensure_ascii=False),
    )


def build_user_message(level: str, tutor_said: str, learner_said: str, unsure: list[str]) -> str:
    return json.dumps(
        {
            "level": level,
            "tutor_said": tutor_said,
            "learner_said": learner_said,
            "asr_unsure": unsure,
        },
        ensure_ascii=False,
    )
