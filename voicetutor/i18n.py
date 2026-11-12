"""Texts the core produces for the window (error messages, connection test results).

They come from ``voicetutor/data/l1/<code>/messages.json`` in the current learner language. The
window shows its own strings from ``web/i18n/<code>.js`` by error ``code``; these texts are the
core-side detail (protocol fields ``message_l1``).
"""

from __future__ import annotations

from collections.abc import Callable

from voicetutor import l1

_current: Callable[[], str] = l1.default_code


def set_current(provider: Callable[[], str]) -> None:
    """The core registers how to read the learner language from the settings."""
    global _current
    _current = provider


def current() -> str:
    try:
        return l1.resolve(_current())
    except Exception:  # settings unreadable (database closed): fall back, never fail an error path
        return l1.FALLBACK


def text(key: str, lang: str | None = None) -> str:
    return str(l1.messages(lang or current())[key])


def error_text(code: str, lang: str | None = None) -> str:
    errors = l1.messages(lang or current())["errors"]
    return str(errors.get(code) or errors["internal"])
