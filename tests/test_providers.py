"""Provider templates (plan item 0.8): the code's templates match docs/reports/providers.md."""

from __future__ import annotations

import re
from pathlib import Path

from voicetutor.data_files import provider_templates
from voicetutor.llm.client import validate_base_url, validate_extra_params

REPO = Path(__file__).resolve().parent.parent
REPORT = REPO / "docs" / "reports" / "providers.md"
EXPECTED_IDS = {"deepseek", "openai", "openrouter", "ollama", "lmstudio", "openai_compatible"}


def _report_rows() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        m = re.match(r"^\|\s*`([a-z_]+)`\s*\|", s)
        if m:
            rows[m.group(1)] = [c.strip() for c in s.strip("|").split("|")]
    return rows


def test_templates_match_the_report() -> None:
    templates = {t["id"]: t for t in provider_templates()}
    rows = _report_rows()
    # A template that could not be confirmed is not shipped, but the plan expects all six.
    assert set(templates) == EXPECTED_IDS, set(templates) ^ EXPECTED_IDS
    assert set(rows) >= set(templates), set(templates) - set(rows)
    for tid, tpl in templates.items():
        row = " ".join(rows[tid])
        if tpl["base_url"]:
            assert f"`{tpl['base_url']}`" in row, (tid, tpl["base_url"])
        if tpl["model"]:
            assert f"`{tpl['model']}`" in row, (tid, tpl["model"])
        if tid != "openai_compatible":
            assert re.search(r"https://[^\s)]+", row), f"{tid}: no official source link"
            assert tpl["docs_url"].startswith("https://"), tid


def test_template_endpoints_are_valid() -> None:
    for tpl in provider_templates():
        if tpl["base_url"]:
            assert validate_base_url(tpl["base_url"]), tpl["id"]
        assert validate_extra_params(tpl["extra_params"]), tpl["id"]
        assert tpl["kind"] in {"cloud", "local", "custom"}
        if tpl["kind"] == "local":
            assert tpl["base_url"].startswith("http://127.0.0.1:"), tpl["id"]
        if tpl["kind"] == "cloud":
            assert tpl["base_url"].startswith("https://"), tpl["id"]
