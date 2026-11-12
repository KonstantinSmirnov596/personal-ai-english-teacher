"""Pronunciation on synthesized speech, per learner language (stage 2 acceptance): false
alarms, catalog mistakes (substitutions, deletions, insertions), assessment time, sensitivity
feedback, cautious marks in conversation."""

from __future__ import annotations

import contextlib
import json
import secrets
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import keyring
import keyring.errors
import pytest

from tests.fixtures.make_fixtures import ensure_reading, ensure_turns
from tests.launcher_proc import LauncherProcess
from tests.mock_llm import MockLLM
from tests.ws_client import WSClient
from voicetutor.speech.audio import read_wav, wav_bytes

pytestmark = pytest.mark.gpu


_EVALUATIONS: dict[str, dict[str, Any]] = {}


def evaluation_for(lang: str) -> dict[str, Any]:
    """scripts/pron_eval.py once per learner language (shared by the tests of this module)."""
    if lang not in _EVALUATIONS:
        import sys

        repo = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(repo / "scripts"))
        import pron_eval

        result = pron_eval.evaluate(lang)
        out = repo / "docs" / "reports" / "data" / f"pron_stage2_{lang}.json"
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        _EVALUATIONS[lang] = result
    return _EVALUATIONS[lang]


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_false_alarms_on_native_reading(lang: str) -> None:
    """Three American voices read all 30 phrases: at most 3 % of phones get "error"."""
    fa = evaluation_for(lang)["false_alarms"]
    assert fa["phones"] > 2000
    assert fa["error_rate"] <= 0.03, [o for o in fa["offenders"] if o["level"] == "error"]


@pytest.mark.parametrize("lang", ["es-419", "pt-BR"])
def test_catalog_mistakes_are_flagged_and_named(lang: str) -> None:
    """SPEC 12: a catalog substitution or insertion gets "error" in >= 80 % of cases over all
    verifiable entries together, and the heard sound is named in >= 60 %."""
    m = evaluation_for(lang)["mistakes"]
    every = m["error_level_entries"]
    assert every["cases"] >= 100
    assert every["error"] >= 0.80, m["by_entry"]
    assert every["diagnosis"] >= 0.60, m["by_entry"]
    assert not m["skipped"], m["skipped"]


def test_accented_phrase_marks_the_right_words() -> None:
    from voicetutor.gpu_env import prepare_cuda_dlls

    prepare_cuda_dlls()
    from voicetutor.data_files import reading_phrases
    from voicetutor.pron.assess import build_result
    from voicetutor.pron.engine import PronEngine
    from voicetutor.pron.phoneme_model import PhonemeModel
    from voicetutor.pron.reference import build_reference
    from voicetutor.speech.audio import STT_RATE, resample

    text = next(p["text"] for p in reading_phrases()["phrases"] if p["id"] == "p01")
    audio, rate = read_wav(ensure_turns()["reading_p01_accent"])
    source = text.split()
    ref = build_reference(source, lang="es-419")
    result = build_result(
        ref, PronEngine(PhonemeModel()).analyze(resample(audio, rate, STT_RATE), ref), source
    )
    words = {w["w"]: w for w in result["words"]}
    assert words["third"]["level"] == "error"
    assert words["third"]["tip"]["heard"] == "t" and words["third"]["tip"]["expected"] == "θ"
    # an inserted vowel before the s-cluster is named as an extra sound (plan item 2.2)
    assert words["start"]["level"] == "error"
    assert words["start"]["tip"]["catalog_id"] == "s_cluster_epenthesis"
    assert words["start"]["tip"]["heard"] in {"+ɛ", "+ə"}
    wrong = [w["w"] for w in result["words"] if w["level"] == "error"]
    assert set(wrong) == {"third", "start"}, wrong


