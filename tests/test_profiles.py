"""Profiles completo / compacto / unsupported (SPEC 7, plan item 3.2)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from tests.helpers import make_app
from tests.hw_fakes import FakeDetector, FakePhonemeModel, FakeSTT, card, machine
from voicetutor import profiles
from voicetutor.hardware import HardwareInfo


def test_profiles_from_measured_free_memory() -> None:
    """SPEC 7: completo from 7 GB free, compacto from 5 GB, unsupported below."""
    assert profiles.assess(machine(gpu=card(free=7400)), measured=True).profile == "completo"
    assert profiles.assess(machine(gpu=card(free=5600)), measured=True).profile == "compacto"
    low = profiles.assess(machine(gpu=card(free=4000)), measured=True)
    assert low.profile == "unsupported" and [c.id for c in low.reasons] == ["vram"]
    # the app's own loaded models count as available memory
    again = profiles.assess(machine(gpu=card(free=4000)), measured=True, extra_free_mb=3600)
    assert again.profile == "completo"


def test_profile_estimate_before_the_wizard() -> None:
    """Without a measurement the total video memory decides; a game left open does not lock
    the app at start-up."""
    busy = machine(gpu=card(total=8151, free=1000))
    assert profiles.assess(busy, measured=False).profile == "completo"
    six = machine(gpu=card(total=6144, free=5000))
    assert profiles.assess(six, measured=False).profile == "compacto"
    four = profiles.assess(machine(gpu=card(total=4096, free=3000)), measured=False)
    assert four.profile == "unsupported" and [c.id for c in four.reasons] == ["vram"]


@pytest.mark.parametrize(
    ("info", "reason"),
    [
        (machine(gpu=None), "gpu"),
        (machine(gpu=card(driver="566.36")), "driver"),
        (machine(gpu=card(cc=(7, 0))), "architecture"),
        (machine(gpu=card(cc=(6, 1))), "architecture"),
    ],
)
def test_unsupported_reasons(info: HardwareInfo, reason: str) -> None:
    a = profiles.assess(info, measured=True)
    assert a.profile == "unsupported"
    assert reason in [c.id for c in a.reasons]
    api = a.to_api()
    assert reason in api["reasons"]
    assert all(c["doc"].startswith("hardware.md#") for c in api["checks"])


def test_minimum_hardware_is_supported() -> None:
    """Turing 7.5 with the minimum driver and a 6 GB card is the floor (stage 0 facts)."""
    turing = card(total=6144, free=5300, driver="572.61", cc=(7, 5))
    assert profiles.assess(machine(gpu=turing), measured=True).profile == "compacto"


def test_warnings_do_not_block() -> None:
    a = profiles.assess(
        machine(gpu=card(), ram_mb=8000, disk_mb=500, battery=True, build=19044), measured=True
    )
    assert a.profile == "completo"
    assert {c.id for c in a.warnings} == {"ram", "disk", "power", "windows"}
    assert not a.reasons


def test_benchmark_can_lower_the_profile() -> None:
    assert profiles.after_benchmark("completo", 800, 1500) == "completo"
    assert profiles.after_benchmark("completo", 1300, 1500) == "compacto"
    assert profiles.after_benchmark("completo", 800, 600) == "compacto"
    assert profiles.after_benchmark("compacto", 2000, 100) == "compacto"


def test_compacto_profile_settings(tmp_path: Path) -> None:
    detector = FakeDetector(machine(gpu=card(total=6144, free=5800)))
    stt = FakeSTT()
    with make_app(tmp_path, detector=detector, stt=stt) as ctx:
        ctx.client.portal.call(ctx.core.detect_hardware)
        assert ctx.core.profile == "compacto"
        assert stt.compute_type == "int8_float16"
        settings = ctx.client.get("/api/settings").json()
        assert settings["pron_in_conversation"] is False  # SPEC 7: marks off by default
        h = ctx.auth_headers
        r = ctx.client.patch("/api/settings", json={"pron_in_conversation": True}, headers=h)
        assert r.json()["pron_in_conversation"] is True  # the user's choice wins
        r = ctx.client.patch("/api/settings", json={"profile": "completo"}, headers=h)
        assert r.status_code == 200 and ctx.core.profile == "completo"
        assert stt.compute_type == "float16"


def test_phoneme_model_unloads_after_idle_in_compacto(tmp_path: Path) -> None:
    with make_app(tmp_path, detector=FakeDetector(machine(gpu=card(total=6144)))) as ctx:
        call = ctx.client.portal.call
        call(ctx.core.detect_hardware)
        assert ctx.core.profile == "compacto"
        model = FakePhonemeModel()
        ctx.core.pron.model = model  # type: ignore[assignment]
        ctx.core.pron.last_used = time.monotonic()
        call(ctx.core.pron.unload_when_idle)
        assert model.loaded  # used a moment ago
        ctx.core.pron.last_used = time.monotonic() - 301
        call(ctx.core.pron.unload_when_idle)
        assert not model.loaded
        assert ctx.core.models.phoneme == "not_loaded"


def test_phoneme_model_stays_in_completo(tmp_path: Path) -> None:
    with make_app(tmp_path, detector=FakeDetector(machine(gpu=card()))) as ctx:
        call = ctx.client.portal.call
        call(ctx.core.detect_hardware)
        assert ctx.core.profile == "completo"
        model = FakePhonemeModel()
        ctx.core.pron.model = model  # type: ignore[assignment]
        ctx.core.pron.last_used = time.monotonic() - 3600
        call(ctx.core.pron.unload_when_idle)
        assert model.loaded
