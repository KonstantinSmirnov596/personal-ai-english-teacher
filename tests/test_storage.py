"""Storage: schema, migrations, repositories (plan item 1.2)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from voicetutor.data_files import scenarios
from voicetutor.settings import Settings, SettingsPatch
from voicetutor.storage.db import MIGRATIONS, Database
from voicetutor.storage.repo import ConnectionRepo, ScenarioRepo, SessionRepo, SettingsRepo

TABLES = {
    "connection",
    "setting",
    "scenario",
    "session",
    "turn",
    "correction",
    "pattern",
    "vocab",
    "pron_attempt",
    "pron_sound",
}


def test_data_dir_and_schema_created(tmp_path: Path) -> None:
    db = Database(tmp_path / "nested" / "voicetutor.db")
    names = {r["name"] for r in db.all("SELECT name FROM sqlite_master WHERE type='table'")}
    assert names >= TABLES
    assert db.schema_version() == len(MIGRATIONS)
    db.close()


def test_migrations_are_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "t.db"
    Database(path).close()
    db = Database(path)
    rows = db.all("SELECT version FROM schema_version")
    assert [r["version"] for r in rows] == list(range(1, len(MIGRATIONS) + 1))
    db.close()


def test_new_migration_applies_on_existing_db(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "t.db"
    Database(path).close()
    monkeypatch.setattr(
        "voicetutor.storage.db.MIGRATIONS", [*MIGRATIONS, "CREATE TABLE extra_t (x INTEGER)"]
    )
    db = Database(path)
    assert db.schema_version() == len(MIGRATIONS) + 1
    assert db.one("SELECT name FROM sqlite_master WHERE name = 'extra_t'") is not None
    db.close()


def test_settings_defaults_and_patch(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    repo = SettingsRepo(db)
    assert repo.get() == Settings()
    assert repo.get().correction_mode == "on_click"
    assert repo.get().audio_retention_days == 30
    assert repo.get().voice == "af_heart"
    s = repo.patch(SettingsPatch(level="C1", pause_ms=2000))
    assert s.level == "C1"
    assert repo.get().pause_ms == 2000
    db.close()


def test_connections_single_active(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    repo = ConnectionRepo(db)
    a = repo.create(
        name="A",
        base_url="https://a",
        model="m",
        extra_params={},
        json_format="json_object",
        key_last4="1234",
    )
    b = repo.create(
        name="B",
        base_url="https://b",
        model="m",
        extra_params={},
        json_format="json_object",
        key_last4="5678",
    )
    assert repo.active()["id"] == a
    repo.activate(b)
    assert repo.active()["id"] == b
    assert sum(1 for r in repo.list() if r["is_active"]) == 1
    db.close()


def test_sessions_turns_corrections_cascade(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    ScenarioRepo(db).seed_builtin(scenarios())
    sessions = SessionRepo(db)
    sid = sessions.create(
        scenario_id="free_talk",
        scenario_title_l1="Conversación libre",
        level="B1",
        correction_mode="on_click",
        connection_id=None,
        connection_name="",
        model="",
    )
    t1 = sessions.add_turn(session_id=sid, role="tutor", text="Hi!")
    t2 = sessions.add_turn(session_id=sid, role="user", text="I has a cat", words=[{"w": "I"}])
    sessions.add_corrections(
        sid,
        t2,
        [
            {
                "id": "c1",
                "quote": "I has",
                "fix": "I have",
                "type": "grammar",
                "note_l1": "Con I va have.",
                "pattern": "third_person_s",
                "start": 0,
                "end": 5,
            }
        ],
    )
    turns = sessions.turns(sid)
    assert [t["idx"] for t in turns] == [0, 1]
    assert turns[0]["id"] == t1
    assert len(sessions.corrections(sid)) == 1
    sessions.delete(sid)
    assert db.one("SELECT COUNT(*) AS n FROM correction")["n"] == 0
    assert db.one("SELECT COUNT(*) AS n FROM turn")["n"] == 0
    db.close()


def test_builtin_scenarios_seeded_once(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    repo = ScenarioRepo(db)
    repo.seed_builtin(scenarios())
    repo.seed_builtin(scenarios())
    rows = repo.list()
    assert len(rows) == 11
    assert rows[0]["id"] == "free_talk"
    db.close()


def test_no_key_columns_in_schema(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    cols = {r["name"] for r in db.all("PRAGMA table_info(connection)")}
    assert "api_key" not in cols and "key" not in cols
    assert "key_last4" in cols
    db.close()
    with sqlite3.connect(tmp_path / "t.db") as c:
        assert c.execute("PRAGMA foreign_keys").fetchone() is not None


def test_migration_note_l1(tmp_path: Path, monkeypatch) -> None:
    """Plan item 1.4: a database of schema 4 (Russian-only fields) migrates with its data kept."""
    path = tmp_path / "old.db"
    monkeypatch.setattr("voicetutor.storage.db.MIGRATIONS", MIGRATIONS[:4])
    old = Database(path)
    assert old.schema_version() == 4
    old.execute(
        "INSERT INTO session(id, scenario_id, scenario_title_ru, level, correction_mode,"
        " started_at) VALUES ('s1', 'free_talk', 'Old title', 'B1', 'on_click', '2026-01-01')"
    )
    old.execute(
        "INSERT INTO turn(id, session_id, idx, role, text, created_at)"
        " VALUES ('t1', 's1', 0, 'user', 'I have 30 years.', '2026-01-01')"
    )
    old.execute(
        "INSERT INTO correction(id, turn_id, session_id, quote, fix, type, note_ru, pattern,"
        " created_at) VALUES ('c1', 't1', 's1', 'I have 30 years', 'I am 30', 'grammar',"
        " 'old explanation', 'age_have', '2026-01-01')"
    )
    old.execute(
        "INSERT INTO vocab(phrase, translation_ru, next_review_at, created_at)"
        " VALUES ('walk me through', 'old translation', '2026-01-02', '2026-01-01')"
    )
    old.close()
    monkeypatch.setattr("voicetutor.storage.db.MIGRATIONS", MIGRATIONS)
    db = Database(path)
    assert db.schema_version() == len(MIGRATIONS)
    assert db.one("SELECT note_l1 FROM correction WHERE id = 'c1'")["note_l1"] == "old explanation"
    s = db.one("SELECT scenario_title_l1, l1 FROM session WHERE id = 's1'")
    assert s["scenario_title_l1"] == "Old title" and s["l1"] == ""
    v = db.one("SELECT translation_l1 FROM vocab WHERE phrase = 'walk me through'")
    assert v["translation_l1"] == "old translation"
    cols = {r["name"] for r in db.all("PRAGMA table_info(correction)")}
    assert "note_l1" in cols and "note_ru" not in cols
    db.close()


def test_session_records_its_language(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    sid = SessionRepo(db).create(
        scenario_id="free_talk",
        scenario_title_l1="Conversa livre",
        level="B1",
        correction_mode="on_click",
        connection_id=None,
        connection_name="",
        model="",
        l1="pt-BR",
    )
    assert db.one("SELECT l1 FROM session WHERE id = ?", (sid,))["l1"] == "pt-BR"
    db.close()


def test_builtin_titles_follow_the_language(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    repo = ScenarioRepo(db)
    repo.seed_builtin(scenarios())
    row = repo.get("small_talk")
    assert repo.to_api(row, "es-419")["title_l1"] == "Charla con un colega"
    assert repo.to_api(row, "pt-BR")["title_l1"] == "Papo com um colega"
    # a built-in removed from the data file disappears from the table
    repo.seed_builtin([s for s in scenarios() if s["id"] != "small_talk"])
    assert repo.get("small_talk") is None
    db.close()
