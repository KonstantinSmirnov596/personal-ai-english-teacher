"""Video memory pressure on the real GPU (plan item 3.3, SPEC 7).

Another program (this test process) takes almost all free video memory while the core runs.
The core must keep serving: a pronunciation check and a conversation turn either work (Windows
drivers may fall back to system memory) or end with the clear ``vram_low`` message; the process
never dies, and everything works again once the memory is released.
"""

from __future__ import annotations

import contextlib
import os
import secrets
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from tests.fixtures.make_fixtures import ensure_reading, ensure_turns
from tests.launcher_proc import LauncherProcess
from tests.mock_llm import MockLLM
from tests.ws_client import WSClient
from voicetutor.speech.audio import read_wav, wav_bytes

pytestmark = pytest.mark.gpu

LEAVE_FREE_MB = 150


@pytest.fixture
def core(tmp_path: Path) -> Iterator[dict[str, Any]]:
    key = "sk-test-" + secrets.token_urlsafe(24)
    mock = MockLLM(key).start()
    lp = LauncherProcess(tmp_path)
    try:
        lp.login()
        with lp.http() as http:
            r = http.post(
                "/api/connections",
                json={"name": "Mock", "base_url": mock.base_url, "model": "m", "api_key": key},
            )
            assert r.status_code == 201, r.text
            deadline = time.monotonic() + 180
            while http.get("/api/health").json()["status"] != "ok":
                assert time.monotonic() < deadline, "models did not load"
                time.sleep(0.5)
        yield {"lp": lp, "mock": mock}
    finally:
        lp.stop()
        mock.stop()
        import keyring

        for i in range(1, 3):
            with contextlib.suppress(Exception):
                keyring.delete_password(os.environ["VOICETUTOR_KEYRING_SERVICE"], f"connection-{i}")


def fill_video_memory() -> list[Any]:
    """Allocate in chunks until about LEAVE_FREE_MB stay free on the device."""
    import torch

    hog: list[Any] = []
    while True:
        free, _total = torch.cuda.mem_get_info()
        spare = free - LEAVE_FREE_MB * 2**20
        if spare < 64 * 2**20:
            return hog
        size = min(spare, 512 * 2**20)
        try:
            hog.append(torch.empty(size, dtype=torch.uint8, device="cuda"))
        except torch.OutOfMemoryError:
            return hog


def reading_body() -> bytes:
    item = next(i for i in ensure_reading() if i["phrase"]["id"] == "p01")
    audio, rate = read_wav(item["path"])
    return wav_bytes(audio, rate)


def one_turn(lp: LauncherProcess, wav: Path) -> dict[str, Any]:
    """A whole turn; returns the transcript or the error the core sent."""
    with lp.ws_connect() as ws:
        client = WSClient(ws)
        assert client.recv().msg["type"] == "hello"
        client.send({"type": "session.start", "scenario_id": "free_talk"})
        got = client.until(lambda m: m["type"] in ("tutor.done", "error"), timeout=90)
        last = got[-1].msg
        if last["type"] == "error":
            return last
        client.send({"type": "playback.ended", "turn_id": last["turn_id"]})
        client.until(lambda m: m["type"] == "state" and m["value"] == "idle", timeout=10)
        client.send_turn(wav)
        got = client.until(lambda m: m["type"] in ("user.transcript", "error"), timeout=120)
        return got[-1].msg


def test_core_survives_video_memory_pressure(core: dict[str, Any]) -> None:
    import torch

    lp: LauncherProcess = core["lp"]
    body = reading_body()
    turn = ensure_turns()["turn_basic"]
    url = "/api/pron/assess?phrase_id=p01"
    hog = fill_video_memory()
    try:
        free_mb = torch.cuda.mem_get_info()[0] // 2**20
        assert free_mb < 1024, f"could not fill video memory: {free_mb} MB free"
        with lp.http() as http:
            http.timeout = 120
            r = http.post(url, content=body, headers={"Content-Type": "audio/wav"})
            if r.status_code != 200:
                assert r.status_code == 503, r.text
                assert r.json()["error"]["code"] in {"vram_low", "pron_unavailable"}
                assert r.json()["error"]["message_l1"]
        result = one_turn(lp, turn)
        if result["type"] == "error":
            assert result["code"] in {"vram_low", "stt_failed", "tts_failed"}, result
        else:
            assert result["text"].strip()
        with lp.http() as http:
            assert http.get("/api/health").status_code == 200
        assert lp.proc.poll() is None, "the core process died"
        print(f"under pressure ({free_mb} MB free): assess {r.status_code}, turn {result}")
    finally:
        del hog
        torch.cuda.empty_cache()

    # Memory is back: everything works again.
    with lp.http() as http:
        http.timeout = 120
        r = http.post(url, content=body, headers={"Content-Type": "audio/wav"})
        assert r.status_code == 200, r.text
    result = one_turn(lp, turn)
    assert result["type"] == "user.transcript" and result["text"].strip(), result
