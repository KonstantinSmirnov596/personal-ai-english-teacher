"""Hardware requirements and model profiles (SPEC 7).

Requirements and their sources are in ``docs/reports/stage0.md`` ("Hardware facts"):

- NVIDIA GPU of compute capability 7.5 (Turing) or newer: the torch ``cu128`` wheel and
  CTranslate2 4.9.0 carry native code from sm_75 on;
- NVIDIA driver 572.61 or newer: CUDA 12.8 Update 1, which CTranslate2 4.9.0 is built with;
- free video memory: ``completo`` from 7 GB, ``compacto`` from 5 GB, below that unsupported.

Profiles decide how the models use video memory:

=========== ============================== ==========================================
profile     speech recognition             phoneme model
=========== ============================== ==========================================
completo    turbo, float16                 float16, kept in memory once loaded
compacto    turbo, int8_float16            float16, loaded on demand, unloaded after
                                           5 minutes idle; conversation marks off by
                                           default
=========== ============================== ==========================================

Two moments decide a profile. The first-run wizard measures free video memory (and runs a
short benchmark) and follows the SPEC thresholds. Before the wizard ran, the core estimates a
profile from the total video memory, so a game left open at start-up does not lock the app;
the wizard then explains a shortage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from voicetutor.hardware import HardwareInfo

Profile = Literal["completo", "compacto", "unsupported"]

MIN_DRIVER = (572, 61)
MIN_COMPUTE_CAPABILITY = (7, 5)
COMPLETO_FREE_MB = 7 * 1024
COMPACTO_FREE_MB = 5 * 1024
# Estimate before any measurement: an 8 GB card reports about 8150 MiB.
COMPLETO_TOTAL_MB = 7_600
COMPACTO_TOTAL_MB = 5_800
MIN_RAM_MB = 15_000  # 16 GB installed shows about 15.7 GB to Windows
MIN_DISK_FREE_MB = 2_048  # runtime: audio, logs and database growth
MIN_WINDOWS_BUILD = 19045  # Windows 10 22H2

STT_COMPUTE_TYPE = {"completo": "float16", "compacto": "int8_float16"}
PHONEME_IDLE_UNLOAD_S = {"completo": None, "compacto": 300.0}
PRON_IN_CONVERSATION_DEFAULT = {"completo": True, "compacto": False}

# Where the user docs explain each requirement (docs/<lang>/hardware.md).
DOC = "hardware.md"


@dataclass(frozen=True)
class Check:
    id: str  # gpu, driver, architecture, vram, ram, disk, power, windows
    ok: bool
    value: str
    required: str
    blocking: bool  # False: a warning, the app still runs
    # Numbers behind value/required, so the window formats them in the learner's language.
    params: dict[str, Any] = field(default_factory=dict)

    def to_api(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ok": self.ok,
            "value": self.value,
            "required": self.required,
            "blocking": self.blocking,
            "params": dict(self.params),
            "doc": f"{DOC}#{self.id}",
        }


@dataclass(frozen=True)
class Assessment:
    profile: Profile
    checks: list[Check] = field(default_factory=list)
    measured: bool = False  # True: free video memory decided the profile (wizard)

    @property
    def reasons(self) -> list[Check]:
        return [c for c in self.checks if not c.ok and c.blocking]

    @property
    def warnings(self) -> list[Check]:
        return [c for c in self.checks if not c.ok and not c.blocking]

    def to_api(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "measured": self.measured,
            "checks": [c.to_api() for c in self.checks],
            "reasons": [c.id for c in self.reasons],
            "warnings": [c.id for c in self.warnings],
        }


def _gb(mb: int) -> str:
    return f"{mb / 1024:.1f} GB"


def assess(info: HardwareInfo, *, measured: bool, extra_free_mb: int = 0) -> Assessment:
    """Profile and per-item checks. ``measured`` follows the SPEC free-memory thresholds;
    otherwise the profile is estimated from the total video memory. ``extra_free_mb`` is video
    memory held by this app's own models, which is available to it."""
    checks: list[Check] = []
    gpu = info.gpu
    checks.append(
        Check(
            "gpu",
            gpu is not None,
            gpu.name if gpu else "none",
            "NVIDIA GPU",
            blocking=True,
            params={"name": gpu.name if gpu else None},
        )
    )
    if gpu is not None:
        checks.append(
            Check(
                "driver",
                gpu.driver_tuple >= MIN_DRIVER,
                gpu.driver,
                ".".join(map(str, MIN_DRIVER)),
                blocking=True,
                params={"version": gpu.driver, "min": ".".join(map(str, MIN_DRIVER))},
            )
        )
        cc = gpu.compute_capability
        checks.append(
            Check(
                "architecture",
                cc >= MIN_COMPUTE_CAPABILITY,
                f"{cc[0]}.{cc[1]}",
                "7.5 (Turing)",
                blocking=True,
                params={"cc": f"{cc[0]}.{cc[1]}", "min": "7.5"},
            )
        )
        free_mb = min(gpu.vram_total_mb, gpu.vram_free_mb + max(0, extra_free_mb))
        if measured:
            vram_ok = free_mb >= COMPACTO_FREE_MB
            checks.append(
                Check(
                    "vram",
                    vram_ok,
                    f"{_gb(free_mb)} free of {_gb(gpu.vram_total_mb)}",
                    f"{_gb(COMPACTO_FREE_MB)} free",
                    blocking=True,
                    params={
                        "free_mb": free_mb,
                        "total_mb": gpu.vram_total_mb,
                        "min_free_mb": COMPACTO_FREE_MB,
                    },
                )
            )
        else:
            checks.append(
                Check(
                    "vram",
                    gpu.vram_total_mb >= COMPACTO_TOTAL_MB,
                    _gb(gpu.vram_total_mb),
                    "6 GB",
                    blocking=True,
                    params={"total_mb": gpu.vram_total_mb, "min_total_mb": 6 * 1024},
                )
            )
    checks.append(
        Check(
            "ram",
            info.ram_total_mb >= MIN_RAM_MB,
            _gb(info.ram_total_mb),
            "16 GB",
            blocking=False,
            params={"total_mb": info.ram_total_mb, "min_mb": 16 * 1024},
        )
    )
    checks.append(
        Check(
            "disk",
            info.disk_free_mb >= MIN_DISK_FREE_MB,
            f"{_gb(info.disk_free_mb)} free",
            f"{_gb(MIN_DISK_FREE_MB)} free",
            blocking=False,
            params={"free_mb": info.disk_free_mb, "min_free_mb": MIN_DISK_FREE_MB},
        )
    )
    checks.append(
        Check(
            "power",
            info.on_battery is not True,
            "battery" if info.on_battery else "mains",
            "mains",
            blocking=False,
            params={"on_battery": info.on_battery},
        )
    )
    if info.windows_build:
        checks.append(
            Check(
                "windows",
                info.windows_build >= MIN_WINDOWS_BUILD,
                str(info.windows_build),
                f"{MIN_WINDOWS_BUILD} (Windows 10 22H2)",
                blocking=False,
                params={"build": info.windows_build, "min": MIN_WINDOWS_BUILD},
            )
        )
    if any(not c.ok and c.blocking for c in checks) or gpu is None:
        return Assessment("unsupported", checks, measured)
    if measured:
        profile: Profile = "completo" if free_mb >= COMPLETO_FREE_MB else "compacto"
    else:
        profile = "completo" if gpu.vram_total_mb >= COMPLETO_TOTAL_MB else "compacto"
    return Assessment(profile, checks, measured)


def after_benchmark(profile: Profile, first_audio_ms: float, free_after_load_mb: int) -> Profile:
    """SPEC 7 step 4: completo is confirmed only if it is fast enough and leaves room."""
    if profile == "completo" and (first_audio_ms > 1200 or free_after_load_mb < 800):
        return "compacto"
    return profile
