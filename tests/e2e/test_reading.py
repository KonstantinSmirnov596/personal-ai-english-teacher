"""Reading screen end-to-end with a fake microphone (Spanish learner, the default language).

The microphone loops phrase p01 with two planted mistakes of Spanish speakers: "start" said
as "estart" and "third" said with /t/ (tests/fixtures/phrases.json, reading_p01_accent).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.e2e.conftest import E2E, open_env
from tests.e2e.test_conversation import wait_level

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def env(tmp_path_factory: pytest.TempPathFactory) -> Iterator[E2E]:
    yield from open_env(tmp_path_factory, "reading_p01_accent")


def test_reading_marks_sounds_and_accepts_feedback(env: E2E) -> None:
    env.wait_models()
    page = env.new_page()
    page.goto(env.lp.base + "/#/reading")
    page.wait_for_selector("[data-testid=reading-text][data-phrase-id=p01]")
    env.screenshot("13-reading-empty")

    # the first click opens the microphone; cancel and wait for the gap in the looping file
    page.click("[data-testid=reading-mic]")
    page.wait_for_selector("[data-testid=reading-panel][data-state=listening]", timeout=10_000)
    page.keyboard.press("Escape")
    page.wait_for_selector("[data-testid=reading-panel][data-state=idle]")
    wait_level(page, above=False, hold_s=1.0)
    page.keyboard.press("Space")
    page.wait_for_selector("[data-testid=reading-panel][data-state=listening]")
    wait_level(page, above=True, hold_s=0.3)
    wait_level(page, above=False, hold_s=1.0)
    page.keyboard.press("Space")

    page.wait_for_selector("[data-testid=read-word]", timeout=60_000)
    errors = page.locator("[data-testid=read-word][data-level=error]")
    assert sorted(t.strip(".").lower() for t in errors.all_inner_texts()) == ["start", "third"]
    assert page.locator("[data-testid=reading-score]").is_visible()

    # the first wrong word is opened: what was heard, the tip, the minimal pair
    detail = page.locator("[data-testid=word-detail]")
    assert detail.locator("h2").inner_text() == "start"
    assert detail.get_attribute("lang") == "es-419"
    # the inserted vowel is shown as an extra sound (plan item 2.2)
    title = page.inner_text("[data-testid=word-tip-title]")
    assert "Sobra un sonido" in title, title
    assert detail.locator(".phone-chip[data-level=error]").count() == 1
    assert "speak — espeak" in detail.inner_text()
    env.screenshot("14-reading-result")

    # the sidebar counts marked sounds
    page.locator("[data-testid=sound-row][data-phone=s]").wait_for(timeout=10_000)

    # "That was right" clears the mark and makes the sound less sensitive
    page.click("[data-testid=was-correct]")
    page.locator("[data-testid=reading-message]").filter(has_text="menos rigor").wait_for(
        timeout=10_000
    )
    assert errors.count() == 1
    with env.http() as c:
        sounds = {s["phone"]: s for s in c.get("/api/pron/sounds?days=7").json()}
    assert "s" not in sounds and sounds["θ"]["errors"] == 1  # the cleared mark is not counted

    # other words open on click
    page.locator("[data-testid=read-word]", has_text="third").click()
    title = page.inner_text("[data-testid=word-tip-title]")
    assert "/t/" in title and "/θ/" in title, title
    page.locator("[data-testid=read-word]", has_text="week").click()
    assert page.locator("[data-testid=word-tip-title]").count() == 0

    assert not page.locator("[data-testid=reading-mine]").is_disabled()
    page.click("[data-testid=reading-next]")
    page.wait_for_selector("[data-testid=reading-text][data-phrase-id=p02]")
    assert page.locator("[data-testid=read-word]").count() == 0
    problems = [line for line in env.console if line.startswith("error")]
    assert not problems, problems


def test_reading_in_portuguese(env: E2E) -> None:
    """The same recording assessed for a Portuguese speaker: Portuguese tips and catalog."""
    with env.http() as c:
        assert c.patch("/api/settings", json={"l1": "pt-BR"}).status_code == 200
    page = env.new_page()
    page.goto(env.lp.base + "/#/reading")
    page.wait_for_selector("[data-testid=reading-text][data-phrase-id=p01]")
    page.click("[data-testid=reading-mic]")
    page.wait_for_selector("[data-testid=reading-panel][data-state=listening]", timeout=10_000)
    page.keyboard.press("Escape")
    page.wait_for_selector("[data-testid=reading-panel][data-state=idle]")
    wait_level(page, above=False, hold_s=1.0)
    page.keyboard.press("Space")
    page.wait_for_selector("[data-testid=reading-panel][data-state=listening]")
    wait_level(page, above=True, hold_s=0.3)
    wait_level(page, above=False, hold_s=1.0)
    page.keyboard.press("Space")
    page.wait_for_selector("[data-testid=read-word]", timeout=60_000)
    page.locator("[data-testid=read-word]", has_text="third").click()
    detail = page.locator("[data-testid=word-detail]")
    assert detail.get_attribute("lang") == "pt-BR"
    title = page.inner_text("[data-testid=word-tip-title]")
    assert "Soou /t/ em vez de /θ/" in title, title
    assert "três" not in detail.inner_text()  # tips are Portuguese text, pairs stay English
    assert "Ponha a ponta da língua entre os dentes" in detail.inner_text()
    env.screenshot("22-reading-pt")
    with env.http() as c:
        c.patch("/api/settings", json={"l1": "es-419"})
