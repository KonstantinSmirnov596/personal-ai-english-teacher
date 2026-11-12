"""Unsupported hardware: the core explains why and loads nothing (plan item 3.6).

A fake detector reaches the core through dependency injection; the app has no switch that
fakes hardware. The window side is checked in ``tests/e2e/test_wizard.py``.
"""

from __future__ import annotations

import time
from pathlib import Path

from tests.helpers import make_app
from tests.hw_fakes import FakeDetector, machine


def test_unsupported_hardware_is_explained_and_models_stay_unloaded(tmp_path: Path) -> None:
    """Plan item 3.6: a fake detector (no NVIDIA GPU) reaches the core by injection; the core
    does not load models, does not crash, and explains why."""
    detector = FakeDetector(machine(gpu=None))
    with make_app(tmp_path, detector=detector, load_models=True) as ctx:
        deadline = time.monotonic() + 10
        while ctx.core.models.problem == "" and time.monotonic() < deadline:
            time.sleep(0.05)
        assert ctx.core.profile == "unsupported"
        assert ctx.core.models.problem == "unsupported_hardware"
        assert not ctx.core.stt.loaded and not ctx.core.tts.loaded
        health = ctx.client.get("/api/health").json()
        assert health["problems"][0]["code"] == "unsupported_hardware"
        assert health["problems"][0]["message_l1"]
        hw = ctx.client.get("/api/hardware").json()
        assert hw["profile"] == "unsupported" and hw["current"]["reasons"] == ["gpu"]
        assert detector.calls >= 2
