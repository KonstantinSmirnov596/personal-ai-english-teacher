"""Profile acceptance on the development machine (plan item 3.8, SPEC 7).

For each profile (``completo``, ``compacto``) a fresh data directory gets the profile stored as
if the user had chosen it in Settings → Performance, then the real launcher runs a full
scenario with the mock LLM: a conversation of 10 turns (5 with a 0 ms first chunk, 5 with
500 ms) and "Reading" with 5 phrases. ``nvidia-smi`` samples the device memory every 200 ms;
the core's peak is the highest sample minus the memory used before the core started (Windows
WDDM reports no per-process memory, so other programs must stay idle meanwhile).

Afterwards, in this process: speech recognition of a ten-second phrase and the TTS -> STT loop
WER (10 phrases) for each profile's compute type.

    .venv\\Scripts\\python.exe scripts\\bench_profiles.py [--out <json>]

Exit code 1 when an acceptance criterion fails (compacto peak > 5.0 GB, WER delta > 2 pp, a
profile not applied); latency misses are reported but, per docs/PLAN.md, do not fail.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import secrets
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

PROFILES = ("completo", "compacto")
COMPACTO_PEAK_MAX_MB = 5 * 1024
WER_DELTA_MAX = 0.02
FIRST_AUDIO_TARGET_MS = {0: 900, 500: 1500}
TURNS_PER_DELAY = 5
READINGS = ("p01", "p02", "p03", "p04", "p05")


def device_used_mb() -> int:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    ).stdout.strip()
    return int(out.splitlines()[0])


class Sampler:
    def __init__(self, period_s: float = 0.2) -> None:
        self.period_s = period_s
        self.samples: list[int] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self._stop.is_set():
            with contextlib.suppress(Exception):
                self.samples.append(device_used_mb())
            self._stop.wait(self.period_s)

    def __enter__(self) -> Sampler:
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join(timeout=5)


def median(values: list[float]) -> float:
    return round(statistics.median(values), 1)


def run_profile(profile: str, key: str, mock: Any) -> dict[str, Any]:
    import tests.profile_opt as profile_opt
    from tests.fixtures.make_fixtures import ensure_reading, ensure_turns
    from tests.launcher_proc import LauncherProcess
    from tests.ws_client import WSClient
    from voicetutor.speech.audio import read_wav, wav_bytes

    profile_opt.set_profile(profile)
    wav = ensure_turns()["turn_basic"]
    readings = {
        i["phrase"]["id"]: i["path"]
        for i in ensure_reading()
        if i["phrase"]["id"] in READINGS and i["voice"] == "am_michael"
    }
    data = Path(tempfile.mkdtemp(prefix=f"bench-{profile}-"))
    baseline = device_used_mb()
    out: dict[str, Any] = {"baseline_device_used_mb": baseline}
    with Sampler() as sampler:
        lp = LauncherProcess(data)  # seeds the profile into the data directory first
        try:
            lp.login()
            with lp.http() as http:
                http.post(
                    "/api/connections",
                    json={"name": "Mock", "base_url": mock.base_url, "model": "m", "api_key": key},
                ).raise_for_status()
                http.patch("/api/settings", json={"correction_mode": "off"}).raise_for_status()
                deadline = time.monotonic() + 180
                while (status := http.get("/api/health").json()["status"]) != "ok":
                    if status == "error" or time.monotonic() > deadline:
                        raise RuntimeError("models did not load: " + "".join(lp.output[-20:]))
                    time.sleep(0.5)
                hw = http.get("/api/hardware").json()
                settings = http.get("/api/settings").json()
            out["applied_profile"] = hw["profile"]
            out["pron_in_conversation"] = settings["pron_in_conversation"]
            out["ready_device_used_mb"] = device_used_mb() - baseline

            latency: dict[str, list[float]] = {}
            with lp.ws_connect() as ws:
                client = WSClient(ws)
                client.recv()
                client.send({"type": "session.start", "scenario_id": "free_talk"})
                got = client.until(lambda m: m["type"] == "tutor.done", timeout=60)
                client.send({"type": "playback.ended", "turn_id": got[-1].msg["turn_id"]})
                for delay in (0, 500):
                    mock.script(first_delay_ms=delay, chunk_delay_ms=30)
                    values: list[float] = []
                    for _ in range(TURNS_PER_DELAY):
                        _tid, sent = client.send_turn(wav)
                        got = client.until(lambda m: m["type"] == "tutor.sentence", timeout=60)
                        values.append((got[-1].at - sent) * 1000.0)
                        rest = client.until(lambda m: m["type"] == "tutor.done", timeout=60)
                        client.send({"type": "playback.ended", "turn_id": rest[-1].msg["turn_id"]})
                        client.until(
                            lambda m: m["type"] == "state" and m["value"] == "idle", timeout=10
                        )
                    latency[str(delay)] = values
            out["first_audio_client_ms"] = {
                d: {"median": median(v), "max": round(max(v), 1), "runs": [round(x) for x in v]}
                for d, v in latency.items()
            }

            reading_ms: list[float] = []
            with lp.http() as http:
                http.timeout = 120
                for pid in READINGS:
                    audio, rate = read_wav(readings[pid])
                    started = time.perf_counter()
                    r = http.post(
                        f"/api/pron/assess?phrase_id={pid}",
                        content=wav_bytes(audio, rate),
                        headers={"Content-Type": "audio/wav"},
                    )
                    reading_ms.append((time.perf_counter() - started) * 1000.0)
                    r.raise_for_status()
                health = http.get("/api/health").json()
            out["reading_roundtrip_ms"] = [round(x) for x in reading_ms]
            out["phoneme_model_after_readings"] = health["models"]["phoneme"]
        finally:
            lp.stop()
    out["peak_device_used_mb"] = max(sampler.samples)
    out["peak_core_mb"] = max(sampler.samples) - baseline
    out["samples"] = len(sampler.samples)
    return out


def stt_quality(compute_type: str) -> dict[str, Any]:
    from tests.fixtures.make_fixtures import ensure_loop, load_spec
    from voicetutor.speech.audio import STT_RATE, read_wav, resample
    from voicetutor.speech.stt import SpeechRecognizer
    from voicetutor.speech.tts import SpeechSynthesizer
    from voicetutor.wer import wer

    stt = SpeechRecognizer(compute_type=compute_type)
    stt.load()
    refs: list[str] = []
    hyps: list[str] = []
    for path, text in ensure_loop():
        audio, rate = read_wav(path)
        hyps.append(stt.transcribe(resample(audio, rate, STT_RATE)).text)
        refs.append(text)
    spec = load_spec()["bench"]
    tts = SpeechSynthesizer()
    syn = tts.synthesize(spec["phrase_10s"], spec["voice"])
    ten = resample(syn.audio, syn.sample_rate, STT_RATE)
    stt.transcribe(ten)  # warm
    times = []
    for _ in range(5):
        started = time.perf_counter()
        stt.transcribe(ten)
        times.append((time.perf_counter() - started) * 1000.0)
    stt.unload()
    tts.unload()
    return {
        "loop_wer": round(wer(refs, hyps), 4),
        "stt_10s_audio_s": round(len(ten) / STT_RATE, 2),
        "stt_10s_warm_median_ms": median(times),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out", default=str(REPO / "docs" / "reports" / "data" / "bench_profiles.json")
    )
    args = ap.parse_args()

    from voicetutor import paths, profiles

    os.environ.setdefault("VOICETUTOR_MODELS_DIR", str(paths.models_dir()))
    os.environ["VOICETUTOR_KEYRING_SERVICE"] = f"VoiceTutor-test-{os.getpid()}"
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import keyring
    import keyring.errors

    from tests.mock_llm import MockLLM

    key = "sk-test-" + secrets.token_urlsafe(24)
    mock = MockLLM(key).start()
    result: dict[str, Any] = {
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "gpu_total_mb": None,
        "profiles": {},
    }
    try:
        for profile in PROFILES:
            print(f"--- {profile}: full scenario", flush=True)
            result["profiles"][profile] = run_profile(profile, key, mock)
            with contextlib.suppress(keyring.errors.PasswordDeleteError):
                keyring.delete_password(os.environ["VOICETUTOR_KEYRING_SERVICE"], "connection-1")
    finally:
        mock.stop()
    for profile in PROFILES:
        print(f"--- {profile}: recognition quality", flush=True)
        result["profiles"][profile].update(stt_quality(profiles.STT_COMPUTE_TYPE[profile]))

    c, k = result["profiles"]["completo"], result["profiles"]["compacto"]
    checks = {
        "completo_applied": c["applied_profile"] == "completo",
        "compacto_applied": k["applied_profile"] == "compacto",
        "compacto_peak_le_5gb": k["peak_core_mb"] <= COMPACTO_PEAK_MAX_MB,
        "wer_delta_le_2pp": k["loop_wer"] - c["loop_wer"] <= WER_DELTA_MAX,
        "wer_le_10pct": max(c["loop_wer"], k["loop_wer"]) <= 0.10,
    }
    latency = {
        f"{p}_first_audio_{d}ms_le_target": result["profiles"][p]["first_audio_client_ms"][str(d)][
            "median"
        ]
        <= target
        for p in PROFILES
        for d, target in FIRST_AUDIO_TARGET_MS.items()
    }
    result["acceptance"] = checks
    result["latency_targets"] = latency
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for p in PROFILES:
        r = result["profiles"][p]
        fa = r["first_audio_client_ms"]
        print(
            f"{p}: peak {r['peak_core_mb']} MB (ready {r['ready_device_used_mb']} MB),"
            f" first audio median {fa['0']['median']} / {fa['500']['median']} ms,"
            f" STT 10 s {r['stt_10s_warm_median_ms']} ms, loop WER {r['loop_wer']:.3f},"
            f" reading {r['reading_roundtrip_ms']} ms"
        )
    print("acceptance:", checks)
    print("latency targets:", latency)
    print(f"written: {out}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
