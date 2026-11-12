"""First-run benchmark (wizard step 4, SPEC 7): about a minute on the user's GPU.

Recognition of a ten-second phrase, synthesis of a first sentence and the pronunciation check of
a short phrase, with the video memory left after all models are loaded. The result confirms the
profile or lowers it to ``compacto``. Nothing is sent anywhere; the result is stored in the
``hardware_profile`` table.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from voicetutor import profiles
from voicetutor.speech.audio import STT_RATE, resample
from voicetutor.storage.repo import now_iso

log = logging.getLogger(__name__)

PHRASE = (
    "Thanks for joining the call today. I wanted to walk you through the new release plan, "
    "and then we can talk about the timeline."
)
FIRST_SENTENCE = "Thanks for joining the call today."
READING = "I think we should start the third project this week."


async def run(core: Any) -> dict[str, Any]:
    """Measure, decide the profile, store the row. Raises if the models cannot run at all."""
    timings: dict[str, float] = {}

    started = time.perf_counter()
    first = await core.gpu.run(core.tts.synthesize, FIRST_SENTENCE)
    timings["tts_first_ms"] = round((time.perf_counter() - started) * 1000, 1)
    speech = await core.gpu.run(core.tts.synthesize, PHRASE)
    audio16 = resample(speech.audio, speech.sample_rate, STT_RATE)
    await core.transcribe(audio16[:STT_RATE])  # warm-up
    started = time.perf_counter()
    transcript = await core.transcribe(audio16)
    timings["stt_ms"] = round((time.perf_counter() - started) * 1000, 1)
    timings["stt_audio_s"] = round(len(audio16) / STT_RATE, 2)

    reading = await core.gpu.run(core.tts.synthesize, READING)
    reading16 = resample(reading.audio, reading.sample_rate, STT_RATE)
    try:
        await core.pron.ensure_loaded()  # compacto loads it on demand; time the check alone
        started = time.perf_counter()
        await core.pron.assess(READING, reading16, source="benchmark")
        timings["pron_ms"] = round((time.perf_counter() - started) * 1000, 1)
    except Exception as e:  # the phoneme model may not fit: compacto loads it on demand anyway
        log.warning("benchmark: pronunciation check failed: %s", type(e).__name__)
        timings["pron_ms"] = -1.0
    del first

    # Without an LLM, the app's own share of "end of turn -> first audio" is recognition plus
    # the first synthesized sentence (the mock-LLM target with 0 ms delay is 0.9 s).
    first_audio_ms = timings["stt_ms"] + timings["tts_first_ms"]
    info = await core.detect_now()
    gpu = info.gpu
    free_after = gpu.vram_free_mb if gpu else 0
    # Free memory is measured while this app's own models are loaded: count them as available,
    # the SPEC thresholds are about what the desktop and other programs leave.
    own_mb = core.models_vram_mb(free_after if gpu else None)
    assessment = profiles.assess(info, measured=True, extra_free_mb=own_mb)
    measured_profile = assessment.profile
    if measured_profile == "unsupported" and [c.id for c in assessment.reasons] == ["vram"]:
        # The hardware is supported; other programs hold the video memory right now.
        measured_profile = "compacto"
    profile = (
        profiles.after_benchmark(measured_profile, first_audio_ms, free_after)
        if measured_profile != "unsupported"
        else "unsupported"
    )
    measurements = {
        **timings,
        "first_audio_ms": round(first_audio_ms, 1),
        "vram_free_after_load_mb": free_after,
        "vram_used_mb": own_mb,
        "vram_total_mb": gpu.vram_total_mb if gpu else 0,
        "stt_compute_type": core.stt.compute_type,
        "transcript_ok": "release plan" in transcript.text.lower(),
    }
    core.db.execute(
        "INSERT INTO hardware_profile(created_at, gpu_name, driver, vram_total_mb, vram_free_mb,"
        " compute_capability, ram_total_mb, profile, measurements)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            now_iso(),
            gpu.name if gpu else "",
            gpu.driver if gpu else "",
            gpu.vram_total_mb if gpu else 0,
            free_after,
            ".".join(map(str, gpu.compute_capability)) if gpu else "",
            info.ram_total_mb,
            profile,
            json.dumps(measurements),
        ),
    )
    return {
        "profile": profile,
        "measured_profile": measured_profile,
        "measurements": measurements,
        "assessment": assessment.to_api(),
    }
