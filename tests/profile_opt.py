"""The model profile the gpu and e2e suites run under (SPEC 7: both profiles pass them).

``pytest --vt-profile compacto`` (``scripts\\test.ps1 gpu --vt-profile compacto``) is read by the
tests only. A running core is switched the way a user does it, through Settings → Performance
(``PATCH /api/settings {"profile": ...}``); models built directly in a test get the compute type
of the profile. The app itself has no switch for this.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from voicetutor import profiles

CHOICES = ("auto", "completo", "compacto")
PROFILE = "auto"


def set_profile(value: str) -> None:
    global PROFILE
    if value not in CHOICES:
        raise ValueError(value)
    PROFILE = value


def stt_compute_type() -> str:
    """Compute type of a speech recognizer built directly in a test."""
    return profiles.STT_COMPUTE_TYPE.get(PROFILE, profiles.STT_COMPUTE_TYPE["completo"])


def seed_profile(data_dir: Path) -> None:
    """Store the chosen profile in a data directory before a core starts there, as if the user
    had picked it in Settings → Performance earlier: the core loads its models that way."""
    if PROFILE == "auto":
        return
    from voicetutor.settings import SettingsPatch
    from voicetutor.storage.db import Database
    from voicetutor.storage.repo import SettingsRepo

    db = Database(data_dir / "voicetutor.db")
    try:
        SettingsRepo(db).patch(SettingsPatch(profile=PROFILE))  # type: ignore[arg-type]
    finally:
        db.close()


def apply_profile(http: Any) -> None:
    """Switch a running core to the chosen profile; ``auto`` keeps the core's own choice."""
    if PROFILE == "auto":
        return
    r = http.patch("/api/settings", json={"profile": PROFILE})
    r.raise_for_status()
    got = http.get("/api/hardware").json()["profile"]
    assert got == PROFILE, f"core runs {got}, tests asked for {PROFILE}"
