"""Access to the bundled data files in ``voicetutor/data``."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"


@cache
def load_json(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def scenarios() -> list[dict[str, Any]]:
    return list(load_json("scenarios.json")["scenarios"])


def patterns() -> list[dict[str, Any]]:
    return list(load_json("patterns.json")["patterns"])


def pattern_keys() -> list[str]:
    return [p["key"] for p in patterns()]


def pattern_by_key() -> dict[str, dict[str, Any]]:
    return {p["key"]: p for p in patterns()}


def reading_phrases() -> dict[str, Any]:
    return dict(load_json("reading_phrases.json"))


def l1_catalog(lang: str) -> dict[str, Any]:
    """Pronunciation catalog of a learner language (voicetutor/data/l1/<code>/catalog.json)."""
    return dict(json.loads((DATA_DIR / "l1" / lang / "catalog.json").read_text(encoding="utf-8")))


def corrector_eval(lang: str) -> list[dict[str, Any]]:
    """Corrector evaluation cases for one learner language (live suite, docs/testing.md)."""
    path = DATA_DIR / "l1" / lang / "corrector_eval.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def provider_templates() -> list[dict[str, Any]]:
    """LLM provider templates (docs/reports/providers.md), in display order."""
    return list(load_json("providers.json")["templates"])
