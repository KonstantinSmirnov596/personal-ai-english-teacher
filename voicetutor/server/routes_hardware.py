"""Hardware, profile and model routes of the first-run wizard (SPEC 7, plan items 3.1–3.5)."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Request

from voicetutor import profiles
from voicetutor.model_registry import ALL_MODELS, local_path
from voicetutor.server.app import ApiError
from voicetutor.server.routes_api import core_of

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
NOTICES = ("on_battery", "hardware_changed")


@router.get("/hardware")
async def get_hardware(request: Request) -> dict[str, Any]:
    """Wizard step 2: what this computer has now and which profile fits."""
    core = core_of(request)
    info = await core.detect_now()
    own = core.models_vram_mb(info.gpu.vram_free_mb if info.gpu else None)
    current = profiles.assess(info, measured=True, extra_free_mb=own)
    stored = core.db.one("SELECT * FROM hardware_profile ORDER BY created_at DESC LIMIT 1")
    return {
        "info": info.to_api(),
        "current": current.to_api(),
        "profile": core.profile,
        "startup": core.assessment.to_api() if core.assessment else None,
        "notices": list(core.hardware_notices),
        "stored": (
            {
                "created_at": stored["created_at"],
                "gpu_name": stored["gpu_name"],
                "driver": stored["driver"],
                "profile": stored["profile"],
                "measurements": json.loads(stored["measurements"]),
            }
            if stored
            else None
        ),
    }


@router.post("/hardware/benchmark")
async def run_benchmark(request: Request) -> dict[str, Any]:
    """Wizard step 4: about a minute of measurements on this GPU; nothing leaves the computer."""
    from voicetutor import benchmark

    core = core_of(request)
    if not core.models.ready:
        raise ApiError(409, "models_loading")
    result = await benchmark.run(core)
    if core.settings.get().profile == "auto" and result["profile"] in profiles.STT_COMPUTE_TYPE:
        await core.apply_profile(result["profile"])
    core.dismissed_notices.add("hardware_changed")
    core.hardware_notices = [n for n in core.hardware_notices if n != "hardware_changed"]
    result["applied_profile"] = core.profile
    return result


@router.post("/hardware/notices/{notice}/dismiss", status_code=204)
async def dismiss_notice(notice: str, request: Request) -> None:
    """Battery and changed-hardware notices are shown once per run."""
    if notice not in NOTICES:
        raise ApiError(404, "not_found")
    core = core_of(request)
    core.dismissed_notices.add(notice)
    core.hardware_notices = [n for n in core.hardware_notices if n != notice]


# --- models (wizard step 3) ---------------------------------------------------------------


def _models_present() -> dict[str, bool]:
    out: dict[str, bool] = {}
    for model in ALL_MODELS:
        try:
            local_path(model)
            out[model.key] = True
        except Exception:
            out[model.key] = False
    return out


@router.get("/models")
async def models_status(request: Request) -> dict[str, Any]:
    present = await asyncio.to_thread(_models_present)
    return {"present": present, "all_present": all(present.values())}


@router.post("/models/load", status_code=202)
async def models_load(request: Request) -> dict[str, Any]:
    """After install.cmd added missing models: load them without restarting the app.

    The app never downloads models itself (CLAUDE.md: models are downloaded only at install
    time); the wizard sends the user to install.cmd, which resumes and verifies downloads.
    """
    present = await asyncio.to_thread(_models_present)
    if not all(present.values()):
        raise ApiError(409, "models_missing")
    started = core_of(request).reload_models()
    return {"state": "loading" if started else "busy"}
