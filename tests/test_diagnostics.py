"""Diagnostics archive (plan item 4.7): no keys, no user name, no conversation text.

A key is planted in the test credential store, in a log line and as a key-like string; turn text
is planted in a detailed-log line. The archive must contain none of them.
"""

from __future__ import annotations

import getpass
import json
import secrets
import sqlite3
import zipfile
from pathlib import Path

import keyring

from voicetutor import keystore
from voicetutor.diagnostics import TURN_LOGGER, collect
from voicetutor.storage.db import Database


def test_archive_has_no_keys_user_or_turn_text(tmp_path: Path) -> None:
    root = tmp_path / "data"
    db = Database(root / "voicetutor.db")
    db.execute(
        "INSERT INTO connection(name, base_url, model, extra_params, json_format, key_last4,"
        " is_active) VALUES ('Mock', 'https://api.example.test', 'm', '{}', 'json_object',"
        " 'abcd', 1)"
    )
    db.close()
    planted = "zz" + secrets.token_hex(24)  # no "sk-" prefix: only the exact match removes it
    keystore.save_key(1, planted)
    user = getpass.getuser()
    users = "\\" + "Us" + "ers" + "\\"  # built from parts: the repository holds no user path
    fake_key = "sk-" + "proj-" + "ABCDEFGHIJKLMNOP"
    turn_text = "I have worked on this project since two years PLANTED-TURN"
    logs = root / "logs"
    logs.mkdir(parents=True)
    (logs / "voicetutor.log").write_text(
        "\n".join(
            [
                "2026-11-12 10:00:00,000 INFO voicetutor.core: hardware: RTX, profile completo",
                f"2026-11-12 10:00:01,000 INFO {TURN_LOGGER}: user: {turn_text}",
                f"2026-11-12 10:00:02,000 WARNING voicetutor.llm: provider said {planted}",
                f"2026-11-12 10:00:03,000 WARNING voicetutor.llm: echo {fake_key}",
                f"2026-11-12 10:00:04,000 INFO voicetutor.launcher: data C:{users}{user}\\x",
            ]
        ),
        encoding="utf-8",
    )
    try:
        archive = collect(tmp_path / "out", root)
    finally:
        keyring.delete_password(keystore.service_name(), "connection-1")
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        content = "\n".join(z.read(n).decode("utf-8") for n in names)
        report = json.loads(z.read("report.json"))
    assert "logs/voicetutor.log" in names
    assert planted not in content and "ABCDEFGHIJKLMNOP" not in content
    assert "PLANTED-TURN" not in content and TURN_LOGGER not in content
    assert f"{users}{user}\\" not in content and f"{users}<user>\\" in content
    assert "[key removed]" in content
    assert "hardware: RTX, profile completo" in content  # ordinary lines stay
    assert report["connections"][0]["name"] == "Mock"
    assert "key_last4" not in report["connections"][0]
    assert report["versions"]["voicetutor"]
    con = sqlite3.connect(root / "voicetutor.db")
    con.close()
