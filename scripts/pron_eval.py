"""Evaluation of pronunciation scoring on synthesized speech, per learner language (stage 2).

1. False alarms: three American Kokoro voices read every reading phrase; share of phones that
   get the level "error" (and "close") when the reference uses the learner language's catalog.
2. Catalog mistakes: every catalog pair is spoken as the learner would say it (Kokoro phoneme
   override such as /ɛspˈik/ for "speak") inside carrier phrases; how often the target phone is
   flagged "error" and the heard sound (substitution, deletion or insertion) is named.

Writes docs/reports/data/pron_stage2_<lang>.json and prints a summary.
    .venv\\Scripts\\python.exe scripts\\pron_eval.py --lang es-419 [--carrier "Say {word} now."]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

LANGS = ("es-419", "pt-BR")
# An entry whose share of "error" judgements stays below this is listed as unreliable.
RELIABLE = 0.5


def normalize_heard(key: str) -> str:
    """Comparable form of a heard key: classes for sounds, '+class' for an insertion."""
    from voicetutor.pron.catalog import split_sequence, to_class

    if key.startswith("+"):
        return "+" + to_class(key[1:])
    return "".join(split_sequence(key))


def target_phone(ref: Any, word_index: int, entry: Any, heard: str) -> int | None:
    """First phone of the word where the catalog entry applies to the pair's heard sound."""
    from voicetutor.pron import catalog

    for w in ref.words:
        if w.source_index != word_index:
            continue
        for pi in w.phones:
            p = ref.phones[pi]
            if p.scored and entry.expects(p.cls) and catalog.position_ok(entry.position, p):
                if entry.detect != "substitution":
                    return pi
                want = normalize_heard(heard)
                if any(exp == p.cls and "".join(v) == want for exp, v in entry.pairs):
                    return pi
    return None


