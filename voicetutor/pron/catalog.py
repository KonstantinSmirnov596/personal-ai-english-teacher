"""Catalog of typical pronunciation mistakes of a learner language (SPEC 12).

Each learner language has ``voicetutor/data/l1/<code>/catalog.json``. Symbols are ordinary IPA;
here they are normalized to the scoring classes (``voicetutor/pron/inventory.py``) and matched
against "expected -> heard" pairs. Three kinds of mistakes are detected:

- substitution: another sound (or a sequence such as ŋ+ɡ, ɛ+ɾ) in place of the expected one;
- deletion: the expected sound is missing;
- insertion: an extra sound before or after the expected one ("espeak", "bigi"), shown as
  ``+ɛ``. Insertions are only tried at the positions the catalog names, so they do not
  multiply false alarms elsewhere.

Competitors that the generic reference does not try (insertions, catalog sequences) are added
by :func:`add_competitors` for the phones where an entry of the current language applies.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from typing import Any

from voicetutor import l1
from voicetutor.pron.inventory import CONSONANTS, R_COLORED, VOWELS
from voicetutor.pron.reference import Reference, RefPhone, Variant

# ordinary IPA of the catalog -> scoring class
IPA_TO_CLASS = {
    "ɝ": "ɜː",
    "ɜ": "ɜː",
    "ɚ": "ɜː",
    "ɑ": "ɑː",
    "ɔ": "ɔː",
    "o": "ɔː",
    "i": "iː",
    "u": "uː",
    "e": "ɛ",
    "a": "ɑː",
    "β": "b",
    "ʝ": "j",
}
SONORANTS = frozenset({"m", "n", "ŋ", "l", "ɹ", "w", "j"})
HIGH_FRONT = frozenset({"iː", "ɪ"})
TWO_LETTER_CLASSES = sorted(
    (c for c in [*CONSONANTS, *VOWELS] if len(c) > 1), key=len, reverse=True
)


def to_class(symbol: str) -> str:
    return IPA_TO_CLASS.get(symbol, symbol)


def split_sequence(heard: str) -> Variant:
    """'ŋɡ' -> ('ŋ', 'ɡ'), 'ɛɾ' -> ('ɛ', 'ɾ'), 'ɪd' -> ('ɪ', 'd'), 'tʃ' -> ('tʃ',)."""
    out: list[str] = []
    i = 0
    while i < len(heard):
        cls = next((c for c in TWO_LETTER_CLASSES if heard.startswith(c, i)), None)
        if cls is None:
            cls = heard[i]
        out.append(to_class(cls))
        i += len(cls)
    return tuple(out)


@dataclass(frozen=True)
class CatalogEntry:
    id: str
    position: str
    detect: str
    default_level: str
    priority: int
    title_l1: str
    tip_l1: str
    expected: tuple[str, ...]  # expected classes; ("*",) = any consonant
    pairs: tuple[tuple[str, Variant], ...]  # (expected class, heard variant)
    insert_where: str  # "", "before" or "after"
    insert_sounds: tuple[str, ...]
    examples: tuple[tuple[str, str, str], ...]  # (heard key, expected word, heard word)

    def example_for(self, heard: str) -> tuple[str, str] | None:
        for key, a, b in self.examples:
            if key == heard:
                return a, b
        return (self.examples[0][1], self.examples[0][2]) if self.examples else None

    def expects(self, cls: str) -> bool:
        if "*" in self.expected:
            return cls in CONSONANTS
        return cls in self.expected


def heard_key(variant: Variant) -> str:
    """Key of a competitor: '' for a deletion, the class for one phone, joined for sequences."""
    return "".join(variant)


def _load(code: str) -> dict[str, Any]:
    path = l1.L1_DIR / l1.resolve(code) / "catalog.json"
    return dict(json.loads(path.read_text(encoding="utf-8")))


@cache
def entries(code: str = "") -> tuple[CatalogEntry, ...]:
    """Automatically detected entries of a learner language (manual ones are left out)."""
    out: list[CatalogEntry] = []
    for e in _load(code)["entries"]:
        if e.get("detect") == "manual":
            continue
        pairs: list[tuple[str, Variant]] = []
        if "expected_map" in e:
            pairs = [(to_class(a), split_sequence(b)) for a, b in e["expected_map"]]
            expected = tuple(dict.fromkeys(a for a, _ in pairs))
        else:
            expected = ("*",) if e["expected"] == "*" else (to_class(e["expected"]),)
            if e.get("detect") == "deletion":
                pairs = [(x, ()) for x in expected]
            elif e.get("detect") == "substitution":
                pairs = [(expected[0], split_sequence(h)) for h in e.get("heard", [])]
        insert = e.get("insert") or {}
        examples = tuple(
            (str(p["heard"]), p["words"][0], p["words"][1]) for p in e.get("pairs", [])
        )
        out.append(
            CatalogEntry(
                id=e["id"],
                position=e.get("position", "any"),
                detect=e.get("detect", "substitution"),
                default_level=e.get("default_level", "approx"),
                priority=int(e.get("priority", 3)),
                title_l1=e.get("title", ""),
                tip_l1=e.get("tip", ""),
                expected=expected,
                pairs=tuple(pairs),
                insert_where=str(insert.get("where", "")),
                insert_sounds=tuple(to_class(s) for s in insert.get("sounds", [])),
                examples=examples,
            )
        )
    return tuple(out)


def raw_entries(code: str) -> list[dict[str, Any]]:
    """All entries as written in the file, including manual ones (statistics, docs)."""
    return list(_load(code)["entries"])


def entry_by_id(entry_id: str, code: str = "") -> CatalogEntry | None:
    return next((e for e in entries(code) if e.id == entry_id), None)


def position_ok(position: str, p: RefPhone) -> bool:
    if position == "any":
        return True
    if position == "word_final":
        return p.word_final
    if position == "word_initial":
        return p.word_initial
    if position == "stressed":
        return p.stressed
    if position == "unstressed":
        return not p.stressed
    if position == "after_vowel":
        return p.after_vowel or p.cls in R_COLORED or p.cls == "ɜː"
    if position == "s_cluster":  # speak, student: s + consonant at the start of a word
        return p.word_initial and p.cls == "s" and p.next_in_word in CONSONANTS
    if position == "word_final_obstruent":  # big, book: a final consonant that is not a sonorant
        return p.word_final and p.cls in CONSONANTS and p.cls not in SONORANTS
    if position == "word_final_cluster":  # world, hand: a final consonant after a consonant
        return p.word_final and p.cls in CONSONANTS and p.prev_in_word in CONSONANTS
    if position == "ed_suffix":  # worked, liked: -ed that is not a syllable of its own
        text = p.word_text.lower().strip("'")
        return (
            p.word_final
            and p.cls in ("t", "d")
            and text.endswith("ed")
            and p.prev_in_word in CONSONANTS
            and p.prev_in_word not in ("t", "d")
        )
    if position == "before_high_front_vowel":  # party, city: t, d before i
        return p.next_in_word in HIGH_FRONT
    if position == "coda":  # feel, milk: a consonant that closes a syllable
        return p.word_final or (p.next_in_word in CONSONANTS)
    return False


def _insertion_variants(entry: CatalogEntry, p: RefPhone) -> list[tuple[str, Variant]]:
    base = p.canonical
    out: list[tuple[str, Variant]] = []
    for s in entry.insert_sounds:
        variant = (s, *base) if entry.insert_where == "before" else (*base, s)
        out.append(("+" + s, variant))
    return out


def add_competitors(ref: Reference) -> None:
    """Add the competitors of the language's catalog that the generic reference does not try."""
    for p in ref.phones:
        if not p.scored:
            continue
        for e in entries(p.lang):
            if not e.expects(p.cls) or not position_ok(e.position, p):
                continue
            new: list[Variant] = []
            if e.detect == "insertion":
                new = [v for _, v in _insertion_variants(e, p)]
            else:
                new = [v for exp, v in e.pairs if exp == p.cls and len(v) > 1]
                if e.detect == "deletion" and () not in p.accept:
                    new.append(())
            for v in new:
                if v not in p.competitors and v not in p.accept:
                    p.competitors.append(v)


