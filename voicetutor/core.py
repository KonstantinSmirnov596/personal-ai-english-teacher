"""Core services shared by HTTP routes and the WebSocket conversation."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Any, TypeVar

from voicetutor import __version__, i18n, keystore, l1, profiles
from voicetutor.data_files import scenarios as builtin_scenarios
from voicetutor.hardware import HardwareDetector, HardwareInfo, SystemDetector
from voicetutor.llm.client import Endpoint, LLMClient, LLMError, Timeouts, is_local_url
from voicetutor.server.guard import AccessKeys
from voicetutor.speech.stt import SpeechRecognizer
from voicetutor.speech.tts import SpeechSynthesizer
from voicetutor.storage.db import Database
from voicetutor.storage.repo import ConnectionRepo, ScenarioRepo, SessionRepo, SettingsRepo

log = logging.getLogger(__name__)
T = TypeVar("T")


class GpuQueue:
    """All GPU model calls run one at a time on a single worker thread."""

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="gpu")

    async def run(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, partial(fn, *args, **kwargs))

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


@dataclass
class ModelStatus:
    stt: str = "not_loaded"  # not_loaded | loading | ready | error
    tts: str = "not_loaded"
    phoneme: str = "not_loaded"
    error: str = ""
    problem: str = ""  # no_gpu | models_missing | model_load_failed
    load_ms: dict[str, float] = field(default_factory=dict)
    warm: bool = False  # the first calls after loading are done (slow: kernels, caches)

    @property
    def loaded(self) -> bool:
        return self.stt == "ready" and self.tts == "ready"

    @property
    def ready(self) -> bool:
        # Ready only after the warm-up: a request queued behind it on the GPU thread would wait.
        return self.loaded and self.warm


class NoActiveConnection(Exception):
    pass


class VramLowError(Exception):
    """A model ran out of video memory even after the phoneme model was freed."""


def is_out_of_memory(exc: BaseException) -> bool:
    """CUDA out-of-memory from torch or CTranslate2 (faster-whisper)."""
    name = type(exc).__name__
    text = str(exc).lower()
    return (
        name == "OutOfMemoryError" or "out of memory" in text or "cuda_error_out_of_memory" in text
    )


class Core:
    def __init__(
        self,
        *,
        data_dir: Path,
        keys: AccessKeys,
        load_models: bool = True,
        llm_timeouts: Timeouts | None = None,
        detector: HardwareDetector | None = None,
        stt: SpeechRecognizer | None = None,
        tts: SpeechSynthesizer | None = None,
    ) -> None:
        """``detector``, ``stt`` and ``tts`` are injected by tests; the app uses the real ones."""
        self.data_dir = data_dir
        self.keys = keys
        self.app_version = __version__
        data_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir = data_dir / "audio"
        self.db = Database(data_dir / "voicetutor.db")
        self.settings = SettingsRepo(self.db)
        self.connections = ConnectionRepo(self.db)
        self.scenarios = ScenarioRepo(self.db)
        self.sessions = SessionRepo(self.db)
        self.llm = LLMClient(llm_timeouts)
        self.gpu = GpuQueue()
        self.detector: HardwareDetector = detector or SystemDetector()
        self.stt = stt or SpeechRecognizer()
        self.tts = tts or SpeechSynthesizer()
        self.hardware: HardwareInfo | None = None
        self.assessment: profiles.Assessment | None = None
        self.profile: str = "completo"
        self.hardware_notices: list[str] = []
        self.dismissed_notices: set[str] = set()  # once per run (SPEC 7)
        self.vram_free_before_load: int | None = None
        self.vram_free_after_load: int | None = None
        from voicetutor.pron.service import PronService

        self.pron = PronService(self)
        self.models = ModelStatus()
        self.load_models = load_models
        self.models_ready = asyncio.Event()
        self.started_at = time.monotonic()
        # WebSocket presence, used by the launcher to exit after the window is closed.
        self.ws_count = 0
        self.ws_ever_connected = False
        self.ws_last_change = time.monotonic()
        self.current_ws: Any = None
        self._load_task: asyncio.Task[None] | None = None
        self._cleanup_task: asyncio.Task[None] | None = None
        self._idle_task: asyncio.Task[None] | None = None
        i18n.set_current(lambda: self.l1)

    def effective_settings(self) -> dict[str, Any]:
        """Settings as the window should show them: profile-dependent defaults filled in."""
        s = self.settings.get().model_dump()
        if not self.settings.is_set("pron_in_conversation"):
            s["pron_in_conversation"] = profiles.PRON_IN_CONVERSATION_DEFAULT.get(
                self.profile, True
            )
        return s

    @property
    def l1(self) -> str:
        """Current learner language: the saved setting, else the Windows-locale suggestion."""
        return l1.resolve(self.settings.get().l1 or l1.default_code())

    async def startup(self) -> None:
        from voicetutor.maintenance import cleanup_loop

        self.scenarios.seed_builtin(builtin_scenarios())
        self._cleanup_task = asyncio.create_task(cleanup_loop(self))
        self._idle_task = asyncio.create_task(self._idle_loop())
        if self.load_models:
            self._load_task = asyncio.create_task(self._load_models())

    async def shutdown(self) -> None:
        for task in (self._cleanup_task, self._load_task, self._idle_task):
            if task is not None and not task.done():
                task.cancel()
        await self.llm.aclose()
        self.gpu.shutdown()
        self.db.close()

    def _preflight(self) -> str:
        """Runs on the GPU thread before loading: is there a video card, are the models here?"""
        import torch

        from voicetutor.model_registry import STT, TTS, local_path

        if not torch.cuda.is_available():
            return "no_gpu"
        try:
            local_path(STT)
            local_path(TTS)
        except Exception:
            return "models_missing"
        return ""

    async def detect_hardware(self) -> None:
        """Decide the profile before loading anything (SPEC 7); never fails the start-up."""
        try:
            self.hardware = await asyncio.to_thread(self.detector.detect, self.data_dir)
        except Exception:
            log.exception("hardware detection failed")
            return
        stored = self.sessions.db.one(
            "SELECT * FROM hardware_profile ORDER BY created_at DESC LIMIT 1"
        )
        self.assessment = profiles.assess(self.hardware, measured=False)
        chosen = self.settings.get().profile
        gpu = self.hardware.gpu
        if self.assessment.profile == "unsupported":
            self.profile = "unsupported"
        elif chosen in ("completo", "compacto"):
            self.profile = chosen
        elif stored is not None and gpu is not None and stored["gpu_name"] == gpu.name:
            self.profile = stored["profile"] if stored["profile"] != "unsupported" else "compacto"
        else:
            self.profile = self.assessment.profile
        self.hardware_notices = []
        if gpu is not None and not (self.stt.loaded or self.tts.loaded):
            # the baseline for "video memory used by the models"; later checks run with them loaded
            self.vram_free_before_load = gpu.vram_free_mb
        if self.hardware.on_battery:
            self.hardware_notices.append("on_battery")
        if (
            stored is not None
            and gpu is not None
            and (stored["gpu_name"] != gpu.name or stored["driver"] != gpu.driver)
        ):
            self.hardware_notices.append("hardware_changed")
        self.hardware_notices = [
            n for n in self.hardware_notices if n not in self.dismissed_notices
        ]
        if self.profile in profiles.STT_COMPUTE_TYPE:
            self.stt.compute_type = profiles.STT_COMPUTE_TYPE[self.profile]
        log.info(
            "hardware: %s, profile %s",
            gpu.name if gpu else "no NVIDIA GPU",
            self.profile,
        )

    async def _idle_loop(self) -> None:
        while True:
            await asyncio.sleep(30)
            try:
                await self.pron.unload_when_idle()
            except Exception:
                log.exception("idle unload failed")

    async def detect_now(self) -> HardwareInfo:
        info = await asyncio.to_thread(self.detector.detect, self.data_dir)
        return info

    def models_vram_mb(self, free_now_mb: int | None = None) -> int:
        """Video memory held by this app's models: free before loading minus free now (or, by
        default, right after loading). The phoneme model loads on demand, so "now" counts it."""
        after = free_now_mb if free_now_mb is not None else self.vram_free_after_load
        if self.vram_free_before_load is None or after is None:
            return 0
        return max(0, self.vram_free_before_load - after)

    def hardware_api(self) -> dict[str, Any]:
        """Profile, start-up assessment and notices for the window (hello, /api/hardware)."""
        return {
            "profile": self.profile,
            "assessment": self.assessment.to_api() if self.assessment else None,
            "notices": list(self.hardware_notices),
        }

    async def apply_profile(self, profile: str) -> None:
        """Switch between completo and compacto at runtime (Settings → Performance)."""
        if profile not in profiles.STT_COMPUTE_TYPE or profile == self.profile:
            return
        self.profile = profile
        self.stt.compute_type = profiles.STT_COMPUTE_TYPE[profile]
        loading = self._load_task is not None and not self._load_task.done()
        if self.stt.loaded or loading:
            # Queued behind a load in progress; load() reloads only if the type changed.
            await self.gpu.run(self.stt.load)
        if profile == "compacto" and self.pron.model.loaded:
            await self.gpu.run(self.pron.model.unload)
            self.models.phoneme = "not_loaded"

    async def transcribe(self, audio_16k: Any) -> Any:
        """Speech recognition that survives a shortage of video memory (SPEC 7).

        On out-of-memory the phoneme model is freed and recognition tried once more; if it
        still fails, VramLowError lets the caller show a clear message. The process lives on.
        """
        try:
            return await self.gpu.run(self.stt.transcribe, audio_16k)
        except Exception as e:
            if not is_out_of_memory(e):
                raise
            log.warning("speech recognition ran out of video memory; freeing the phoneme model")
        await self.pron.free_memory()
        try:
            return await self.gpu.run(self.stt.transcribe, audio_16k)
        except Exception as e:
            if is_out_of_memory(e):
                raise VramLowError from e
            raise

    def reload_models(self) -> bool:
        """Load the models again (after the wizard downloaded them). False: already busy."""
        if self.models.ready or (self._load_task is not None and not self._load_task.done()):
            return False
        self.models = ModelStatus()
        self._load_task = asyncio.create_task(self._load_models())
        return True

    async def _load_models(self) -> None:
        await self.detect_hardware()
        if self.profile == "unsupported":
            self.models.problem = "unsupported_hardware"
            self.models.error = "unsupported_hardware"
            self.models.stt = self.models.tts = "error"
            log.error("models are not loaded: the hardware is below the minimum")
            return
        try:
            problem = await self.gpu.run(self._preflight)
        except Exception:
            log.exception("model preflight failed")
            problem = "model_load_failed"
        if problem:
            log.error("models are not loaded: %s", problem)
            self.models.problem = problem
            self.models.error = problem
            self.models.stt = self.models.tts = "error"
            return
        for name, model in (("stt", self.stt), ("tts", self.tts)):
            setattr(self.models, name, "loading")
            started = time.perf_counter()
            try:
                await self.gpu.run(model.load)
            except Exception as e:  # missing GPU, missing models, broken install
                log.exception("failed to load %s model", name)
                setattr(self.models, name, "error")
                self.models.error = f"{name}: {type(e).__name__}"
                self.models.problem = "model_load_failed"
                continue
            self.models.load_ms[name] = round((time.perf_counter() - started) * 1000)
            setattr(self.models, name, "ready")
            log.info("%s model ready in %.0f ms", name, self.models.load_ms[name])
        if self.models.loaded:
            # Warm-up: the first call after loading is slower (CUDA kernels, caches).
            try:
                await self.gpu.run(self.tts.synthesize, "Hello there.")
                import numpy as np

                await self.gpu.run(self.stt.transcribe, np.zeros(16000, dtype=np.float32))
            except Exception:
                log.exception("model warm-up failed")
            try:
                after = await self.detect_now()
                if after.gpu is not None:
                    self.vram_free_after_load = after.gpu.vram_free_mb
            except Exception:
                log.exception("video memory check after loading failed")
            self.models.warm = True
            self.models_ready.set()

    # --- connections ---------------------------------------------------------------------------

    def active_endpoint(self) -> tuple[Any, Endpoint]:
        row = self.connections.active()
        if row is None:
            raise NoActiveConnection
        key = keystore.load_key(int(row["id"])) or ""
        if not key and not is_local_url(row["base_url"]):
            raise LLMError("llm_unauthorized", "no key saved for the active connection")
        return row, endpoint_from_row(row, key)

    def connection_ref(self, row: Any) -> dict[str, Any]:
        return {"id": int(row["id"]), "name": row["name"], "model": row["model"]}


def endpoint_from_row(row: Any, key: str) -> Endpoint:
    import json

    return Endpoint(
        base_url=row["base_url"],
        model=row["model"],
        api_key=key,
        extra_params=json.loads(row["extra_params"] or "{}"),
        json_format=row["json_format"],
    )
