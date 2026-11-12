"""Stage 3 end-to-end: the first-run wizard in both learner languages (plan item 3.5).

Each language gets a fresh data directory, so the wizard opens by itself. The window is driven
like a user would: the language step, the hardware check on this machine's real GPU, the models
installed by setup, the benchmark, the microphone check with the fake microphone, the voice
preview, the LLM connection to the mock provider, and the level. Then Settings → Performance
shows the stored measurement and switches the profile.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import pytest

from tests.e2e.conftest import E2E, open_env
from tests.e2e.test_languages import wait_html_lang

pytestmark = pytest.mark.e2e

TEXT = {
    "es-419": {
        "next": "Siguiente",
        "hardware": "Revisión del equipo",
        "finish": "Terminar y empezar",
        "skip_hint": "La lectura funciona sin conexión",
        "performance": "Rendimiento",
        "free": "libres de",
    },
    "pt-BR": {
        "next": "Avançar",
        "hardware": "Verificação do computador",
        "finish": "Concluir e começar",
        "skip_hint": "A leitura funciona sem conexão",
        "performance": "Desempenho",
        "free": "livres de",
    },
}


@pytest.fixture(scope="module", params=["es-419", "pt-BR"])
def env(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Iterator[E2E]:
    env_iter = open_env(tmp_path_factory, "turn_basic", wizard_done=False)
    env = next(env_iter)
    env.lang = request.param  # type: ignore[attr-defined]
    yield env
    for _ in env_iter:
        pass


def wait_attr(page: Any, selector: str, name: str, values: set[str], timeout: float = 30.0) -> str:
    """Poll from Python: the window's CSP forbids Playwright's string predicates."""
    deadline = time.monotonic() + timeout
    value = None
    while time.monotonic() < deadline:
        loc = page.locator(selector)
        if loc.count():
            value = loc.first.get_attribute(name)
            if value in values:
                return value
        time.sleep(0.1)
    raise AssertionError(f"{selector}[{name}] = {value!r}, expected one of {sorted(values)}")


def step(page: Any, name: str) -> None:
    wait_attr(page, "[data-testid=wizard]", "data-step", {name})


def next_step(page: Any, name: str) -> None:
    page.click("[data-testid=wizard-next]")
    step(page, name)


def test_first_run_wizard(env: E2E) -> None:
    lang: str = env.lang  # type: ignore[attr-defined]
    t = TEXT[lang]
    page = env.new_page()
    page.goto(env.lp.base + "/")

    # 1. Language: the wizard opens by itself, without the section navigation.
    step(page, "language")
    assert page.url.endswith("#/wizard/language")
    assert page.locator("nav.nav").count() == 0
    page.click(f"[data-testid=wizard-language-switch] [data-lang={lang}]")
    wait_html_lang(page, lang)
    assert page.locator("[data-testid=wizard-next]").inner_text() == t["next"]
    env.screenshot(f"30-wizard-language-{lang}")

    # 2. Hardware: this machine's real GPU (RTX 5060 Laptop, 8 GB) is supported.
    next_step(page, "hardware")
    assert page.locator("h1").first.inner_text() == t["hardware"]
    state = wait_attr(
        page,
        "[data-testid=wizard-hardware]",
        "data-state",
        {"completo", "compacto", "vram_low", "unsupported"},
    )
    assert state in {"completo", "compacto", "vram_low"}, state
    rows = page.locator("[data-testid=hardware-checks] tr[data-check]")
    checks = {
        rows.nth(i).get_attribute("data-check"): rows.nth(i).get_attribute("data-result")
        for i in range(rows.count())
    }
    assert {"gpu", "driver", "architecture", "vram", "ram", "disk", "power"} <= set(checks)
    assert checks["gpu"] == checks["driver"] == checks["architecture"] == "ok"
    assert not page.locator("[data-testid=wizard-next]").is_disabled()
    table = page.locator("[data-testid=hardware-checks]").inner_text()
    assert " free" not in table and "mains" not in table  # values in the learner's language
    assert t["free"] in table
    env.screenshot(f"31-wizard-hardware-{lang}")

    # 3. Models: installed by setup.
    next_step(page, "models")
    wait_attr(page, "[data-testid=wizard-models]", "data-state", {"present"})

    # 4. Benchmark: needs the models loaded, then about a few seconds on the GPU.
    next_step(page, "benchmark")
    env.wait_models()
    run = page.locator("[data-testid=benchmark-run]")
    deadline = time.monotonic() + 60
    while run.is_disabled():
        assert time.monotonic() < deadline, "benchmark button stayed disabled"
        time.sleep(0.2)
    run.click()
    wait_attr(page, "[data-testid=wizard-benchmark]", "data-state", {"done"}, timeout=180)
    profile = page.locator("[data-testid=benchmark-profile]").get_attribute("data-profile")
    assert profile in {"completo", "compacto"}
    with env.http() as c:
        stored = c.get("/api/hardware").json()["stored"]
    assert stored is not None and stored["measurements"]["transcript_ok"] is True
    assert stored["measurements"]["first_audio_ms"] > 0
    env.screenshot(f"32-wizard-benchmark-{lang}")

    # 5. Microphone: 3 s of "silence" and 4 s of speech from the fake microphone.
    next_step(page, "microphone")
    wait_attr(page, "[data-testid=wizard-microphone]", "data-state", {"idle"})
    page.click("[data-testid=mic-start]")
    wait_attr(
        page, "[data-testid=wizard-microphone]", "data-state", {"done", "no-signal"}, timeout=30
    )
    with env.http() as c:
        s = c.get("/api/settings").json()
    result = page.locator("[data-testid=mic-result]")
    assert float(result.get_attribute("data-threshold")) == s["vad_threshold"]
    assert s["vad_threshold"] in {0.5, 0.6, 0.7}
    assert s["noise_suppression"] is (result.get_attribute("data-room") != "quiet")
    assert page.locator(".mic-phrase").get_attribute("lang") == "en"

    # 6. Sound and voice: the preview plays; headphones answered.
    next_step(page, "sound")
    page.click("[data-testid=wizard-play]")
    wait_attr(page, "[data-testid=wizard-sound]", "data-state", {"played"}, timeout=30)
    page.check("#wizard-phones-true")
    time.sleep(0.3)
    with env.http() as c:
        assert c.get("/api/settings").json()["headphones"] is True

    # 7. LLM: a local template warns about the shared GPU; the mock provider is checked and saved.
    next_step(page, "llm")
    wait_attr(page, "[data-testid=wizard-llm]", "data-state", {"idle"})
    assert t["skip_hint"] in page.locator("[data-testid=wizard-llm]").inner_text()
    page.select_option("[data-testid=wizard-template]", "ollama")
    assert page.locator("[data-testid=llm-local-warning]").is_visible()
    page.select_option("[data-testid=wizard-template]", "openai_compatible")
    assert not page.locator("[data-testid=llm-local-warning]").is_visible()
    page.fill("#wizard-url", env.mock.base_url)
    page.fill("#wizard-model", "m")
    page.fill("[data-testid=wizard-key]", env.key)
    page.click("[data-testid=llm-check]")
    wait_attr(page, "[data-testid=wizard-llm]", "data-state", {"ok"}, timeout=30)
    page.wait_for_selector("[data-testid=llm-active]")
    assert env.key not in page.content()
    with env.http() as c:
        conns = c.get("/api/connections").json()
    assert len(conns) == 1 and conns[0]["is_active"] and conns[0]["key_last4"] == env.key[-4:]

    # 8. Level, then the conversation screen.
    next_step(page, "level")
    page.check("#wizard-level-B2")
    assert page.locator("[data-testid=wizard-finish]").inner_text() == t["finish"]
    env.screenshot(f"33-wizard-level-{lang}")
    page.click("[data-testid=wizard-finish]")
    page.wait_for_url("**/#/talk")
    page.wait_for_selector("nav.nav a")
    with env.http() as c:
        s = c.get("/api/settings").json()
    assert s["wizard_done"] is True and s["level"] == "B2" and s["l1"] == lang

    # A new start does not open the wizard again.
    page.goto(env.lp.base + "/")
    page.wait_for_selector("nav.nav a")
    assert "#/wizard" not in page.url

    # Settings → Performance: the stored measurement, a manual profile, the wizard again.
    page.goto(env.lp.base + "/#/settings/performance")
    page.wait_for_selector("[data-testid=last-measurement]")
    assert page.locator("h1").first.inner_text() == t["performance"]
    page.select_option("[data-testid=profile-select]", "compacto")
    wait_attr(page, "[data-testid=profile-current]", "data-profile", {"compacto"})
    with env.http() as c:
        s = c.get("/api/settings").json()
        assert s["profile"] == "compacto" and s["pron_in_conversation"] is False
        assert c.get("/api/hardware").json()["profile"] == "compacto"
    env.screenshot(f"34-settings-performance-{lang}")
    page.select_option("[data-testid=profile-select]", "auto")
    wait_attr(page, "[data-testid=profile-current]", "data-profile", {"completo", "compacto"})
    page.click("[data-testid=rerun-wizard]")
    step(page, "language")
    # Re-run from Settings: the sections stay reachable.
    assert page.locator("nav.nav").count() == 1
