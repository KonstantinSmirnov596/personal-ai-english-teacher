"""Learner languages (L1): discovered from files, no code per language (SPEC 5).

A learner language is a directory ``voicetutor/data/l1/<code>/`` with:

- ``meta.json`` — code, names, HTML language tag, Windows locale prefixes, detector words;
- ``messages.json`` — texts produced by the core (errors, connection test results);
- ``patterns.json`` — names and hints of the recurring-mistake keys;
- ``catalog.json`` and ``reading_phrases.json`` — pronunciation (stage 2).

The window's strings live next to the page in ``web/i18n/<code>.js``.
"""

from __future__ import annotations

import ctypes
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

L1_DIR = Path(__file__).resolve().parent / "data" / "l1"
FALLBACK = "es-419"
META_FIELDS = ("code", "name_native", "name_en", "html_lang", "catalog_l1", "windows_locales")


def discover(root: Path = L1_DIR) -> dict[str, dict[str, Any]]:
    """All learner languages under ``root``: code -> meta. Sorted by code."""
    found: dict[str, dict[str, Any]] = {}
    for meta_file in sorted(root.glob("*/meta.json")):
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        missing = [f for f in META_FIELDS if f not in meta]
        if missing:
            raise ValueError(f"{meta_file}: missing {missing}")
        if meta["code"] != meta_file.parent.name:
            raise ValueError(f"{meta_file}: code {meta['code']!r} differs from the directory name")
        found[meta["code"]] = meta
    return found


@cache
def metas() -> dict[str, dict[str, Any]]:
    return discover()


def codes() -> list[str]:
    return list(metas())


def is_known(code: str) -> bool:
    return code in metas()


def meta(code: str) -> dict[str, Any]:
    return metas().get(code) or metas()[FALLBACK]


def resolve(code: str | None) -> str:
    """A known code: the given one, else the fallback."""
    return code if code and is_known(code) else FALLBACK


@cache
def _load(code: str, name: str) -> Any:
    path = L1_DIR / code / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def messages(code: str) -> dict[str, Any]:
    return dict(_load(resolve(code), "messages.json") or {})


def patterns(code: str) -> dict[str, dict[str, str]]:
    data = _load(resolve(code), "patterns.json") or {}
    return dict(data.get("patterns", {}))


def name_en(code: str) -> str:
    return str(meta(resolve(code))["name_en"])


def html_lang(code: str) -> str:
    return str(meta(resolve(code))["html_lang"])


def short(code: str) -> str:
    """Two-letter family used to mark catalog entries and mistake keys (``es``, ``pt``)."""
    return str(meta(resolve(code))["catalog_l1"])


def for_locale(locale_name: str, available: dict[str, dict[str, Any]] | None = None) -> str:
    """Learner language suggested by a Windows locale name such as ``es-MX`` or ``pt-BR``.

    SPEC 5: ``es-*`` -> Spanish, ``pt-*`` -> Portuguese, anything else -> Spanish.
    """
    langs = available if available is not None else metas()
    prefix = (locale_name or "").split("-")[0].split("_")[0].lower()
    for code, m in langs.items():
        if prefix and prefix in [p.lower() for p in m.get("windows_locales", [])]:
            return code
    return FALLBACK if FALLBACK in langs else next(iter(langs))


def windows_locale() -> str:
    """The user's default locale name from Windows (``GetUserDefaultLocaleName``), or ''."""
    if sys.platform != "win32":
        return ""
    buf = ctypes.create_unicode_buffer(85)  # LOCALE_NAME_MAX_LENGTH
    try:
        n = ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, len(buf))
    except (AttributeError, OSError):
        return ""
    return buf.value if n else ""


def default_code() -> str:
    """First-run suggestion; the user confirms it (wizard, stage 3) or changes it in Settings."""
    return for_locale(windows_locale())
