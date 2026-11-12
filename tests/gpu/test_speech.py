"""Speech services behind the single GPU queue (plan item 1.5)."""

from __future__ import annotations

import asyncio

import numpy as np
import pytest

from tests.profile_opt import stt_compute_type
from voicetutor.core import GpuQueue
from voicetutor.lang_guard import LearnerLanguageError
from voicetutor.speech.audio import STT_RATE, TTS_RATE, resample
from voicetutor.speech.stt import SpeechRecognizer
from voicetutor.speech.tts import SpeechSynthesizer
from voicetutor.wer import wer

pytestmark = pytest.mark.gpu


@pytest.fixture(scope="module")
def models() -> tuple[SpeechRecognizer, SpeechSynthesizer]:
    stt = SpeechRecognizer(compute_type=stt_compute_type())
    tts = SpeechSynthesizer()
    stt.load()
    tts.load()
    return stt, tts


def test_queue_runs_jobs_sequentially(models) -> None:
    stt, tts = models
    queue = GpuQueue()

    async def scenario() -> list[str]:
        texts = ["The meeting starts at nine.", "Could you share your screen, please?"]
        syn = await asyncio.gather(*(queue.run(tts.synthesize, t) for t in texts))
        heard = await asyncio.gather(
            *(queue.run(stt.transcribe, resample(s.audio, TTS_RATE, STT_RATE)) for s in syn)
        )
        return [h.text for h in heard]

    heard = asyncio.run(scenario())
    queue.shutdown()
    assert (
        wer(["The meeting starts at nine.", "Could you share your screen, please?"], heard) <= 0.1
    )


def test_input_resampled_from_48k(models) -> None:
    stt, tts = models
    syn = tts.synthesize("I usually work from home on Fridays.")
    audio48 = resample(syn.audio, TTS_RATE, 48_000)
    tr = stt.transcribe(resample(audio48, 48_000, STT_RATE))
    assert wer(["I usually work from home on Fridays."], [tr.text]) <= 0.1


def test_synthesis_rejects_learner_language(models) -> None:
    """SPEC 5: Spanish and Portuguese text is shown, never spoken."""
    _stt, tts = models
    for text in (
        "Para una duración se usa for.",
        "Você pode repetir, por favor?",
        "Hello, \u043c\u0438\u0440.",  # another script
    ):
        with pytest.raises(LearnerLanguageError):
            tts.synthesize(text)
    assert tts.synthesize("We met in São Paulo last May.").audio.size > 0


def test_silence_gives_empty_transcript(models) -> None:
    stt, _tts = models
    tr = stt.transcribe(np.zeros(STT_RATE * 3, dtype=np.float32))
    assert tr.text == ""
