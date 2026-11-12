"""Built-in scenarios (plan item 1.6, SPEC 6)."""

from __future__ import annotations

from voicetutor import l1
from voicetutor.data_files import scenarios
from voicetutor.lang_guard import not_english

SPEC_IDS = [
    "free_talk",
    "small_talk",
    "standup",
    "client_call",
    "interview_backend",
    "interview_frontend",
    "interview_qa",
    "interview_ml_engineer",
    "interview_data_scientist",
    "interview_mlops",
    "interview_ai_engineer",
]
# SPEC 6 titles (es / pt) that must appear exactly.
SPEC_TITLES = {
    "free_talk": ("Conversación libre", "Conversa livre"),
    "small_talk": ("Charla con un colega", "Papo com um colega"),
    "client_call": ("Llamada con un cliente", "Ligação com um cliente"),
    "interview_backend": (
        "Entrevista: desarrollador backend",
        "Entrevista: desenvolvedor back-end",
    ),
    "interview_qa": ("Entrevista: QA", "Entrevista: QA"),
    "interview_ai_engineer": (
        "Entrevista: ingeniero de IA (LLM)",
        "Entrevista: engenheiro de IA (LLM)",
    ),
}
FORBIDDEN = ("erp", "ecm", "document workflow", "document management", "document system")


def test_ids_exactly_as_in_spec() -> None:
    assert [s["id"] for s in scenarios()] == SPEC_IDS


def test_titles_and_descriptions_in_every_learner_language() -> None:
    for s in scenarios():
        for code in l1.codes():
            assert s["title"][code].strip(), (s["id"], code)
            assert s["description"][code].strip(), (s["id"], code)
    for sid, (es, pt) in SPEC_TITLES.items():
        s = next(x for x in scenarios() if x["id"] == sid)
        assert s["title"]["es-419"] == es and s["title"]["pt-BR"] == pt


def test_english_fields_are_english() -> None:
    for s in scenarios():
        texts = [s["title_en"], s["role"], s["setting"], *s["goals"], *s["openers"]]
        assert not [t for t in texts if not_english(t)], s["id"]
        assert len(s["openers"]) >= 3


def test_no_erp_or_document_workflow() -> None:
    for s in scenarios():
        blob = " ".join(
            [s["title_en"], s["role"], s["setting"], *s["goals"], *s["openers"]]
        ).lower()
        assert not [w for w in FORBIDDEN if w in blob], s["id"]


def test_interviews_follow_the_backend_structure() -> None:
    """SPEC 6: experience → one project → trade-off → conflict or failure → candidate's questions;
    the interviewer gives no feedback."""
    for s in scenarios():
        if not s["id"].startswith("interview_"):
            continue
        goals = " ".join(s["goals"]).lower()
        for part in ("background", "one project in depth", "trade-off", "conflict or a failure"):
            assert part in goals, (s["id"], part)
        assert "candidate's questions" in goals
        assert "do not give feedback" in goals