def evaluate(lang: str = "es-419", carriers: list[str] | None = None) -> dict[str, Any]:
    from tests.fixtures.make_fixtures import ensure_pairs, ensure_reading
    from voicetutor.gpu_env import prepare_cuda_dlls

    prepare_cuda_dlls()
    from voicetutor.pron import catalog
    from voicetutor.pron.assess import build_result, heard_of, judge
    from voicetutor.pron.engine import PronEngine
    from voicetutor.pron.phoneme_model import PhonemeModel
    from voicetutor.pron.reference import build_reference
    from voicetutor.speech.audio import STT_RATE, read_wav, resample

    engine = PronEngine(PhonemeModel())

    def load(path: Path) -> Any:
        audio, rate = read_wav(path)
        return resample(audio, rate, STT_RATE)

    # --- false alarms on native-like reading ------------------------------------------------
    per_sound: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "error": 0, "approx": 0})
    total = errors = approx = 0
    offenders: list[dict[str, Any]] = []
    timings: list[tuple[float, float]] = []
    for item in ensure_reading():
        text = item["phrase"]["text"]
        source = text.split()
        audio = load(item["path"])
        started = time.perf_counter()
        ref = build_reference(source, lang=lang)
        result = build_result(ref, engine.analyze(audio, ref), source)
        timings.append((len(audio) / STT_RATE, time.perf_counter() - started))
        for word in result["words"]:
            for ph in word["phones"]:
                if not ph["scored"]:
                    continue
                total += 1
                stat = per_sound[ph["cls"]]
                stat["n"] += 1
                if ph["level"] == "error":
                    errors += 1
                    stat["error"] += 1
                elif ph["level"] == "approx":
                    approx += 1
                    stat["approx"] += 1
                if ph["level"] != "ok":
                    offenders.append(
                        {
                            "phrase": item["phrase"]["id"],
                            "voice": item["voice"],
                            "word": word["w"],
                            "expected": ph["expected"],
                            "heard": ph["heard"],
                            "level": ph["level"],
                            "catalog_id": ph["catalog_id"],
                            "gop": ph["gop"],
                        }
                    )

    # --- catalog mistakes ---------------------------------------------------------------------
    cases: list[dict[str, Any]] = []
    for item in ensure_pairs(lang, carriers=carriers):
        entry = catalog.entry_by_id(item["entry_id"], lang)
        if entry is None:
            continue  # manual entries are not detected automatically
        source = item["reference_text"].split()
        ref = build_reference(source, lang=lang)
        ti = target_phone(ref, item["word_index"], entry, item["heard"])
        if ti is None:
            cases.append({"entry": entry.id, "skipped": "entry does not apply", **_meta(item)})
            continue
        evidence = engine.analyze(load(item["path"]), ref)
        p = ref.phones[ti]
        j = judge(p, evidence.phones[ti])
        heard = heard_of(p, j) if j.heard is not None else None
        # a pair may list several names for its mistake (catalog "names"): an American phoneme
        # model hears a tap as the flap /t, d/, an inserted vowel as /ə/ or /ɛ/
        accepted = {normalize_heard(n) for n in item.get("names") or [item["heard"]]}
        named = (
            j.entry is not None
            and j.entry.id == entry.id
            and heard is not None
            and normalize_heard(heard) in accepted
        )
        cases.append(
            {
                "entry": entry.id,
                "default_level": entry.default_level,
                "target": p.symbol,
                "level": j.level,
                "judged_entry": j.entry.id if j.entry else None,
                "heard": heard,
                "llr": round(j.llr, 2),
                "diagnosis_ok": bool(named),
                **_meta(item),
            }
        )

    scored = [c for c in cases if "skipped" not in c]

    def rates(selected: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(selected)
        return {
            "cases": n,
            "error": round(sum(c["level"] == "error" for c in selected) / n, 3) if n else None,
            "flagged": round(sum(c["level"] != "ok" for c in selected) / n, 3) if n else None,
            "diagnosis": round(sum(c["diagnosis_ok"] for c in selected) / n, 3) if n else None,
        }

    by_entry = {
        e: rates([c for c in scored if c["entry"] == e])
        for e in dict.fromkeys(c["entry"] for c in scored)
    }
    error_entries = [e.id for e in catalog.entries(lang) if e.default_level == "error"]
    unreliable = {
        e: r
        for e, r in by_entry.items()
        if (r["error"] if e in error_entries else r["flagged"]) is not None
        and (r["error"] if e in error_entries else r["flagged"]) < RELIABLE
    }
    five = [t for d, t in timings if 4.0 <= d <= 6.0] or [t for _, t in timings]
    return {
        "lang": lang,
        "carriers": sorted({c["carrier"] for c in cases}),
        "false_alarms": {
            "phones": total,
            "error": errors,
            "approx": approx,
            "error_rate": round(errors / total, 4) if total else None,
            "approx_rate": round(approx / total, 4) if total else None,
            "per_sound": dict(sorted(per_sound.items(), key=lambda kv: -kv[1]["n"])),
            "offenders": offenders,
        },
        "mistakes": {
            "error_level_entries": rates([c for c in scored if c["entry"] in error_entries]),
            "approx_level_entries": rates([c for c in scored if c["entry"] not in error_entries]),
            "all": rates(scored),
            "by_entry": by_entry,
            "unreliable": unreliable,
            "skipped": [c for c in cases if "skipped" in c],
            "cases": scored,
        },
        "timing": {
            "analysis_s_median_for_5s_phrase": round(sorted(five)[len(five) // 2], 3),
            "analysis_s_max": round(max(t for _, t in timings), 3),
        },
    }


def _meta(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "expected": item["expected"],
        "actual": item["actual"],
        "pair_heard": item["heard"],
        "voice": item["voice"],
        "carrier": item["carrier"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=LANGS, action="append", help="default: both")
    ap.add_argument("--carrier", action="append", default=None, help="experimental carrier")
    args = ap.parse_args()
    for lang in args.lang or LANGS:
        result = evaluate(lang, args.carrier)
        if args.carrier is None:
            out = REPO / "docs" / "reports" / "data" / f"pron_stage2_{lang}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        fa = result["false_alarms"]
        print(
            f"[{lang}] false alarms: error {fa['error']}/{fa['phones']} = {fa['error_rate']:.2%},"
            f" approx {fa['approx_rate']:.2%}"
        )
        for o in fa["offenders"]:
            if o["level"] == "error":
                print(
                    f"   error {o['phrase']} {o['voice']:10} {o['word']:10}"
                    f" {o['expected']} -> {o['heard'] or '∅'} {o['catalog_id']} ({o['gop']})"
                )
        m = result["mistakes"]
        print(f"[{lang}] error-level entries:", m["error_level_entries"])
        print(f"[{lang}] approx-level entries:", m["approx_level_entries"])
        for entry, r in m["by_entry"].items():
            print(f"   {entry:22} {r}")
        print(f"[{lang}] unreliable:", m["unreliable"])
        for s in m["skipped"]:
            print("   skipped:", s)
        print(f"[{lang}] timing:", result["timing"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
