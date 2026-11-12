"""Diagnostics archive for bug reports (plan item 4.7; ``scripts/collect_diagnostics.ps1``).

Collects versions, the GPU and hardware profile, settings without device ids, the API
connections without keys, and the logs. Before anything is written:

- every saved API key (read from the Windows Credential Manager) and anything that looks like a
  key or a bearer token is replaced by ``[key removed]``;
- the Windows user name in paths becomes ``<user>``;
- lines of the detailed turn log (logger ``voicetutor.turns``, written only when the user turned
  on "Detailed log") are dropped, so no conversation text leaves.

Nothing is sent anywhere: the user attaches the archive to an issue if they want.
"""

from __future__ import annotations

import argparse
import contextlib
import getpass
import importlib.metadata as md
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from voicetutor import __version__, keystore
from voicetutor.paths import data_dir

TURN_LOGGER = "voicetutor.turns"
KEY_LIKE = re.compile(
    r"(?i)\b(?:sk|pk|rk|or|key)-[A-Za-z0-9_\-]{8,}|bearer\s+[A-Za-z0-9._\-]{8,}|\b[A-Za-z0-9_\-]{40,}\b"
)
PACKAGES = (
    "torch",
    "ctranslate2",
    "faster-whisper",
    "kokoro",
    "transformers",
    "fastapi",
    "uvicorn",
    "httpx",
    "keyring",
)
SETTINGS_SKIP = {"input_device_id", "output_device_id"}


def saved_keys(db: Path) -> list[str]:
    keys: list[str] = []
    for cid in connection_ids(db):
        with contextlib.suppress(Exception):
            key = keystore.load_key(cid)
            if key:
                keys.append(key)
    return keys


def connection_ids(db: Path) -> list[int]:
    if not db.exists():
        return []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return [int(r[0]) for r in con.execute("SELECT id FROM connection")]
    except sqlite3.Error:
        return []
    finally:
        con.close()


class Scrubber:
    def __init__(self, keys: list[str]) -> None:
        self.keys = sorted({k for k in keys if len(k) >= 4}, key=len, reverse=True)
        user = ""
        with contextlib.suppress(Exception):
            user = getpass.getuser()
        self.user = user
        home = str(Path.home())
        self.paths = [p for p in {home, home.replace("\\", "/")} if user and user in p]

    def text(self, value: str) -> str:
        for key in self.keys:
            value = value.replace(key, "[key removed]")
        value = KEY_LIKE.sub("[key removed]", value)
        for p in self.paths:
            value = value.replace(p, p.replace(self.user, "<user>"))
        if self.user:
            value = re.sub(rf"(?i)(\\Users\\|/Users/){re.escape(self.user)}", r"\1<user>", value)
        return value

    def log(self, content: str) -> str:
        lines = [line for line in content.splitlines() if f" {TURN_LOGGER}:" not in line]
        return self.text("\n".join(lines) + ("\n" if lines else ""))


def versions() -> dict[str, Any]:
    out: dict[str, Any] = {
        "voicetutor": __version__,
        "python": sys.version.split()[0],
        "windows": platform.version(),
        "machine": platform.machine(),
    }
    for name in PACKAGES:
        with contextlib.suppress(md.PackageNotFoundError):
            out[name] = md.version(name)
    return out


def gpu() -> str:
    try:
        return subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,compute_cap,memory.total,memory.free",
                "--format=csv",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as e:
        return f"nvidia-smi not available: {type(e).__name__}"


def database_facts(db: Path) -> dict[str, Any]:
    if not db.exists():
        return {"database": "missing"}
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    facts: dict[str, Any] = {}
    try:
        with contextlib.suppress(sqlite3.Error):
            facts["settings"] = {
                r["key"]: r["value"]
                for r in con.execute("SELECT key, value FROM setting")
                if r["key"] not in SETTINGS_SKIP
            }
        with contextlib.suppress(sqlite3.Error):
            facts["hardware_profile"] = [
                dict(r)
                for r in con.execute(
                    "SELECT created_at, gpu_name, driver, vram_total_mb, vram_free_mb,"
                    " compute_capability, ram_total_mb, profile, measurements"
                    " FROM hardware_profile ORDER BY created_at DESC LIMIT 5"
                )
            ]
        with contextlib.suppress(sqlite3.Error):
            facts["connections"] = [
                dict(r)
                for r in con.execute(
                    "SELECT id, name, base_url, model, json_format, is_active FROM connection"
                )
            ]
        with contextlib.suppress(sqlite3.Error):
            facts["counts"] = {
                t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("session", "turn", "correction", "vocab")
            }
    finally:
        con.close()
    return facts


def collect(out_dir: Path, root: Path | None = None) -> Path:
    root = root or data_dir()
    db = root / "voicetutor.db"
    scrub = Scrubber(saved_keys(db))
    report = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "versions": versions(),
        "gpu": gpu(),
        **database_facts(db),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = out_dir / f"VoiceTutor-diagnostics-{stamp}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("report.json", scrub.text(json.dumps(report, indent=2, default=str)))
        logs = root / "logs"
        if logs.is_dir():
            for f in sorted(logs.glob("voicetutor.log*")):
                content = f.read_text(encoding="utf-8", errors="replace")
                z.writestr(f"logs/{f.name}", scrub.log(content))
    return archive


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out", type=Path, default=Path(os.environ.get("USERPROFILE", ".")) / "Desktop"
    )
    args = ap.parse_args()
    out = args.out if args.out.is_dir() else Path.cwd()
    archive = collect(out)
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
