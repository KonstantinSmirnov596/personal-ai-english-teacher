"""Hardware test doubles, injected into the core by dependency injection in tests only."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from voicetutor.hardware import GpuInfo, HardwareInfo
from voicetutor.speech.stt import Transcript
from voicetutor.speech.tts import Synthesis


def machine(
    *,
    gpu: GpuInfo | None = None,
    ram_mb: int = 16_000,
    disk_mb: int = 50_000,
    battery: bool | None = False,
    build: int = 22631,
) -> HardwareInfo:
    return HardwareInfo(
        gpu=gpu,
        ram_total_mb=ram_mb,
        ram_available_mb=ram_mb // 2,
        disk_free_mb=disk_mb,
        on_battery=battery,
        cpu_cores=8,
        windows_build=build,
    )


def card(
    total: int = 8192, free: int = 7600, driver: str = "610.47", cc: tuple[int, int] = (8, 6)
) -> GpuInfo:
    return GpuInfo("NVIDIA GeForce RTX 3060 Laptop GPU", total, free, driver, cc)


@dataclass
class FakeDetector:
    info: HardwareInfo
    calls: int = 0

    def detect(self, data_dir: Path) -> HardwareInfo:
        self.calls += 1
        return self.info


@dataclass
class FakeSTT:
    """Speech recognizer double: raises out-of-memory a given number of times."""

    oom_times: int = 0
    compute_type: str = "float16"
    loaded: bool = True
    calls: list[int] = field(default_factory=list)

    def transcribe(self, audio: np.ndarray) -> Transcript:
        self.calls.append(len(audio))
        if self.oom_times > 0:
            self.oom_times -= 1
            raise RuntimeError("CUDA failed with error out of memory")
        return Transcript(text="hello", words=[], duration_s=1.0, elapsed_ms=1.0)

    def load(self) -> None:
        self.loaded = True

    def unload(self) -> None:
        self.loaded = False


@dataclass
class FakePhonemeModel:
    loaded: bool = True

    def unload(self) -> None:
        self.loaded = False


@dataclass
class FakeTTS:
    """Speech synthesizer double: a short silence per sentence."""

    loaded: bool = True
    spoken: list[str] = field(default_factory=list)

    def synthesize(self, text: str, voice: str = "af_heart", speed: float = 1.0) -> Synthesis:
        self.spoken.append(text)
        return Synthesis(audio=np.zeros(2400, dtype=np.float32), sample_rate=24000, elapsed_ms=1.0)

    def load(self) -> None:
        self.loaded = True

    def unload(self) -> None:
        self.loaded = False
