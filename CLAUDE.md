# Voice Tutor

Open-source Windows desktop app for practicing spoken American English. Learners speak Latin American Spanish (`es-419`) or Brazilian Portuguese (`pt-BR`); the tutor speaks only General American English. Speech recognition, speech synthesis and pronunciation assessment run locally on an NVIDIA GPU; only dialogue text goes to the LLM provider the user picks.

The code base comes from a private single-user predecessor; its location and owner-specific notes are in `CLAUDE.local.md` (not tracked). The predecessor is **read-only**: never edit, commit, or run setup there.

Project documents:

- `docs/SPEC.md` — the brief (owner's language, not tracked in git). Source of truth for WHAT to build.
- `docs/BASELINE_REPORT.md` — what the predecessor does and its measured targets (not tracked in git).
- `docs/PLAN.md` — stages 0–4, items, checks. Source of truth for ORDER and for when a stage is closed.
- `docs/PROGRESS.md` — current stage and item, decisions with reasons, failed checks, measurements.
- `docs/HUMAN_TASKS.md` — what only the owner can do, plus the question queue.
- `docs/design.md`, `docs/protocol.md`, `docs/testing.md` — architecture, window-core contract, test method.
- `docs/reports/` — stage reports, `licenses.md`, `providers.md`, measurement data.

## Every session

1. Read `docs/PROGRESS.md`: current stage, current item, open problems.
2. Continue with the first open item of `docs/PLAN.md`.
3. Update `docs/PROGRESS.md` after every closed item and at the end of the session.

## Working mode: autonomous

- Make decisions inside a stage yourself. Record every non-trivial one in `docs/PROGRESS.md` → "Decisions": what and why, one or two lines.
- An item is closed only when its check ran and passed. Never mark something done that did not run.
- A stage is closed when `scripts/check_stage.ps1 <N>` exits with 0 and `docs/reports/stage<N>.md` (or the report named in the plan) is written. Then send the owner a stage summary (done, measurements vs targets, what failed, what is needed) and continue with the next stage.
- Questions to the owner go to `docs/HUMAN_TASKS.md` → "Question queue" and are asked in one message at the end of a stage. Meanwhile do whatever is not blocked; use the listed default.
- After three different failed approaches to a check, write down what was tried and seen, and move to independent work. Never weaken or delete a check; a criterion changes only with a reason in "Decisions".
- When documents contradict each other, pick the option that does not break "Hard constraints" and record the contradiction in "Decisions".
- Verify, do not recall: package versions, flags, licenses, driver requirements and provider API parameters are checked against official sources (docs, release notes, LICENSE files, `--help`, an actual run). Write the link next to the fact.

## Hard constraints

- No publishing: no `git push`, no GitHub repository, release, issue or PR without the owner's explicit command in chat. Work happens in the local git repository.
- Never ask the owner for an API key in chat. Keys are typed only into the app window.
- At runtime the only outbound traffic is HTTPS (or `http://127.0.0.1` for local providers) to the base URL of the active LLM connection. No telemetry, analytics, crash reports, update checks, CDNs, external fonts or scripts. Packages, models, fonts and the VAD are downloaded only at install time.
- Audio never leaves the computer: STT, TTS and pronunciation assessment run locally.
- API keys live only in Windows Credential Manager via `keyring`. A key never appears in files, the database, logs, tests, git, command output or chat. The window receives only the last 4 characters.
- The local server listens on `127.0.0.1` only, requires the launch token, checks `Origin` and `Host` for HTTP and WebSocket, and enables no CORS.
- The tutor speaks only American English. Learner-language text (Spanish, Portuguese) appears only as text and never reaches speech synthesis; a language guard rejects it before TTS.
- LLM output goes into the DOM as text (`textContent`); LLM JSON is validated against pydantic schemas.
- No test back doors in the app: no routes, flags or env vars that bypass security or fake recognition. Tests observe the window through `data-state`, `data-testid` and `lang` attributes. Hardware fakes are injected only through dependency injection inside unit tests.
- Logs contain no turn text by default; verbose logging is an explicit, warned setting.
- No personal data in the repository: no user names, Windows user paths, e-mail addresses, keys, tokens or voice recordings. `tests/test_hygiene.py` enforces this.
- Model weights and espeak-ng binaries (GPL-3.0) are never committed or put into the release archive; they are installed on the user's machine.

## Stack

Pinned in `uv.lock`; facts and links in `docs/reports/stage0.md`.

- Python 3.12, FastAPI + uvicorn in one process, SQLite, httpx for LLM (OpenAI-compatible `POST {base_url}/chat/completions`, SSE stream).
- STT: faster-whisper `turbo` (CTranslate2, CUDA). TTS: Kokoro-82M, `lang_code='a'`. Pronunciation: `facebook/wav2vec2-lv-60-espeak-cv-ft` + espeak-ng `en-us` (from `espeakng-loader`).
- torch `cu128` build; cuBLAS/cuDNN DLLs come from `torch\lib`. The compute device is chosen in one place (`voicetutor/gpu_env.py` / hardware profile).
- Window: static frontend without a build step (HTML, CSS, ES modules) in Edge `--app` with its own `--user-data-dir`.
- Tests: pytest; end-to-end — Playwright, channel `msedge`, fake microphone.
- App data: `%LOCALAPPDATA%\VoiceTutor` (database, audio, models, logs, Edge profile). Package `voicetutor`. Keyring service `VoiceTutor`.

## Learner languages

- A learner language is a set of files, no code changes: `web/i18n/<lang>.js`, `voicetutor/data/l1/<lang>/{meta,catalog,patterns,reading_phrases}.json` (reading phrases optional).
- Spanish: neutral Latin American, `tú`, no `vosotros`, no `voseo`, no Spain-only words. Portuguese: Brazilian, `você`, Brazilian spelling and vocabulary.
- English: code, identifiers, comments, logs, commit messages, developer docs. Learner language: UI, `note_l1`, summary takeaway, translations, tips, error messages.
- User-facing docs exist in `en` (primary), `es`, `pt-BR` with the same second-level headings.

## Commands

- `scripts/setup.ps1` — environment, dependencies, models, fonts, VAD. Safe to run again.
- `scripts/run.ps1` — start the app from a terminal.
- `scripts/test.ps1 fast|gpu|e2e|live|all` — test suites. `live` costs the owner money: only on the owner's word.
- `scripts/check_stage.ps1 <N>` — stage acceptance (suites of stage N and earlier, required tests, reports).
- `scripts/ci_local.ps1` — the CI steps, locally (ruff, fast suite).
- `scripts/check_release.ps1` — gpu and e2e under both profiles (what CI cannot run).
- `install.cmd` / `uninstall.cmd` — the user's installer and uninstaller (`scripts/setup.ps1`, `scripts/uninstall.ps1`).
- `scripts/make_release.ps1` — `dist/VoiceTutor-<version>.zip` and `SHA256SUMS.txt`. Nothing is uploaded.
- `scripts/collect_diagnostics.ps1` — a bug-report archive without keys or conversation text.

## Test isolation

Tests never touch the real data directory or real keys: `VOICETUTOR_DATA_DIR` (temp dir), `VOICETUTOR_KEYRING_SERVICE` (`VoiceTutor-test-<pid>`, one per test session), `VOICETUTOR_MODELS_DIR` (shared real models dir so models are not downloaded again).

## Code

- Type annotations everywhere; protocol messages and LLM responses are pydantic models; `ruff check` and `ruff format --check` are clean.
- UI strings only in `web/i18n/<lang>.js`; core user-facing messages only in `voicetutor/data/l1/<lang>/` files.
- No stubs or `TODO: implement` in closed items.
- Commit after every closed plan item: `stage<N>: <what was done>`, with the attribution trailer. Never `git push`.

## Compact Instructions

When compacting, keep: current stage and plan item, failing checks with their last errors, decisions and owner questions not yet written to `docs/PROGRESS.md` and `docs/HUMAN_TASKS.md`, and the fact that the source project is read-only and nothing may be pushed.
