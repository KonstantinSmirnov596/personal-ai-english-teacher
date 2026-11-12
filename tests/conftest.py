"""Shared pytest setup: isolate tests from the owner's data and keys."""

from __future__ import annotations

import contextlib
import os
import secrets
import tempfile
from collections.abc import Iterator
from pathlib import Path

import keyring
import keyring.errors
import pytest

from voicetutor import paths

# Tests share the real models directory (no re-downloads) but never touch the owner's data dir.
_REAL_MODELS = paths.models_dir()
REAL_DATA_DIR = paths.data_dir()  # read only by the live suite (owner's active connection)
os.environ.setdefault("VOICETUTOR_MODELS_DIR", str(_REAL_MODELS))
os.environ["VOICETUTOR_DATA_DIR"] = str(Path(tempfile.mkdtemp(prefix="voicetutor-test-data-")))
# One credential service per test session: two sessions running at once (or a bench script)
# never delete each other's keys. Launchers started by tests inherit it.
os.environ["VOICETUTOR_KEYRING_SERVICE"] = f"VoiceTutor-test-{os.getpid()}"
TEST_SERVICE = os.environ["VOICETUTOR_KEYRING_SERVICE"]
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from tests.mock_llm import MockLLM  # noqa: E402  (after the environment is isolated)
from tests.profile_opt import CHOICES, set_profile  # noqa: E402


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--vt-profile",
        default="auto",
        choices=CHOICES,
        help="model profile for the gpu and e2e suites (tests/profile_opt.py)",
    )


def pytest_configure(config: pytest.Config) -> None:
    set_profile(config.getoption("--vt-profile"))


@pytest.fixture
def test_key() -> str:
    return "sk-test-" + secrets.token_urlsafe(24)


@pytest.fixture
def mock_llm(test_key: str) -> Iterator[MockLLM]:
    mock = MockLLM(test_key).start()
    try:
        yield mock
    finally:
        mock.stop()


@pytest.fixture(autouse=True)
def _clean_test_keyring(request: pytest.FixtureRequest) -> Iterator[None]:
    """Remove every key the test stored in this session's test service.

    GPU and e2e modules share one running core per module and clean up their own keys.
    """
    yield
    if request.node.get_closest_marker("gpu") or request.node.get_closest_marker("e2e"):
        return
    service = os.environ["VOICETUTOR_KEYRING_SERVICE"]
    assert service.startswith("VoiceTutor-test-")
    for i in range(1, 11):
        with contextlib.suppress(keyring.errors.PasswordDeleteError):
            keyring.delete_password(service, f"connection-{i}")


@pytest.fixture(scope="session", autouse=True)
def _sweep_session_keyring() -> Iterator[None]:
    """At the end of the session no test key is left in the Credential Manager."""
    yield
    assert TEST_SERVICE.startswith("VoiceTutor-test-")
    for i in range(1, 51):
        with contextlib.suppress(keyring.errors.PasswordDeleteError):
            keyring.delete_password(TEST_SERVICE, f"connection-{i}")