@pytest.fixture(scope="module")
def env(tmp_path_factory: pytest.TempPathFactory) -> Iterator[dict[str, Any]]:
    key = "sk-test-" + secrets.token_urlsafe(24)
    mock = MockLLM(key).start()
    lp = LauncherProcess(tmp_path_factory.mktemp("core"))
    try:
        lp.login()
        with lp.http() as http:
            http.post(
                "/api/connections",
                json={"name": "Mock", "base_url": mock.base_url, "model": "m", "api_key": key},
            )
            deadline = time.monotonic() + 180
            while http.get("/api/health").json()["status"] != "ok":
                assert time.monotonic() < deadline
                time.sleep(0.5)
        yield {"lp": lp, "mock": mock}
    finally:
        lp.stop()
        mock.stop()
        for i in range(1, 4):
            with contextlib.suppress(keyring.errors.PasswordDeleteError):
                keyring.delete_password("VoiceTutor-test", f"connection-{i}")


def wav_of(path: Path, trim_tail_s: float = 0.0) -> bytes:
    audio, rate = read_wav(path)
    if trim_tail_s:
        audio = audio[: len(audio) - int(trim_tail_s * rate)]
    return wav_bytes(audio, rate)


def test_assessment_time_for_a_five_second_phrase(env: dict[str, Any]) -> None:
    """A 5 s phrase is assessed within 1 s after the recording ends (warm model)."""
    lp: LauncherProcess = env["lp"]
    import numpy as np

    item = next(
        i for i in ensure_reading() if i["phrase"]["id"] == "p06" and i["voice"] == "am_michael"
    )
    speech, rate = read_wav(item["path"])
    # a real recording has a short pause before and after the phrase: 5 s in total
    lead = np.zeros(int(0.3 * rate), dtype=np.float32)
    tail = np.zeros(max(0, int(5.0 * rate) - len(speech) - len(lead)), dtype=np.float32)
    body = wav_bytes(np.concatenate([lead, speech, tail]), rate)
    url = f"/api/pron/assess?phrase_id={item['phrase']['id']}"
    with lp.http() as http:
        first = http.post(url, content=body, headers={"Content-Type": "audio/wav"})
        assert first.status_code == 200, first.text  # loads the phoneme model
        times = []
        for _ in range(3):
            started = time.perf_counter()
            r = http.post(url, content=body, headers={"Content-Type": "audio/wav"})
            times.append(time.perf_counter() - started)
            assert r.status_code == 200
        result = r.json()
        health = http.get("/api/health").json()
    assert max(times) <= 1.0, times
    assert result["attempt_id"] and 0.9 <= result["score"] <= 1.0
    assert all(w["level"] != "error" for w in result["words"])
    assert 4.9 <= result["duration_s"] <= 5.2
    assert health["models"]["phoneme"] == "ready"
    report = Path(__file__).resolve().parents[2] / "docs" / "reports" / "data"
    report.mkdir(parents=True, exist_ok=True)
    (report / "pron_timing.json").write_text(
        json.dumps(
            {
                "phrase_s": result["duration_s"],
                "http_roundtrip_s": [round(t, 3) for t in times],
                "analysis_ms": result["analysis_ms"],
                "vram_used_mb_all_models": health["gpu"]["vram_used_mb"],
                "vram_total_mb": health["gpu"]["vram_total_mb"],
            }
        ),
        encoding="utf-8",
    )


def test_feedback_lowers_sensitivity(env: dict[str, Any]) -> None:
    lp: LauncherProcess = env["lp"]
    body = wav_of(ensure_turns()["reading_p01_accent"], trim_tail_s=4.5)
    with lp.http() as http:
        r = http.post(
            "/api/pron/assess?phrase_id=p01", content=body, headers={"Content-Type": "audio/wav"}
        )
        assert r.status_code == 200, r.text
        res = r.json()
        wi = next(i for i, w in enumerate(res["words"]) if w["w"] == "third")
        word = res["words"][wi]
        assert word["level"] == "error" and word["tip"]["catalog_id"] == "th_voiceless"
        sounds = {s["phone"]: s for s in http.get("/api/pron/sounds?days=7").json()}
        assert sounds["θ"]["errors"] >= 1 and sounds["θ"]["example"] == "third"

        fb = http.post(
            "/api/pron/feedback",
            json={
                "attempt_id": res["attempt_id"],
                "word_index": wi,
                "phone_index": word["tip"]["phone_index"],
                "verdict": "was_correct",
            },
        ).json()
        assert fb["phone"] == "θ" and fb["sensitivity_offset"] >= 1.0
        assert fb["attempt"]["words"][wi]["level"] == "ok"
        gop = -word["phones"][word["tip"]["phone_index"]]["gop"]
        offset = fb["sensitivity_offset"]
        for _ in range(8):  # press "That was right" until this recording is accepted
            if offset + 2.0 > gop:
                break
            again = http.post(
                "/api/pron/assess?phrase_id=p01",
                content=body,
                headers={"Content-Type": "audio/wav"},
            ).json()
            w2 = again["words"][wi]
            if w2["level"] != "error":
                break
            offset = http.post(
                "/api/pron/feedback",
                json={
                    "attempt_id": again["attempt_id"],
                    "word_index": wi,
                    "phone_index": w2["tip"]["phone_index"],
                    "verdict": "was_correct",
                },
            ).json()["sensitivity_offset"]
        final = http.post(
            "/api/pron/assess?phrase_id=p01", content=body, headers={"Content-Type": "audio/wav"}
        ).json()
        assert final["words"][wi]["level"] != "error"
        start = next(w for w in final["words"] if w["w"] == "start")
        assert start["level"] == "error"  # other sounds keep their sensitivity


