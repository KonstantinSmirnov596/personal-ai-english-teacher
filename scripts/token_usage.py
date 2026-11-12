"""Tokens per turn for the cost estimate in docs/<lang>/api-keys.md (plan item 4.4).

A session runs in this process with the mock LLM and fake speech models (no GPU): the opener,
10 learner turns of ordinary length with corrections on, one hint and the summary. Every request
body the mock receives is measured. Tokens are estimated with DeepSeek's documented ratio of
about 0.3 tokens per English character (https://api-docs.deepseek.com/quick_start/token_usage);
other providers count differently, so the numbers are a guide, not a bill. Output tokens are
bounded by each request's ``max_tokens``; the mock's own answers say nothing about real lengths.

    .venv\\Scripts\\python.exe scripts\\token_usage.py
"""

from __future__ import annotations

import contextlib
import json
import os
import queue
import secrets
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

TOKENS_PER_CHAR = 0.3
KIND_BY_MAX_TOKENS = {
    400: "tutor",
    800: "corrector",
    1200: "summary",
    600: "helper",
    300: "history",
}
LEARNER = [
    "I have been working as a backend developer for about four years now.",
    "Most of my work is with Python and PostgreSQL, and sometimes with Go.",
    "Last year we migrated our payment service to a new cloud provider.",
    "The hardest part was moving the data without stopping the service.",
    "We did it in small steps and tested every step with real traffic.",
    "I like working in a small team because everybody can see the whole system.",
    "In my free time I am learning English and playing football with friends.",
    "I want to improve my speaking because meetings in English are difficult for me.",
    "Sometimes I understand everything but I need too much time to answer.",
    "I think practicing every day for twenty minutes will help me a lot.",
]


def main() -> int:
    os.environ["VOICETUTOR_DATA_DIR"] = tempfile.mkdtemp(prefix="vt-tokens-")
    os.environ["VOICETUTOR_KEYRING_SERVICE"] = f"VoiceTutor-test-{os.getpid()}"
    import keyring
    import numpy as np

    from tests.helpers import TEST_PORT, make_app
    from tests.hw_fakes import FakeDetector, FakeSTT, FakeTTS, card, machine
    from tests.mock_llm import MockLLM
    from voicetutor.speech.stt import Transcript

    lines = iter(LEARNER)

    class ScriptedSTT(FakeSTT):
        def transcribe(self, audio: np.ndarray) -> Transcript:
            return Transcript(text=next(lines), words=[], duration_s=4.0, elapsed_ms=1.0)

    key = "sk-test-" + secrets.token_urlsafe(24)
    mock = MockLLM(key).start()
    data = Path(os.environ["VOICETUTOR_DATA_DIR"])
    try:
        with make_app(
            data, detector=FakeDetector(machine(gpu=card())), stt=ScriptedSTT(), tts=FakeTTS()
        ) as ctx:
            m = ctx.core.models
            m.stt = m.tts = "ready"
            m.warm = True
            ctx.core.models_ready.set()
            h = ctx.auth_headers
            ctx.client.post(
                "/api/connections",
                json={"name": "Mock", "base_url": mock.base_url, "model": "m", "api_key": key},
                headers=h,
            ).raise_for_status()
            ctx.client.patch(
                "/api/settings", json={"correction_mode": "instant", "level": "B1"}, headers=h
            ).raise_for_status()
            with ctx.client.websocket_connect(f"ws://127.0.0.1:{TEST_PORT}/ws", headers=h) as ws:
                inbox: queue.Queue[dict[str, Any]] = queue.Queue()

                def reader() -> None:
                    with contextlib.suppress(Exception):
                        while True:
                            msg = ws.receive()
                            if msg.get("text"):
                                inbox.put(json.loads(msg["text"]))

                threading.Thread(target=reader, daemon=True).start()

                def wait_for(*kinds: str) -> dict[str, dict[str, Any]]:
                    """Every kind once, in any order (corrections may come before tutor.done)."""
                    got: dict[str, dict[str, Any]] = {}
                    while set(kinds) - set(got):
                        data = inbox.get(timeout=30)
                        got.setdefault(data["type"], data)
                    return got

                wait_for("hello")
                ws.send_json({"type": "session.start", "scenario_id": "interview_backend"})
                done = wait_for("tutor.done")["tutor.done"]
                pcm = np.zeros(16000, dtype=np.int16).tobytes()
                for i in range(len(LEARNER)):
                    ws.send_json({"type": "playback.ended", "turn_id": done["turn_id"]})
                    time.sleep(0.05)
                    tid = f"t{i}"
                    ws.send_json({"type": "turn.begin", "turn_id": tid, "mode": "manual"})
                    ws.send_json(
                        {
                            "type": "turn.audio",
                            "turn_id": tid,
                            "audio": {
                                "sample_rate": 16000,
                                "format": "pcm_s16le",
                                "bytes": len(pcm),
                            },
                        }
                    )
                    ws.send_bytes(pcm)
                    done = wait_for("tutor.done", "corrections")["tutor.done"]
                ws.send_json({"type": "playback.ended", "turn_id": done["turn_id"]})
                time.sleep(0.05)
                ws.send_json({"type": "helper.hint", "request_id": "h1"})
                wait_for("helper.result")
                ws.send_json({"type": "session.end"})
                wait_for("summary")
        rows = []
        for r in mock.requests:
            body = r["body"]
            chars = sum(len(str(msg.get("content", ""))) for msg in body.get("messages", []))
            if "response_format" in body:
                chars += len(json.dumps(body["response_format"]))
            kind = KIND_BY_MAX_TOKENS.get(int(body.get("max_tokens") or 0), "other")
            rows.append({"kind": kind, "input_chars": chars, "max_tokens": body.get("max_tokens")})
    finally:
        mock.stop()
        for i in range(1, 3):
            with contextlib.suppress(keyring.errors.PasswordDeleteError):
                keyring.delete_password(os.environ["VOICETUTOR_KEYRING_SERVICE"], f"connection-{i}")

    def tokens(chars: int) -> int:
        return round(chars * TOKENS_PER_CHAR)

    tutor = [r for r in rows if r["kind"] == "tutor"]
    corrector = [r for r in rows if r["kind"] == "corrector"]
    result = {
        "date": time.strftime("%Y-%m-%d"),
        "tokens_per_char": TOKENS_PER_CHAR,
        "requests": {k: sum(1 for r in rows if r["kind"] == k) for k in {r["kind"] for r in rows}},
        "tutor_input_tokens": [tokens(r["input_chars"]) for r in tutor],
        "corrector_input_tokens": [tokens(r["input_chars"]) for r in corrector],
        "summary_input_tokens": [tokens(r["input_chars"]) for r in rows if r["kind"] == "summary"],
        "helper_input_tokens": [tokens(r["input_chars"]) for r in rows if r["kind"] == "helper"],
        "max_output_tokens": {r["kind"]: r["max_tokens"] for r in rows},
        "session_input_tokens": tokens(sum(r["input_chars"] for r in rows)),
    }
    out = REPO / "docs" / "reports" / "data" / "token_usage.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
