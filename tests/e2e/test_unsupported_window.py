"""Stage 3 window check: unsupported hardware is explained, nothing crashes (plan item 3.6).

The core runs in this test process (uvicorn in a thread) and receives a fake hardware detector
through its constructor: dependency injection inside the test, no switch in the app. Edge opens
the launch URL like the real window; the first-run wizard explains each failed requirement with
what to do and where the documentation is, and the conversation screen names the problem.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from tests.e2e.test_languages import wait_html_lang
from tests.e2e.test_wizard import step, wait_attr
from tests.hw_fakes import FakeDetector, card, machine
from voicetutor.hardware import HardwareInfo

pytestmark = pytest.mark.e2e


class InProcessCore:
    def __init__(self, data_dir: Path, info: HardwareInfo) -> None:
        import uvicorn

        from voicetutor.core import Core
        from voicetutor.server.app import create_app
        from voicetutor.server.guard import AccessKeys

        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        self.keys = AccessKeys(port=self.port)
        self.detector = FakeDetector(info)
        self.core = Core(
            data_dir=data_dir, keys=self.keys, detector=self.detector, load_models=True
        )
        config = uvicorn.Config(
            create_app(self.core), host="127.0.0.1", port=self.port, log_config=None, lifespan="on"
        )
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + 30
        while not self.server.started:
            assert time.monotonic() < deadline, "server did not start"
            time.sleep(0.05)
        self.base = f"http://127.0.0.1:{self.port}"
        self.url = f"{self.base}/?t={self.keys.launch_token}"

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=15)


@pytest.fixture(scope="module")
def browser() -> Iterator[Any]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        yield b
        b.close()


def open_window(browser: Any, core: InProcessCore) -> Any:
    context = browser.new_context(viewport={"width": 1180, "height": 860})
    page = context.new_page()
    page.goto(core.url)
    page.wait_for_url(core.base + "/**")
    return page


@pytest.mark.parametrize(
    ("info", "failed"),
    [
        (machine(gpu=None, battery=None), "gpu"),
        (machine(gpu=card(driver="566.36")), "driver"),
        (machine(gpu=card(cc=(6, 1))), "architecture"),
    ],
)
def test_unsupported_screen_explains_why(
    browser: Any, tmp_path: Path, info: HardwareInfo, failed: str
) -> None:
    core = InProcessCore(tmp_path, info)
    try:
        page = open_window(browser, core)
        step(page, "language")
        page.click("[data-testid=wizard-next]")
        step(page, "hardware")
        wait_attr(page, "[data-testid=wizard-hardware]", "data-state", {"unsupported"})
        assert (
            page.locator("[data-testid=hardware-profile]").get_attribute("data-profile")
            == "unsupported"
        )
        row = page.locator(f"[data-testid=hardware-checks] tr[data-check={failed}]")
        assert row.get_attribute("data-result") == "fail"
        fix = page.locator(f"[data-testid=hardware-fix][data-check={failed}]")
        text = fix.inner_text()
        assert f"docs/es/hardware.md#{failed}" in text
        assert len(text) > 80  # what to do, in the learner's language
        assert page.locator("[data-testid=wizard-next]").is_disabled()
        page.screenshot(path=str(tmp_path / f"unsupported-{failed}.png"), full_page=True)

        # The conversation screen names the problem and links to the details.
        page.goto(core.base + "/#/talk")
        banner = page.locator("[data-testid=problem-banner][data-code=unsupported_hardware]")
        banner.wait_for(timeout=15_000)
        assert "requisitos mínimos" in banner.inner_text()
        banner.locator("[data-testid=problem-details]").click()
        step(page, "hardware")

        # Portuguese: the same screen, Portuguese text and documentation folder.
        page.goto(core.base + "/#/settings/language")
        page.click("[data-testid=language-switch] [data-lang=pt-BR]")
        wait_html_lang(page, "pt-BR")
        page.goto(core.base + "/#/wizard/hardware")
        wait_attr(page, "[data-testid=wizard-hardware]", "data-state", {"unsupported"})
        text = page.locator(f"[data-testid=hardware-fix][data-check={failed}]").inner_text()
        assert f"docs/pt-BR/hardware.md#{failed}" in text
        assert core.core.models.problem == "unsupported_hardware"
        assert not core.core.stt.loaded and not core.core.tts.loaded
        page.context.close()
    finally:
        core.stop()
