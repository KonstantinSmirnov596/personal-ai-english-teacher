"""Language guard: is a text written in a learner language rather than in English?

Learner-language text (corrections, translations, tips) must never reach speech synthesis, and
the English fields of LLM answers must stay English (SPEC 5). The guard counts frequent words
of each learner language (``detector.words`` in ``voicetutor/data/l1/<code>/meta.json``) against
English function words. Names do not count: a capitalized word in the middle of a sentence
("José", "São Paulo", "Los Angeles") and lower-case particles between capitalized words
("Rio de Janeiro", "Maria da Silva") are skipped. So English sentences with Spanish or
Portuguese names and places pass, while sentences in those languages are caught.

The word lists leave out words that are also common English words ("no", "do", "me", "son").
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import cache

from voicetutor import l1

_WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?")
_SENTENCE_END = re.compile(r"[.!?¿¡:;\"“”«»()\n]")
_INVERTED = re.compile("[¿¡]")  # Spanish-only punctuation

_ENGLISH_TEXT = """
    the a an and or but if so because i you he she it we they me him her us them my your his
    its our their this that these those is are was were be been being am have has had do does
    did will would can could should shall may might must not to of in on at for with from by
    about into over after before than then there here what which who whom whose when where why
    how all any some no yes very just also only too more most much many such own same other
    let's i'm you're it's that's don't doesn't didn't isn't aren't wasn't can't won't i've
    we're they're i'll you'll we'll i'd you'd there's what's
"""
# Words that are also frequent in Spanish or Portuguese ("a", "no", "me", "do", "as") count for
# neither side.
_AMBIGUOUS = frozenset({"a", "no", "me", "do", "as", "so", "son", "come", "en", "e", "o"})
ENGLISH_FUNCTION_WORDS = frozenset(_ENGLISH_TEXT.split()) - _AMBIGUOUS


@dataclass(frozen=True)
class Verdict:
    language: str | None  # learner language code, or None when the text reads as English
    learner_hits: int
    english_hits: int


def _fold(word: str) -> str:
    return unicodedata.normalize("NFC", word.lower().replace("’", "'"))


@cache
def _lists() -> dict[str, frozenset[str]]:
    return {
        code: frozenset(_fold(w) for w in meta["detector"]["words"])
        for code, meta in l1.metas().items()
    }


@cache
def _letters() -> dict[str, frozenset[str]]:
    """Letters typical for each learner language and absent from English words.

    "é" is left out on purpose: English loanwords such as café and résumé use it.
    """
    return {
        code: frozenset(meta["detector"].get("letters", "")) for code, meta in l1.metas().items()
    }


def _tokens(text: str) -> list[tuple[str, bool]]:
    """Words with a flag: True when the word starts a sentence."""
    out: list[tuple[str, bool]] = []
    start = True
    pos = 0
    for m in _WORD.finditer(text):
        if _SENTENCE_END.search(text[pos : m.start()]):
            start = True
        out.append((m.group(0), start))
        start = False
        pos = m.end()
    return out


def _is_name(word: str, sentence_start: bool) -> bool:
    return word[:1].isupper() and not sentence_start


def _particles(tokens: list[tuple[str, bool]], words: frozenset[str]) -> set[int]:
    """Indexes of lower-case learner words between capitalized words (Maria de la Cruz)."""
    out: set[int] = set()
    for i, (word, _start) in enumerate(tokens):
        if not word[:1].isupper():
            continue
        j = i + 1
        while j < len(tokens) and not tokens[j][0][:1].isupper() and _fold(tokens[j][0]) in words:
            j += 1
        if j > i + 1 and j < len(tokens) and tokens[j][0][:1].isupper():
            out.update(range(i + 1, j))
    return out


def classify(text: str) -> Verdict:
    tokens = _tokens(text or "")
    if not tokens:
        return Verdict(None, 0, 0)
    english = sum(1 for w, _s in tokens if _fold(w) in ENGLISH_FUNCTION_WORDS)
    best_code: str | None = None
    best_hits = 0
    for code, words in _lists().items():
        skip = _particles(tokens, words)
        letters = _letters()[code]
        hits = sum(
            1
            for i, (w, s) in enumerate(tokens)
            if i not in skip
            and not _is_name(w, s)
            # a listed word, or a lower-case word with letters English never uses (ñ, ã, ç, ó...)
            and (_fold(w) in words or (letters and any(c in letters for c in _fold(w))))
        )
        if hits > best_hits:
            best_code, best_hits = code, hits
    if _INVERTED.search(text or ""):
        spanish = next((c for c in _lists() if l1.short(c) == "es"), best_code)
        return Verdict(spanish, max(best_hits, 1), english)
    if best_code is None:
        return Verdict(None, 0, english)
    if best_hits >= 2 and best_hits > english:
        return Verdict(best_code, best_hits, english)
    if best_hits >= 1 and english == 0 and len(tokens) <= 3:
        return Verdict(best_code, best_hits, english)  # short replies: "Gracias", "Muito bom"
    return Verdict(None, best_hits, english)


def is_learner_language(text: str) -> bool:
    return classify(text).language is not None


class LearnerLanguageError(ValueError):
    """Text in a learner language was about to be spoken."""


def has_foreign_script(text: str) -> bool:
    """A letter outside the Latin script (Cyrillic, Greek, CJK, ...): never English."""
    return any(ch.isalpha() and not unicodedata.name(ch, "").startswith("LATIN") for ch in text)


def not_english(text: str) -> bool:
    """True when the text must not be treated as English (synthesis, English answer fields)."""
    return bool(text) and (has_foreign_script(text) or is_learner_language(text))
