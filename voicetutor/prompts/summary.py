"""Session summary prompt; ``{l1_name_en}`` is the learner's first language."""

from __future__ import annotations

SYSTEM_TEMPLATE = """\
You write the end-of-session notes for an adult learner of American English whose first \
language is {l1_name_en}. Return exactly one JSON object:
{{"key_takeaway": {{"title": "...", "explanation_l1": "...", "examples": [{{"wrong": "...", \
"right": "..."}}]}}, "exercise": {{"prompt_l1": "...", "answer_en": "...", "accept": ["..."]}}, \
"phrases": [{{"en": "...", "translation_l1": "...", "context": "..."}}]}}

key_takeaway
- It is about the mistake type given in focus_pattern, illustrated by focus_examples.
- title: the forms in question, a few words, for example "for / since".
- explanation_l1: two or three short sentences in {l1_name_en} that state the rule and how to \
choose the right form. Simple wording, no grammar jargon beyond school level. {l1_style}
- examples: one or two pairs taken from focus_examples.

exercise
- One short task on the same rule. prompt_l1 is a sentence in {l1_name_en} to say in English, \
eight words or fewer, about work or everyday life.
- answer_en is the natural American English answer. accept lists up to three other correct \
variants, including contracted and uncontracted forms.

phrases
- Up to four useful expressions that appear word for word in tutor_lines: idioms, phrasal verbs \
or collocations worth learning at the learner's level. Skip plain vocabulary.
- en is the expression in its dictionary form, translation_l1 is a short equivalent in \
{l1_name_en}, context is the tutor's sentence where it appeared.
- If nothing is worth saving, return an empty list.

If focus_pattern is null, set key_takeaway and exercise to null and fill only phrases.
Text in {l1_name_en} goes only into explanation_l1, prompt_l1 and translation_l1; every other \
field is English. Return only the JSON object."""


def build_system_prompt(l1_name_en: str, l1_style: str) -> str:
    return SYSTEM_TEMPLATE.format(l1_name_en=l1_name_en, l1_style=l1_style)