def test_silence_is_rejected(env: dict[str, Any]) -> None:
    lp: LauncherProcess = env["lp"]
    with lp.http() as http:
        r = http.post(
            "/api/pron/assess?phrase_id=p01",
            content=ensure_turns()["silence_5s"].read_bytes(),
            headers={"Content-Type": "audio/wav"},
        )
    assert r.status_code == 422 and r.json()["error"]["code"] == "pron_no_speech"


def test_reference_audio(env: dict[str, Any]) -> None:
    lp: LauncherProcess = env["lp"]
    with lp.http() as http:
        r = http.get("/api/pron/reference?phrase_id=p01&speed=0.8")
        assert r.status_code == 200 and r.headers["content-type"] == "audio/wav"
        assert len(r.content) > 100_000
        assert http.get("/api/pron/reference?text=think").status_code == 200


def test_conversation_marks_only_clear_errors(env: dict[str, Any]) -> None:
    """Free conversation: "video" said with /b/ (Spanish speakers) is flagged; nothing else is."""
    lp: LauncherProcess = env["lp"]
    with lp.ws_connect() as ws:
        client = WSClient(ws)
        client.recv()
        client.send({"type": "session.start", "scenario_id": "free_talk"})
        got = client.until(lambda m: m["type"] == "tutor.done", timeout=60)
        client.send({"type": "playback.ended", "turn_id": got[-1].msg["turn_id"]})
        turn_id, _ = client.send_turn(ensure_turns()["turn_accent"])
        got = client.until(lambda m: m["type"] == "pron.flags", timeout=60)
        types = [r.msg["type"] for r in got]
        assert types.index("tutor.sentence") < types.index("pron.flags")  # never delays audio
        transcript = next(r.msg for r in got if r.msg["type"] == "user.transcript")
        flags = got[-1].msg
        assert flags["turn_id"] == turn_id
        assert len(flags["items"]) == 1
        item = flags["items"][0]
        assert transcript["words"][item["word_index"]]["w"].strip(".,").lower() == "video"
        assert item["expected"] == "v" and item["heard"] == "b" and item["tip_l1"]
        client.until(lambda m: m["type"] == "tutor.done", timeout=60) if not any(
            r.msg["type"] == "tutor.done" for r in got
        ) else None
        client.send({"type": "session.end"})
        summary = client.until(lambda m: m["type"] == "summary", timeout=60)[-1].msg
    assert summary["sounds"] == [{"phone": "v", "count": 1, "words": ["video"]}]

    # a clean turn produces no marks at all
    with lp.ws_connect() as ws:
        client = WSClient(ws)
        client.recv()
        client.send({"type": "session.start", "scenario_id": "free_talk"})
        got = client.until(lambda m: m["type"] == "tutor.done", timeout=60)
        client.send({"type": "playback.ended", "turn_id": got[-1].msg["turn_id"]})
        client.send_turn(ensure_turns()["turn_basic"])
        client.until(lambda m: m["type"] == "tutor.done", timeout=60)
        rest = client.collect(3.0)
        assert not [r for r in client.log + rest if r.msg["type"] == "pron.flags"]
