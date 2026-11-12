"""Launcher: real process, token exchange, exit after the window is gone."""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from tests.launcher_proc import LauncherProcess


def test_launcher_serves_and_exits_when_window_closes(tmp_path: Path) -> None:
    lp = LauncherProcess(tmp_path, "--no-models", "--exit-when-idle", "2")
    try:
        assert lp.base.startswith("http://127.0.0.1:")
        assert httpx.get(lp.base + "/api/health", timeout=10).status_code == 401
        lp.login()
        with lp.http() as c:
            assert c.get("/api/health").status_code == 200
            assert c.get("/").status_code == 200
        with lp.ws_connect() as ws:
            hello = json.loads(ws.recv(timeout=10))
            assert hello["type"] == "hello"
        started = time.monotonic()
        code = lp.wait_exit(timeout=15)
        assert code == 0, "".join(lp.output)
        assert time.monotonic() - started < 15
        assert (tmp_path / "voicetutor.db").exists()
    finally:
        lp.stop()


def test_launcher_keeps_running_before_first_window(tmp_path: Path) -> None:
    lp = LauncherProcess(tmp_path, "--no-models", "--exit-when-idle", "1")
    try:
        assert lp.wait_exit(timeout=3) is None
    finally:
        lp.stop()


def test_exit_watchdog_ends_a_process_with_a_stuck_thread(tmp_path: Path) -> None:
    """A worker thread that never finishes must not keep a windowless core (and its VRAM) alive.

    The predecessor logged "exiting" after the window closed but the process stayed for hours.
    """
    import subprocess
    import sys

    code = (
        "import threading, time\n"
        "from voicetutor import launcher\n"
        "threading.Thread(target=lambda: time.sleep(3600), daemon=False).start()\n"
        "launcher.exit_watchdog(1.0, code=7)\n"
    )
    started = time.monotonic()
    proc = subprocess.run([sys.executable, "-c", code], timeout=30, check=False)
    assert proc.returncode == 7
    assert time.monotonic() - started < 15