def _candidates(p: RefPhone, variant: Variant) -> list[tuple[str, Variant]]:
    """(expected, heard) keys under which a competitor is looked up in the catalog."""
    cls = p.cls
    out = [(cls, variant)]
    if cls in R_COLORED:
        vowel = R_COLORED[cls]
        if variant == (vowel,):
            out.append(("ɹ", ()))  # r dropped after a vowel
        elif len(variant) == 2 and variant[0] == vowel and variant[1] in ("r", "ɾ"):
            out.append(("ɹ", (variant[1],)))  # trilled or tapped r
    elif cls == "ɜː":
        if variant == ("ə",) and not p.stressed:
            out.append(("ɹ", ()))  # "mother" without the r-coloring
        head = variant[0] if variant else ""
        if head in R_COLORED:  # "word" said as "ward" or "werd"
            out.append((cls, (R_COLORED[head],)))
            out.append((cls, (R_COLORED[head], "ɹ")))
    return out


def match(p: RefPhone, variant: Variant) -> CatalogEntry | None:
    """Catalog entry for "expected p, heard variant", or None for an uncatalogued confusion."""
    best: CatalogEntry | None = None
    for e in entries(p.lang):
        if not position_ok(e.position, p):
            continue
        hit = False
        if e.detect == "insertion":
            hit = e.expects(p.cls) and variant in [v for _, v in _insertion_variants(e, p)]
        else:
            for exp, heard in _candidates(p, variant):
                if (exp, heard) in e.pairs or (
                    e.detect == "deletion" and heard == () and e.expects(exp)
                ):
                    hit = True
                    break
        if hit and (best is None or e.priority < best.priority):
            best = e
    return best


def heard_display(entry: CatalogEntry | None, p: RefPhone, variant: Variant | None) -> str:
    """What the learner said: '+ɛ' for an insertion, the joined sounds otherwise."""
    if variant is None:
        return p.symbol
    if entry is not None and entry.detect == "insertion":
        for key, v in _insertion_variants(entry, p):
            if v == variant:
                return key
    return "".join(variant)


def tip(entry: CatalogEntry, heard: str) -> dict[str, Any]:
    pair = entry.example_for(heard)
    return {
        "catalog_id": entry.id,
        "title_l1": entry.title_l1,
        "tip_l1": entry.tip_l1,
        "pair": list(pair) if pair else None,
    }
