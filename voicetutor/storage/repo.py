"""Repositories over the SQLite schema. All methods are synchronous and fast (local SQLite)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from voicetutor.settings import Settings, SettingsPatch
from voicetutor.storage.db import Database


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------------------------
# Settings


class SettingsRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self) -> Settings:
        stored = {r["key"]: json.loads(r["value"]) for r in self.db.all("SELECT * FROM setting")}
        known = {k: v for k, v in stored.items() if k in Settings.model_fields}
        try:
            return Settings(**known)
        except ValueError:
            return Settings()

    def patch(self, patch: SettingsPatch) -> Settings:
        changes = patch.model_dump(exclude_none=True)
        merged = Settings(**{**self.get().model_dump(), **changes})
        with self.db.transaction() as conn:
            for key in changes:
                conn.execute(
                    "INSERT INTO setting(key, value) VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (key, json.dumps(getattr(merged, key))),
                )
        return merged


# ---------------------------------------------------------------------------------------------
# Connections


class ConnectionRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    @staticmethod
    def to_api(row: Any) -> dict[str, Any]:
        last_test = None
        if row["last_test_at"]:
            last_test = {
                "ok": bool(row["last_test_ok"]),
                "latency_ms": row["last_test_latency_ms"],
                "message_l1": row["last_test_message"] or "",
                "at": row["last_test_at"],
            }
        return {
            "id": row["id"],
            "name": row["name"],
            "base_url": row["base_url"],
            "model": row["model"],
            "extra_params": json.loads(row["extra_params"] or "{}"),
            "json_format": row["json_format"],
            "key_last4": row["key_last4"],
            "is_active": bool(row["is_active"]),
            "last_test": last_test,
        }

    def list(self) -> list[Any]:
        return self.db.all("SELECT * FROM connection ORDER BY id")

    def get(self, conn_id: int) -> Any | None:
        return self.db.one("SELECT * FROM connection WHERE id = ?", (conn_id,))

    def active(self) -> Any | None:
        return self.db.one("SELECT * FROM connection WHERE is_active = 1")

    def create(
        self,
        *,
        name: str,
        base_url: str,
        model: str,
        extra_params: dict[str, Any],
        json_format: str,
        key_last4: str,
    ) -> int:
        with self.db.transaction() as conn:
            has_active = conn.execute("SELECT 1 FROM connection WHERE is_active = 1").fetchone()
            cur = conn.execute(
                "INSERT INTO connection(name, base_url, model, extra_params, json_format,"
                " key_last4, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    name,
                    base_url,
                    model,
                    json.dumps(extra_params),
                    json_format,
                    key_last4,
                    0 if has_active else 1,
                ),
            )
            return int(cur.lastrowid or 0)

    def update(self, conn_id: int, fields: dict[str, Any]) -> None:
        allowed = {"name", "base_url", "model", "extra_params", "json_format", "key_last4"}
        sets: list[str] = []
        values: list[Any] = []
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "extra_params":
                value = json.dumps(value)
            sets.append(f"{key} = ?")
            values.append(value)
        if sets:
            values.append(conn_id)
            self.db.execute(f"UPDATE connection SET {', '.join(sets)} WHERE id = ?", values)

    def delete(self, conn_id: int) -> None:
        self.db.execute("DELETE FROM connection WHERE id = ?", (conn_id,))

    def activate(self, conn_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute("UPDATE connection SET is_active = 0 WHERE is_active = 1")
            conn.execute("UPDATE connection SET is_active = 1 WHERE id = ?", (conn_id,))

    def record_test(self, conn_id: int, ok: bool, latency_ms: int | None, message: str) -> None:
        self.db.execute(
            "UPDATE connection SET last_test_ok = ?, last_test_latency_ms = ?,"
            " last_test_message = ?, last_test_at = ? WHERE id = ?",
            (int(ok), latency_ms, message, now_iso(), conn_id),
        )


# ---------------------------------------------------------------------------------------------
# Scenarios


class ScenarioRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    @staticmethod
    def to_api(row: Any, lang: str = "") -> dict[str, Any]:
        """Scenario for the window; built-in titles in ``lang`` (custom ones as written)."""
        titles = json.loads(row["title_l10n"] or "{}")
        descriptions = json.loads(row["description_l10n"] or "{}")
        return {
            "id": row["id"],
            "builtin": bool(row["builtin"]),
            "title_l1": titles.get(lang) or row["title_l1"] or row["title_en"],
            "title_en": row["title_en"],
            "description_l1": descriptions.get(lang) or row["description_l1"],
            "role": row["role"],
            "setting": row["setting"],
            "goals": json.loads(row["goals"]),
            "openers": json.loads(row["openers"]),
        }

    def seed_builtin(self, scenarios: list[dict[str, Any]]) -> None:
        """Insert or refresh the built-in scenarios; drop built-ins that no longer exist."""
        with self.db.transaction() as conn:
            for order, s in enumerate(scenarios):
                conn.execute(
                    "INSERT INTO scenario(id, builtin, title_l1, title_en, description_l1, role,"
                    " setting, goals, openers, sort_order, title_l10n, description_l10n)"
                    " VALUES (?, 1, '', ?, '', ?, ?, ?, ?, ?, ?, ?)"
                    " ON CONFLICT(id) DO UPDATE SET builtin = 1, title_l1 = '',"
                    " title_en = excluded.title_en, description_l1 = '',"
                    " role = excluded.role, setting = excluded.setting, goals = excluded.goals,"
                    " openers = excluded.openers, sort_order = excluded.sort_order,"
                    " title_l10n = excluded.title_l10n,"
                    " description_l10n = excluded.description_l10n",
                    (
                        s["id"],
                        s.get("title_en", ""),
                        s["role"],
                        s.get("setting", ""),
                        json.dumps(s.get("goals", [])),
                        json.dumps(s.get("openers", [])),
                        order,
                        json.dumps(s.get("title", {}), ensure_ascii=False),
                        json.dumps(s.get("description", {}), ensure_ascii=False),
                    ),
                )
            ids = [s["id"] for s in scenarios]
            marks = ", ".join("?" for _ in ids)
            conn.execute(f"DELETE FROM scenario WHERE builtin = 1 AND id NOT IN ({marks})", ids)

    def list(self) -> list[Any]:
        return self.db.all("SELECT * FROM scenario ORDER BY sort_order, created_at")

    def get(self, scenario_id: str) -> Any | None:
        return self.db.one("SELECT * FROM scenario WHERE id = ?", (scenario_id,))

    def create(self, data: dict[str, Any]) -> str:
        sid = "custom_" + uuid.uuid4().hex[:10]
        self.db.execute(
            "INSERT INTO scenario(id, builtin, title_l1, title_en, description_l1, role, setting,"
            " goals, openers) VALUES (?, 0, ?, ?, ?, ?, ?, ?, ?)",
            (
                sid,
                data["title_l1"],
                data.get("title_en", ""),
                data.get("description_l1", ""),
                data["role"],
                data.get("setting", ""),
                json.dumps(data.get("goals", [])),
                json.dumps(data.get("openers", [])),
            ),
        )
        return sid

    def update(self, scenario_id: str, data: dict[str, Any]) -> None:
        cols = ("title_l1", "title_en", "description_l1", "role", "setting", "goals", "openers")
        sets: list[str] = []
        values: list[Any] = []
        for c in cols:
            if c in data and data[c] is not None:
                v = data[c]
                sets.append(f"{c} = ?")
                values.append(json.dumps(v) if c in ("goals", "openers") else v)
        if sets:
            values.append(scenario_id)
            self.db.execute(f"UPDATE scenario SET {', '.join(sets)} WHERE id = ?", values)

    def delete(self, scenario_id: str) -> None:
        self.db.execute("DELETE FROM scenario WHERE id = ? AND builtin = 0", (scenario_id,))


# ---------------------------------------------------------------------------------------------
# Sessions, turns, corrections


class SessionRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(
        self,
        *,
        scenario_id: str,
        scenario_title_l1: str,
        level: str,
        correction_mode: str,
        connection_id: int | None,
        connection_name: str,
        model: str,
        l1: str = "",
    ) -> str:
        sid = new_id()
        self.db.execute(
            "INSERT INTO session(id, scenario_id, scenario_title_l1, level, correction_mode,"
            " connection_id, connection_name, model, started_at, l1)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                sid,
                scenario_id,
                scenario_title_l1,
                level,
                correction_mode,
                connection_id,
                connection_name,
                model,
                now_iso(),
                l1,
            ),
        )
        return sid

    def get(self, session_id: str) -> Any | None:
        return self.db.one("SELECT * FROM session WHERE id = ?", (session_id,))

    def list(self) -> list[Any]:
        return self.db.all(
            "SELECT s.*, (SELECT COUNT(*) FROM turn t"
            " WHERE t.session_id = s.id AND t.role = 'user') AS user_turns,"
            " (SELECT COUNT(*) FROM correction c WHERE c.session_id = s.id) AS corrections"
            " FROM session s ORDER BY s.started_at DESC"
        )

    def end(self, session_id: str, summary: dict[str, Any] | None) -> None:
        self.db.execute(
            "UPDATE session SET ended_at = ?, summary = ? WHERE id = ?",
            (now_iso(), json.dumps(summary, ensure_ascii=False) if summary else None, session_id),
        )

    def set_history_summary(self, session_id: str, text: str) -> None:
        self.db.execute("UPDATE session SET history_summary = ? WHERE id = ?", (text, session_id))

    def delete(self, session_id: str) -> list[str]:
        paths = [
            r["audio_path"]
            for r in self.db.all(
                "SELECT audio_path FROM turn WHERE session_id = ? AND audio_path IS NOT NULL",
                (session_id,),
            )
        ]
        self.db.execute("DELETE FROM session WHERE id = ?", (session_id,))
        return paths

    # turns -----------------------------------------------------------------------------------

    def add_turn(
        self,
        *,
        session_id: str,
        role: str,
        text: str,
        turn_id: str | None = None,
        words: list[dict[str, Any]] | None = None,
        audio_path: str | None = None,
    ) -> str:
        tid = turn_id or new_id()
        with self.db.transaction() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(idx), -1) + 1 FROM turn WHERE session_id = ?", (session_id,)
            ).fetchone()
            conn.execute(
                "INSERT INTO turn(id, session_id, idx, role, text, words, audio_path, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    tid,
                    session_id,
                    int(row[0]),
                    role,
                    text,
                    json.dumps(words) if words is not None else None,
                    audio_path,
                    now_iso(),
                ),
            )
        return tid

    def update_turn(self, turn_id: str, **fields: Any) -> None:
        allowed = {"text", "timing", "interrupted", "corrections_status", "better", "audio_path"}
        sets: list[str] = []
        values: list[Any] = []
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "timing":
                value = json.dumps(value)
            if key == "interrupted":
                value = int(bool(value))
            sets.append(f"{key} = ?")
            values.append(value)
        if sets:
            values.append(turn_id)
            self.db.execute(f"UPDATE turn SET {', '.join(sets)} WHERE id = ?", values)

    def turns(self, session_id: str) -> list[Any]:
        return self.db.all("SELECT * FROM turn WHERE session_id = ? ORDER BY idx", (session_id,))

    def get_turn(self, turn_id: str) -> Any | None:
        return self.db.one("SELECT * FROM turn WHERE id = ?", (turn_id,))

    def add_corrections(self, session_id: str, turn_id: str, items: list[dict[str, Any]]) -> None:
        with self.db.transaction() as conn:
            for it in items:
                conn.execute(
                    "INSERT INTO correction(id, turn_id, session_id, quote, fix, type, note_l1,"
                    ' pattern, start, "end", created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        it["id"],
                        turn_id,
                        session_id,
                        it["quote"],
                        it["fix"],
                        it["type"],
                        it["note_l1"],
                        it["pattern"],
                        it["start"],
                        it["end"],
                        now_iso(),
                    ),
                )

    def corrections(self, session_id: str) -> list[Any]:
        return self.db.all(
            "SELECT c.* FROM correction c JOIN turn t ON t.id = c.turn_id"
            " WHERE c.session_id = ? ORDER BY t.idx, c.created_at",
            (session_id,),
        )

    def expired_audio(self, older_than_iso: str) -> list[Any]:
        return self.db.all(
            "SELECT id, audio_path FROM turn WHERE audio_path IS NOT NULL AND created_at < ?",
            (older_than_iso,),
        )

    def clear_audio_path(self, turn_id: str) -> None:
        self.db.execute("UPDATE turn SET audio_path = NULL WHERE id = ?", (turn_id,))
