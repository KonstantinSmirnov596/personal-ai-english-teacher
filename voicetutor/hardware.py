"""What the computer has: NVIDIA GPU, video memory, driver, compute capability, RAM, disk, power.

The core receives a :class:`HardwareDetector`; the app uses :class:`SystemDetector`, tests pass
their own object with fixed answers (dependency injection, no test switches in the app). This
is also the single place that decides which compute device the models use (SPEC 15: AMD, Intel
or CPU support would be added here).
"""

from __future__ import annotations

import ctypes
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

log = logging.getLogger(__name__)

COMPUTE_DEVICE = "cuda"


@dataclass(frozen=True)
class GpuInfo:
    name: str
    vram_total_mb: int
    vram_free_mb: int
    driver: str
    compute_capability: tuple[int, int]

    @property
    def driver_tuple(self) -> tuple[int, ...]:
        try:
            return tuple(int(x) for x in self.driver.split("."))
        except ValueError:
            return (0,)


@dataclass(frozen=True)
class HardwareInfo:
    gpu: GpuInfo | None  # the first NVIDIA GPU, or None
    ram_total_mb: int
    ram_available_mb: int
    disk_free_mb: int  # on the drive of the data directory
    on_battery: bool | None  # None: no battery information (desktop) or unknown
    cpu_cores: int
    windows_build: int
    notes: list[str] = field(default_factory=list)

    def to_api(self) -> dict[str, Any]:
        data = asdict(self)
        if self.gpu is not None:
            data["gpu"]["compute_capability"] = ".".join(map(str, self.gpu.compute_capability))
        return data


class HardwareDetector(Protocol):
    def detect(self, data_dir: Path) -> HardwareInfo: ...


def _nvidia_smi() -> GpuInfo | None:
    """First NVIDIA GPU from ``nvidia-smi`` (installed with the driver)."""
    exe = shutil.which("nvidia-smi")
    if exe is None:
        root = os.environ.get("SYSTEMROOT", r"C:\Windows")
        system32 = Path(root) / "System32" / "nvidia-smi.exe"
        exe = str(system32) if system32.exists() else None
    if exe is None:
        return None
    query = "name,memory.total,memory.free,driver_version,compute_cap"
    try:
        out = subprocess.run(
            [exe, f"--query-gpu={query}", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout
    except (OSError, subprocess.SubprocessError) as e:
        log.warning("nvidia-smi failed: %s", type(e).__name__)
        return None
    for line in out.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 5:
            continue
        try:
            major, _, minor = parts[4].partition(".")
            return GpuInfo(
                name=parts[0],
                vram_total_mb=int(float(parts[1])),
                vram_free_mb=int(float(parts[2])),
                driver=parts[3],
                compute_capability=(int(major), int(minor or 0)),
            )
        except ValueError:
            continue
    return None


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class _PowerStatus(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_ubyte),
        ("BatteryFlag", ctypes.c_ubyte),
        ("BatteryLifePercent", ctypes.c_ubyte),
        ("SystemStatusFlag", ctypes.c_ubyte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]


def _memory_mb() -> tuple[int, int]:
    if sys.platform != "win32":
        return 0, 0
    status = _MemoryStatus()
    status.dwLength = ctypes.sizeof(_MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return 0, 0
    return int(status.ullTotalPhys // 2**20), int(status.ullAvailPhys // 2**20)


def _on_battery() -> bool | None:
    """GetSystemPowerStatus: ACLineStatus 0 = battery, 1 = mains; BatteryFlag 128 = no battery."""
    if sys.platform != "win32":
        return None
    status = _PowerStatus()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return None
    if status.BatteryFlag == 128 or status.ACLineStatus == 255:
        return None
    return status.ACLineStatus == 0


def _windows_build() -> int:
    if sys.platform != "win32":
        return 0
    return int(sys.getwindowsversion().build)


class SystemDetector:
    """The real computer."""

    def detect(self, data_dir: Path) -> HardwareInfo:
        total, available = _memory_mb()
        probe = data_dir if data_dir.exists() else Path(data_dir.anchor or ".")
        try:
            disk_free = int(shutil.disk_usage(probe).free // 2**20)
        except OSError:
            disk_free = 0
        return HardwareInfo(
            gpu=_nvidia_smi(),
            ram_total_mb=total,
            ram_available_mb=available,
            disk_free_mb=disk_free,
            on_battery=_on_battery(),
            cpu_cores=os.cpu_count() or 0,
            windows_build=_windows_build(),
        )
