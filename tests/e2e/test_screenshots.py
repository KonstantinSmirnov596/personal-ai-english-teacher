"""Screenshots for the READMEs (plan item 4.5): docs/images/*.png from the real window.

Sample data only: the mock LLM (shown as a "DeepSeek · deepseek-flash" connection, no real key),
synthetic speech from the fake microphone, a fresh data directory. The test fails if a key or a
Windows user path is visible on the page.
"""

from __future__ import annotations

import getpass
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from tests.e2e.conftest import E2E, open_env
from tests.e2e.test_conversation import (
    speak_one_turn,
    start_session,
    wait_level,
    wait_phrase_end,
)
from tests.e2e.test_languages import wait_html_lang

pytestmark = pytest.mark.e2e

IMAGES = Path(__file__).resolve().parents[2] / "docs" / "images"
SHOTS = {"conversation-es": "turn_basic", "reading-pt-BR": "reading_p01_accent"}


@pytest.fixture(scope="module", params=sorted(SHOTS))
def env(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Iterator[E2E]:
    gen = open_env(tmp_path_factory, SHOTS[request.param])
    env = next(gen)
    env.shot = request.param  # type: ignore[attr-defined]
    yield env
    for _ in gen:
        pass


def clean_page(env: E2E, page: Any) -> None:
    html = page.content()
    assert env.key not in html
    assert getpass.getuser() not in html


def save(page: Any, name: str) -> Path:
    IMAGES.mkdir(parents=True, exist_ok=True)
    path = IMAGES / f"{name}.png"
    page.screenshot(path=str(path), full_page=False)
    return path


def test_readme_screenshots(env: E2E) -> None:
    shot: str = env.shot  # type: ignore[attr-defined]
    with env.http() as c:
        c.post(
            "/api/connections",
            json={
                "name": "DeepSeek",
                "base_url": env.mock.base_url,
                "model": "deepseek-flash",
                "api_key": env.key,
            },
        ).raise_for_status()
        if shot.endswith("pt-BR"):
            c.patch("/api/settings", json={"l1": "pt-BR"}).raise_for_status()
    env.wait_models()
    page = env.new_page()
    page.set_viewport_size({"width": 1180, "height": 760})

    if shot == "conversation-es":
        start_session(page, env)
        speak_one_turn(page)
        page.locator("[data-testid=turn-tutor] .turn-text:not(:empty)").nth(1).wait_for(
            timeout=60_000
        )
        mark = page.locator("[data-testid=correction-mark]").first
        mark.wait_for(timeout=30_000)
        page.wait_for_selector("[data-testid=panel][data-state=idle]", timeout=60_000)
        mark.click()  # corrections open on click by default
        page.locator("[data-testid=correction-card]").first.wait_for(timeout=10_000)
        wait_html_lang(page, "es-419")
    else:
        page.goto(env.lp.base + "/#/reading")
        wait_html_lang(page, "pt-BR")
        page.wait_for_selector("[data-testid=reading-text][data-phrase-id=p01]")
        page.click("[data-testid=reading-mic]")
        page.wait_for_selector("[data-testid=reading-panel][data-state=listening]", timeout=10_000)
        page.keyboard.press("Escape")
        page.wait_for_selector("[data-testid=reading-panel][data-state=idle]")
        wait_phrase_end(page)
        page.keyboard.press("Space")
        page.wait_for_selector("[data-testid=reading-panel][data-state=listening]")
        wait_level(page, above=True, hold_s=0.3)
        wait_level(page, above=False, hold_s=1.0)
        page.keyboard.press("Space")
        page.wait_for_selector("[data-testid=word-detail]", timeout=60_000)

    clean_page(env, page)
    path = save(page, shot)
    assert path.stat().st_size > 20_000
