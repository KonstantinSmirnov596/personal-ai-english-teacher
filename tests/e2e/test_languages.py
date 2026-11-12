"""Stage 1 end-to-end: switch the learner language without a restart, then talk in Portuguese.

The default learner language of a fresh data directory is the Windows-locale suggestion (Spanish
on machines that are neither es-* nor pt-*); `test_conversation.py` covers a whole Spanish turn.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.e2e.conftest import E2E, open_env
from tests.e2e.test_conversation import speak_one_turn
from voicetutor.lang_guard import classify, not_english

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def env(tmp_path_factory: pytest.TempPathFactory) -> Iterator[E2E]:
    yield from open_env(tmp_path_factory, "turn_basic")


def nav_text(page) -> str:
    return page.locator("nav.nav").inner_text()


def test_language_switch_and_portuguese_conversation(env: E2E) -> None:
    with env.http() as c:
        r = c.post(
            "/api/connections",
            json={"name": "Mock", "base_url": env.mock.base_url, "model": "m", "api_key": env.key},
        )
        assert r.status_code == 201, r.text
        langs = c.get("/api/languages").json()
    assert [x["code"] for x in langs["available"]] == ["es-419", "pt-BR"]
    env.wait_models()
    page = env.new_page()
    page.goto(env.lp.base + "/#/talk")
    page.wait_for_selector("nav.nav a")
    start_lang = langs["current"]
    assert page.get_attribute("html", "lang") == start_lang

    # Settings → Language: Portuguese, without reloading the page
    page.goto(env.lp.base + "/#/settings/language")
    page.evaluate("window.__noReload = 1")
    page.click("[data-testid=language-switch] [data-lang=pt-BR]")
    page.wait_for_function("document.documentElement.lang === 'pt-BR'")
    assert page.evaluate("window.__noReload") == 1
    assert "Conversa" in nav_text(page) and "Leitura" in nav_text(page)
    assert page.locator("h1").first.inner_text() == "Idioma"
    with env.http() as c:
        assert c.get("/api/settings").json()["l1"] == "pt-BR"
    env.screenshot("20-language-pt")

    # Scenario titles in Portuguese, then a turn: corrections in Portuguese
    page.goto(env.lp.base + "/#/talk")
    card = page.locator("[data-scenario=interview_backend]")
    assert "Entrevista: desenvolvedor back-end" in card.inner_text()
    card.click()
    page.click("[data-testid=start-session]")
    page.wait_for_selector("[data-testid=turn-tutor] .turn-text:not(:empty)", timeout=60_000)
    page.wait_for_selector("[data-testid=panel][data-state=idle]", timeout=60_000)
    speak_one_turn(page)
    page.locator("[data-testid=turn-tutor] .turn-text:not(:empty)").nth(1).wait_for(timeout=60_000)
    page.wait_for_selector("[data-testid=panel][data-state=idle]", timeout=60_000)
    mark = page.locator("[data-testid=correction-mark]").first
    mark.wait_for(timeout=30_000)
    mark.click()
    card = page.locator("[data-testid=correction-card]").first
    assert card.get_attribute("lang") == "pt-BR"
    note = card.locator(".card-note").first.inner_text()
    assert classify(note).language == "pt-BR", note

    # Translation helper answers in Portuguese, as text only
    page.locator("[data-testid=tutor-translate]").first.click()
    tr = page.locator("[data-testid=translation]").first
    tr.filter(has_text="Tradução de teste").wait_for(timeout=20_000)
    assert tr.get_attribute("lang") == "pt-BR"

    # English stays English: no learner-language text in any element marked lang="en"
    en_texts = page.eval_on_selector_all("[lang=en]", "els => els.map(e => e.textContent)")
    assert en_texts and not [t for t in en_texts if not_english(t)]
    env.screenshot("21-conversation-pt")

    # The corrector was asked for Brazilian Portuguese explanations
    corr = [r for r in env.mock.requests if r["body"].get("response_format")]
    assert any("Brazilian Portuguese" in r["body"]["messages"][0]["content"] for r in corr)

    # Back to Spanish: the past session keeps its own language in the history
    page.goto(env.lp.base + "/#/settings/language")
    page.click("[data-testid=language-switch] [data-lang=es-419]")
    page.wait_for_function("document.documentElement.lang === 'es-419'")
    assert "Conversación" in nav_text(page)
    with env.http() as c:
        sessions = c.get("/api/sessions").json()
    assert sessions[0]["l1"] == "pt-BR"
