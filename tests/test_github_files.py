"""GitHub repository files (plan item 4.6): the workflow and the templates parse and agree."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / ".github"
LANGS = ("en", "es", "pt-BR")


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def test_workflow_is_minimal_and_pinned() -> None:
    wf = load(GH / "workflows" / "ci.yml")
    assert wf["permissions"] == {"contents": "read"}
    steps = wf["jobs"]["fast"]["steps"]
    uses = [s["uses"] for s in steps if "uses" in s]
    assert uses and all(re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", u) for u in uses), uses
    runs = " ".join(s.get("run", "") for s in steps)
    assert "ci_local.ps1" in runs and "-NoHardwareCheck" in runs
    text = (GH / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "secrets." not in text  # CI never needs a key


def test_issue_forms_in_three_languages() -> None:
    forms = {p.stem: load(p) for p in (GH / "ISSUE_TEMPLATE").glob("*.yml") if p.stem != "config"}
    assert set(forms) == {f"{k}_{lang}" for k in ("bug", "feature") for lang in LANGS}
    for kind in ("bug", "feature"):
        ids = None
        for lang in LANGS:
            form = forms[f"{kind}_{lang}"]
            assert form["name"] and form["description"] and form["body"]
            these = [b.get("id") for b in form["body"]]
            ids = ids or these
            assert these == ids, (kind, lang)
            for block in form["body"]:
                attrs = block["attributes"]
                if block["type"] != "markdown":
                    assert attrs["label"].strip(), (kind, lang, block.get("id"))
    bug_ids = [b.get("id") for b in forms["bug_en"]["body"]]
    for field in ("version", "gpu", "driver", "profile", "log"):
        assert field in bug_ids
    config = load(GH / "ISSUE_TEMPLATE" / "config.yml")
    assert config["blank_issues_enabled"] is False


def test_pull_request_template_in_english() -> None:
    text = (GH / "pull_request_template.md").read_text(encoding="utf-8")
    assert "ci_local.ps1" in text and text.isascii()
