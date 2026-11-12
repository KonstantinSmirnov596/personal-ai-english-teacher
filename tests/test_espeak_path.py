"""espeak-ng from an app folder with accented letters (plan item 4.1, voicetutor/espeak_path.py).

The espeak-ng data is copied to a temporary folder with accents; a child process points
``espeakng_loader`` there, as if the app were installed in such a folder, and phonemizes a word.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CHILD = r"""
import sys
import espeakng_loader
espeakng_loader.get_data_path = lambda: sys.argv[1]
from voicetutor import espeak_path
espeak_path.configure()
from phonemizer.backend import EspeakBackend
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())  # what misaki does
print("PHONES", EspeakBackend("en-us").phonemize(["think"])[0].strip())
"""


@pytest.mark.skipif(sys.platform != "win32", reason="Windows short names")
def test_accented_data_path_works(tmp_path: Path) -> None:
    import espeakng_loader

    from voicetutor.espeak_path import short_path

    folder = tmp_path / "José Núñez" / "espeak-ng-data"
    shutil.copytree(espeakng_loader.get_data_path(), folder)
    if not short_path(str(folder)).isascii():
        pytest.skip("this volume keeps no 8.3 short names")
    r = subprocess.run(
        [sys.executable, "-c", CHILD, str(folder)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert "PHONES θɪŋk" in r.stdout, r.stdout + r.stderr


def test_ascii_path_is_left_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    import espeakng_loader

    from voicetutor import espeak_path

    monkeypatch.setattr(espeak_path, "_done", False)
    monkeypatch.delenv("ESPEAK_DATA_PATH", raising=False)
    original = espeakng_loader.get_data_path
    espeak_path.configure()
    assert espeakng_loader.get_data_path is original
    assert "ESPEAK_DATA_PATH" not in os.environ
