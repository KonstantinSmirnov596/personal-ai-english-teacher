"""Logs contain no conversation text by default (plan item 4.3).

A whole turn runs through the WebSocket: fake speech models (dependency injection) and the mock
LLM. With the default settings no log record carries the learner's or the tutor's words; with
Settings -> Data -> "Detailed log" on, they appear only under the ``voicetutor.turns`` logger.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from tests.helpers import TEST_PORT, make_app
from tests.hw_fakes import FakeDetector, FakeSTT, FakeTTS, card, machine
from tests.mock_llm import MockLLM
from voicetutor.speech.stt import Transcript

LEARNER = "my secret project codename is bluefinch"


class SayingSTT(FakeSTT):
    def transcribe(self, audio: np.ndarray) -> Transcript:
        self.calls.append(len(audio))
        return Transcript(text=LEARNER, words=[], duration_s=1.0, elapsed_ms=1.0)


def until(ws: Any, kind: str, timeout: float = 20.0) -> list[dict[str, Any]]:
    got: list[dict[str, Any]] = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        msg = ws.receive()
        if "text" not in msg or msg["text"] is None:
            continue
        import json

        data = json.loads(msg["text"])
        got.append(data)
        if data["type"] == kind:
            return got
    raise AssertionError(f"no {kind}: {[m['type'] for m in got]}")


def one_turn(ctx: Any) -> str:
    """Session start, one learner turn, the tutor's reply; returns the reply text."""
    with ctx.client.websocket_connect(
        f"ws://127.0.0.1:{TEST_PORT}/ws", headers=ctx.auth_headers
    ) as ws:
        until(ws, "hello")
        ws.send_json({"type": "session.start", "scenario_id": "free_talk"})
        first = until(ws, "tutor.done")[-1]
        ws.send_json({"type": "playback.ended", "turn_id": first["turn_id"]})
        pcm = (np.zeros(16000, dtype=np.int16)).tobytes()
        ws.send_json({"type": "turn.begin", "turn_id": "t1", "mode": "manual"})
        ws.send_json(
            {
                "type": "turn.audio",
                "turn_id": "t1",
                "audio": {"sample_rate": 16000, "format": "pcm_s16le", "bytes": len(pcm)},
            }
        )
        ws.send_bytes(pcm)
        got = until(ws, "tutor.done")
        assert any(m["type"] == "user.transcript" and m["text"] == LEARNER for m in got)
        return str(got[-1]["text"])


@pytest.mark.parametrize("verbose", [False, True])
def test_turn_text_reaches_the_log_only_with_detailed_log(
    tmp_path: Path,
    mock_llm: MockLLM,
    test_key: str,
    caplog: pytest.LogCaptureFixture,
    verbose: bool,
) -> None:
    caplog.set_level(logging.DEBUG)
    with make_app(
        tmp_path, detector=FakeDetector(machine(gpu=card())), stt=SayingSTT(), tts=FakeTTS()
    ) as ctx:
        models = ctx.core.models
        models.stt = models.tts = "ready"
        models.warm = True
        ctx.core.models_ready.set()
        h = ctx.auth_headers
        ctx.client.post(
            "/api/connections",
            json={"name": "Mock", "base_url": mock_llm.base_url, "model": "m", "api_key": test_key},
            headers=h,
        ).raise_for_status()
        ctx.client.patch(
            "/api/settings", json={"verbose_log": verbose, "correction_mode": "off"}, headers=h
        ).raise_for_status()
        reply = one_turn(ctx)
    assert reply
    records = [(r.name, r.getMessage()) for r in caplog.records]
    with_text = [(name, msg) for name, msg in records if "bluefinch" in msg or reply[:30] in msg]
    if verbose:
        assert with_text and all(name == "voicetutor.turns" for name, _ in with_text)
        assert any("bluefinch" in msg for _, msg in with_text)
    else:
        assert not with_text, with_text
    assert not any(test_key in msg for _, msg in records)
