"""Hardware detector, run-time notices and video-memory shortage (plan items 3.1, 3.3, 3.7).

The core gets fake detectors and fake speech models through dependency injection; the app has
no switch that fakes hardware.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tests.helpers import make_app
from tests.hw_fakes import FakeDetector, FakeSTT, card, machine
from voicetutor.core import VramLowError, is_out_of_memory
from voicetutor.hardware import SystemDetector


def test_system_detector_reads_this_computer(tmp_path: Path) -> None:
    info = SystemDetector().detect(tmp_path)
    assert info.ram_total_mb > 0 and info.disk_free_mb > 0 and info.cpu_cores > 0
    if info.gpu is not None:  # a CI runner has no NVIDIA GPU
        assert info.gpu.vram_total_mb > 0 and info.gpu.compute_capability[0] >= 3


def test_notices_for_battery_and_changed_hardware(tmp_path: Path) -> None:
    detector = FakeDetector(machine(gpu=card(), battery=True))
    with make_app(tmp_path, detector=detector) as ctx:
        ctx.core.db.execute(
            "INSERT INTO hardware_profile(created_at, gpu_name, driver, profile)"
            " VALUES ('2026-01-01', 'NVIDIA GeForce RTX 3060 Laptop GPU', '566.36', 'completo')"
        )
        ctx.client.portal.call(ctx.core.detect_hardware)
        assert set(ctx.core.hardware_notices) == {"on_battery", "hardware_changed"}
        assert ctx.core.profile == "completo"  # the stored measurement of the same GPU


def test_out_of_memory_frees_the_phoneme_model_and_retries(tmp_path: Path) -> None:
    stt = FakeSTT(oom_times=1)
    with make_app(tmp_path, detector=FakeDetector(machine(gpu=card())), stt=stt) as ctx:
        freed: list[bool] = []

        async def free() -> None:
            freed.append(True)

        ctx.core.pron.free_memory = free  # type: ignore[method-assign]
        result = ctx.client.portal.call(ctx.core.transcribe, np.zeros(16000, dtype=np.float32))
        assert result.text == "hello" and freed == [True] and len(stt.calls) == 2


def test_persistent_out_of_memory_gives_a_clear_error(tmp_path: Path) -> None:
    """SPEC 7: no crash; the caller turns VramLowError into the "vram_low" message."""
    stt = FakeSTT(oom_times=5)
    with make_app(tmp_path, detector=FakeDetector(machine(gpu=card())), stt=stt) as ctx:
        with pytest.raises(VramLowError):
            ctx.client.portal.call(ctx.core.transcribe, np.zeros(16000, dtype=np.float32))
        assert ctx.client.get("/api/health").status_code == 200  # still serving
    assert is_out_of_memory(RuntimeError("CUDA failed with error out of memory"))
    assert not is_out_of_memory(RuntimeError("file not found"))


def test_notices_are_dismissed_once_per_run(tmp_path: Path) -> None:
    """SPEC 7: the battery notice is shown once; a dismissed notice stays away for the run."""
    detector = FakeDetector(machine(gpu=card(), battery=True))
    with make_app(tmp_path, detector=detector) as ctx:
        ctx.client.portal.call(ctx.core.detect_hardware)
        assert ctx.core.hardware_api()["notices"] == ["on_battery"]
        h = ctx.auth_headers
        r = ctx.client.post("/api/hardware/notices/on_battery/dismiss", headers=h)
        assert r.status_code == 204
        assert ctx.core.hardware_api()["notices"] == []
        ctx.client.portal.call(ctx.core.detect_hardware)  # e.g. a profile switch to "auto"
        assert ctx.core.hardware_notices == []
        r = ctx.client.post("/api/hardware/notices/whatever/dismiss", headers=h)
        assert r.status_code == 404


def test_hello_carries_profile_and_notices(tmp_path: Path) -> None:
    from tests.helpers import TEST_PORT

    detector = FakeDetector(machine(gpu=card(total=6144), battery=True))
    with make_app(tmp_path, detector=detector) as ctx:
        ctx.client.portal.call(ctx.core.detect_hardware)
        with ctx.client.websocket_connect(
            f"ws://127.0.0.1:{TEST_PORT}/ws", headers=ctx.auth_headers
        ) as ws:
            hello = ws.receive_json()
        assert hello["type"] == "hello"
        assert hello["hardware"]["profile"] == "compacto"
        assert hello["hardware"]["notices"] == ["on_battery"]
        assert hello["settings"]["pron_in_conversation"] is False


def test_models_status_and_load_without_download(tmp_path: Path, monkeypatch) -> None:
    """The wizard's model step: the app reports and loads models, it never downloads them."""
    from voicetutor.server import routes_hardware

    with make_app(tmp_path, detector=FakeDetector(machine(gpu=card()))) as ctx:
        h = ctx.auth_headers
        monkeypatch.setattr(
            routes_hardware, "_models_present", lambda: {"stt": True, "tts": False, "phoneme": True}
        )
        m = ctx.client.get("/api/models").json()
        assert m == {"present": {"stt": True, "tts": False, "phoneme": True}, "all_present": False}
        r = ctx.client.post("/api/models/load", headers=h)
        assert r.status_code == 409 and r.json()["error"]["code"] == "models_missing"
        assert ctx.client.post("/api/models/download", headers=h).status_code in (404, 405)
        started: list[bool] = []
        monkeypatch.setattr(
            routes_hardware, "_models_present", lambda: dict.fromkeys(m["present"], True)
        )
        monkeypatch.setattr(ctx.core, "reload_models", lambda: started.append(True) or True)
        r = ctx.client.post("/api/models/load", headers=h)
        assert r.status_code == 202 and r.json() == {"state": "loading"} and started == [True]
