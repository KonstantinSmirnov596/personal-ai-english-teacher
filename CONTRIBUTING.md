# Contributing to Voice Tutor

Thank you for helping. Voice Tutor is a Windows desktop app for practicing spoken American English, for learners who speak Latin American Spanish or Brazilian Portuguese. Bug reports, translations, pronunciation catalogs and code are all welcome.

Code, comments, commit messages and developer documentation are in English. User-facing texts are in Spanish and Portuguese (and English for the installer and the docs).

## Reporting bugs and ideas

Use the issue templates (bug report or feature request, in English, Spanish or Portuguese). For a bug, attach the archive from `scripts\collect_diagnostics.ps1`: it contains versions, the hardware profile and logs without keys or conversation text. Never paste an API key anywhere. Security problems go through `SECURITY.md`, not public issues.

## Development setup

Requirements: Windows 10 22H2 or 11, an NVIDIA GPU of the Turing generation or newer with driver 572.61 or newer, and Git. Python is not needed: the setup installs its own.

```powershell
scripts\setup.ps1 -Dev         # uv, Python 3.12, packages and test tools from uv.lock, models, fonts
scripts\run.ps1                # start the app from a terminal
scripts\test.ps1 fast          # tests without a GPU (about a minute)
scripts\test.ps1 gpu           # models on the GPU
scripts\test.ps1 e2e           # the whole window in Edge with a fake microphone
scripts\ci_local.ps1           # the CI steps
```

`scripts\setup.ps1 -Dev -NoHardwareCheck -SkipModels` prepares only the Python environment on a machine without an NVIDIA GPU (enough for `fast` and `ruff`). The `live` suite calls a real LLM provider with your own key and costs money; it is never required for a pull request.

How the app is built: `docs/design.md` (architecture), `docs/protocol.md` (window ↔ core contract), `docs/testing.md` (how everything is tested without a person).

## Rules the project keeps

These are checked by tests where possible; a pull request must not weaken them.

- **Audio stays on the computer.** Speech recognition, speech synthesis and pronunciation assessment run locally. Only dialogue text goes to the LLM provider the user picks.
- **No other network traffic at run time.** No telemetry, analytics, crash reports, update checks, CDNs, external fonts or scripts. Packages, models, fonts and the voice detector are downloaded only by the installer, pinned and checksummed.
- **Keys live only in the Windows Credential Manager** (through `keyring`). A key never appears in files, the database, logs, tests, commits or output; the window receives only its last four characters.
- **The local server** listens on `127.0.0.1` only, requires the launch token, checks `Origin` and `Host`, and enables no CORS.
- **The tutor speaks only American English.** Learner-language text is shown, never spoken; a language guard rejects it before speech synthesis.
- **LLM output is untrusted**: it goes into the page as text (`textContent`), and its JSON is validated with pydantic.
- **No test back doors.** No routes, flags or environment variables that bypass security or fake hardware or recognition. Test doubles are passed to constructors in tests.
- **Logs contain no conversation text** unless the user turns on the detailed log.
- **No personal data in the repository** (names, Windows user paths, e-mail addresses, keys, recordings); `tests/test_hygiene.py` checks this.
- **No model weights or espeak-ng binaries** in the repository or the release archive.

## Code style

- Python 3.12 with type annotations; `ruff check` and `ruff format --check` must be clean.
- Protocol messages and LLM answers are pydantic models.
- The window is static HTML, CSS and ES modules without a build step. Interface strings live only in `web/i18n/<lang>.js`; messages from the core live in `voicetutor/data/l1/<lang>/`.
- Tests observe the window through `data-testid`, `data-state` and `lang` attributes.

## Adding a learner language

A learner language is a set of files, no code changes:

- `web/i18n/<lang>.js` with the same keys as `web/i18n/es-419.js`;
- `voicetutor/data/l1/<lang>/meta.json`, `messages.json`, `patterns.json`, `catalog.json` (the pronunciation mistakes typical for that language) and `corrector_eval.jsonl`;
- user documentation `docs/<lang>/` and a README with the same sections as the English ones.

`tests/test_i18n.py`, `tests/test_l1.py` and `tests/test_catalogs.py` tell you what is missing.

## Pull requests

- One topic per pull request, with tests for the change.
- `scripts\ci_local.ps1` passes; run `gpu` and `e2e` when you touch speech, pronunciation or the window.
- Describe what changed and how you tested it (the pull request template asks).
- By contributing you agree that your contribution is licensed under the MIT license of the project.
