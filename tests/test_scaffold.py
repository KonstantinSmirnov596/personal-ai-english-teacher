"""Smoke checks of the project skeleton."""

from __future__ import annotations

import os
from pathlib import Path

import voicetutor
from voicetutor import paths


def test_package_imports() -> None:
    assert voicetutor.__version__


def test_predecessor_package_name_is_gone() -> None:
    import importlib.util

    assert importlib.util.find_spec("trainer") is None
    assert paths.APP_DIR_NAME == "VoiceTutor"


def test_data_dir_honours_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VOICETUTOR_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.delenv("VOICETUTOR_MODELS_DIR", raising=False)
    assert paths.data_dir() == tmp_path / "data"
    assert paths.models_dir() == tmp_path / "data" / "models"


def test_models_dir_override(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VOICETUTOR_MODELS_DIR", str(tmp_path / "m"))
    assert paths.models_dir() == tmp_path / "m"


def test_default_data_dir_is_localappdata(monkeypatch) -> None:
    monkeypatch.delenv("VOICETUTOR_DATA_DIR", raising=False)
    local = os.environ.get("LOCALAPPDATA")
    if local:
        assert paths.data_dir() == Path(local) / "VoiceTutor"
