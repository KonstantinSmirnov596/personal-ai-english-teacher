# Plan and acceptance criteria

Five stages from `docs/SPEC.md` section 13. A stage is closed when `scripts/check_stage.ps1 <N>` exits with 0 and its report is in `docs/reports/`. Suites and required tests of earlier stages are part of every later acceptance. Items run in order; mark them in `docs/PROGRESS.md` only after their check passed.

## Defaults

The owner may change them; until then these apply (SPEC section 1).

| Question | Default |
| --- | --- |
| Working name | Voice Tutor; package `voicetutor`; data dir `%LOCALAPPDATA%\VoiceTutor`; keyring service `VoiceTutor`; env prefix `VOICETUTOR_` |
| Repository | Local git only, no remote |
| Code license | MIT, unless the license audit (0.6) finds an obstacle |
| Learner languages | `es-419`, `pt-BR`; Russian locale of the predecessor is dropped in stage 1 |
| Target language | General American English only |
| Platform | Windows 11 x64 (Windows 10 22H2 x64 supported, not tested) |

## Targets

From the predecessor (`docs/BASELINE_REPORT.md`) plus SPEC section 7 for `compacto`.

| Metric | Target | Where |
| --- | --- | --- |
| STT of a 10 s turn | ≤ 0.4 s | stages 0, 3 (`scripts/bench.py`) |
| TTS first sentence | ≤ 0.3 s | stages 0, 3 |
| End of turn → first audio, mock LLM 0 ms | ≤ 0.9 s | stages 0, 1, 3 |
| End of turn → first audio, mock LLM 500 ms | ≤ 1.5 s | stages 0, 1, 3 |
| VRAM, all models (`completo`) | ≤ 6.5 GB of 8 | stages 0, 3 |
| VRAM peak of the core process (`compacto`, 10 turns + 5 readings) | ≤ 5.0 GB | stage 3 |
| WER TTS → STT loop | ≤ 10 %; `compacto` no more than 2 pp worse than `completo` | stages 0, 3 |
| Startup to ready | ≤ 20 s warm | stage 4 |
| Pronunciation false "error" on correct reading | ≤ 3 % of phonemes, per learner language | stage 2 |
| Catalog substitution/insertion flagged "error" | ≥ 80 %, per learner language | stage 2 |
| Heard sound named correctly | ≥ 60 %, per learner language | stage 2 |
| Outbound connections in a full scenario | only the LLM host | stages 0, 4 |

A missed latency target does not block a stage by itself: record the measurement, the cause and the trade-off in the stage report.

---

## Stage 0. Transfer and foundation check

Goal: the predecessor's code runs under the new name, the repository holds no personal data, and the facts the rest of the plan depends on (hardware support, licenses, provider APIs) are confirmed from official sources.

- **0.1 Transfer.** Copy `trainer/`, `web/`, `scripts/`, `tests/`, `pyproject.toml`, `uv.lock`, `docs/protocol.md`, `docs/testing.md`, `docs/design.md`, `docs/ui/` (tracked files only; no `.git`, `.venv`, caches, fixtures, local settings, owner data). New git repository with a clean first commit. Brief and baseline report stay untracked.
  *Check:* `git status` shows only the intended files; no `.venv`, `test-results`, `*.wav`, `*.db`, `settings.local.json`.
- **0.2 Rename.** Package `trainer` → `voicetutor`; data dir `VoiceTutor`; env vars `VOICETUTOR_DATA_DIR`, `VOICETUTOR_MODELS_DIR`, `VOICETUTOR_KEYRING_SERVICE`; keyring service, mutex, window title, shortcut, icon name. Version `0.1.0`.
  *Check:* `tests/test_scaffold.py` (package imports, no `trainer` module, data dir name); `rg -w trainer` finds no code references.
- **0.3 Environment.** `scripts/setup.ps1` builds `.venv` from `uv.lock`, downloads pinned models into `%LOCALAPPDATA%\VoiceTutor\models`, fonts and VAD with hash checks.
  *Check:* repeated `setup.ps1` exits 0 (part of `check_stage.ps1`).
- **0.4 Cleanup.** Remove owner-specific content (names, laptop, ERP/ECM and document-workflow references in docs, user paths). Translate developer docs (`design.md`, `protocol.md`, `testing.md`, `docs/ui/`) and remaining comments to English. Russian remains only as ru-locale data in allowlisted paths until stage 1 replaces it.
  *Check:* `tests/test_hygiene.py`: no Windows user-profile paths, the current Windows user name, e-mail addresses, `sk-` keys, base64-alphabet strings longer than 30 chars (allowlist for hashes with reasons), `.wav` outside generated dirs, Cyrillic outside the allowlist.
- **0.5 Predecessor suites under the new name.** `fast`, `gpu`, `e2e` pass unchanged in substance.
  *Check:* `scripts/test.ps1 fast|gpu|e2e` green; required tests listed in `scripts/check_stage.py`.
- **0.6 Hardware facts (SPEC 7).** From official sources and an actual run: compute capabilities in the Windows `cu128` torch wheel and in CTranslate2 4.9.0 for Windows; minimum NVIDIA Windows driver for CUDA 12.8; `float16` and `int8_float16` support in CTranslate2 on the minimum architecture. If Turing (sm_75) is not covered, raise the minimum to Ampere everywhere.
  *Check:* `tests/gpu/test_stage0.py::test_torch_arch_list_covers_minimum` (reads `torch.cuda.get_arch_list()`), and filled table in `docs/reports/stage0.md` with links.
- **0.7 License audit.** Every Python dependency in `uv.lock`, every model, font, VAD/ONNX asset and binary component (espeak-ng): license from the primary source, link, whether it is in the repo/release or downloaded on the user's machine. GPL question for the owner, no legal conclusion.
  *Check:* `tests/test_licenses.py`: every package in `uv.lock` has a row in `docs/reports/licenses.md`; no row with an empty license; no model weights or espeak-ng binaries tracked by git.
- **0.8 Provider templates (SPEC 11).** DeepSeek, OpenAI, OpenRouter, Ollama, LM Studio, other OpenAI-compatible: base URL, auth header, model default, `response_format` support, streaming format, reasoning switch — each from official docs with links in `docs/reports/providers.md`. A template that cannot be confirmed is not included.
  *Check:* `tests/test_providers.py`: templates in code match the report (ids, base URLs), every confirmed template has at least one official link.
- **0.9 Benchmarks under the new name.** `scripts/bench.py` and `scripts/bench_turn.py` on the development machine (RTX 5060 Laptop, 8 GB).
  *Check:* numbers in `docs/reports/stage0.md` vs targets; `test_tts_stt_loop_wer` passes.

Acceptance (`check_stage.ps1 0`): repeated setup OK; `fast`, `gpu`, `e2e` green with the predecessor's required tests under the new name; `test_hygiene`, `test_licenses`, `test_providers` green; `docs/reports/stage0.md`, `licenses.md`, `providers.md` exist without placeholders or empty table cells.

---

## Stage 1. Learner languages

Goal: the whole app works in `es-419` and `pt-BR`, switched by hand without restart; the Russian locale is gone.

- **1.1 Language registry.** `voicetutor/data/l1/<lang>/meta.json` (`code`, `name_native`, `name_en`, `html_lang`, `detector` word lists); discovery by files; setting `l1`; first-run default from the Windows locale (`es-*` → es-419, `pt-*` → pt-BR, else es-419).
  *Check:* `tests/test_l1.py`: discovery, locale mapping, a third language added in a temp dir by files only is discovered.
- **1.2 Window i18n.** `web/i18n/es-419.js`, `web/i18n/pt-BR.js`; runtime loader; switch in Settings → Language without reload of the core and without page restart; `lang` attributes from `meta.json`. Core messages localized from `voicetutor/data/l1/<lang>/messages.json`.
  *Check:* `tests/test_i18n.py`: key completeness 100 % for both languages against the key set used in `web/js` and `index.html`, no empty values, same placeholders; e2e switch test.
- **1.3 Prompts with a language parameter.** `{{l1_name_en}}` in tutor, corrector, summary and helper prompts; per-language corrector example (`I have 30 years` / `In my city has a big park`); corrector receives the pattern list with language marks.
  *Check:* `tests/test_prompts.py`: rendered prompts for both languages name the right language, contain the right example, no "Russian".
- **1.4 `note_ru` → `note_l1`.** Protocol, pydantic schemas, mock LLM, window, export, DB migration with data kept; sessions record their `l1`.
  *Check:* `tests/test_storage.py::test_migration_note_l1` (old DB with `note_ru` rows migrates), protocol tests.
- **1.5 Language guard before TTS.** Replaces the Cyrillic check: es/pt detector (frequent words, diacritics, letter patterns); a rejected sentence is not spoken and a warning is logged.
  *Check:* `tests/test_lang_guard.py`: es and pt sentences rejected; English sentences with Spanish/Portuguese names and places pass (≥ 30 cases); gpu test that synthesis rejects them before model work.
- **1.6 Scenarios (SPEC 6).** 11 scenarios; ERP/ECM and document workflow removed; `title`/`description` per learner language; interviews follow the backend structure.
  *Check:* `tests/test_scenarios.py`: ids exactly as in SPEC, both languages present, English fields have no learner-language text.
- **1.7 Recurring-mistake keys.** Common key file with `l1: [...]`; names and hints in language files; keys not typical for es/pt removed; new keys from SPEC 12.
  *Check:* `tests/test_patterns.py`: key set equals SPEC table, `l1` marks match, every key marked for a language has a name and hint in it.
- **1.8 Corrector sets.** `corrector_eval.es.jsonl`, `corrector_eval.pt-BR.jsonl`: 40 cases each (28 typical errors, 8 correct incl. colloquial forms and fillers, 4 with low-confidence words); `live` suite parametrized by language with thresholds of `docs/testing.md` plus `note_l1` in the learner language and ≤ 25 words.
  *Check:* `tests/test_corrector_sets.py` (counts, schema); `live` run if a key is saved, otherwise deferred in `HUMAN_TASKS.md`.
- **1.9 Window behaviour.** Translations, "How do I say?", hints, summary and errors in the learner language; history keeps the language it was created in.
  *Check:* e2e conversation per language; e2e check that elements with `lang="en"` contain no learner-language text (guard detector).
- **1.10 Drop the Russian locale.** Remove `ru.js`, `i18n_ru.py`, Russian prompts, mistake keys, scenarios and the Russian corrector set. The Russian pronunciation catalog stays until item 2.1 replaces it.
  *Check:* `test_hygiene.py` allowlists only `voicetutor/data/l1_ru_catalog.json`; item 2.1 empties the list.

Acceptance (`check_stage.ps1 1`): stage 0 checks; i18n completeness 100 % for both languages; e2e conversation in each language; no learner-language text in `lang="en"` elements; `live` for both languages if a key exists, otherwise noted; `docs/reports/stage1.md`.

---

## Stage 2. Pronunciation for es and pt

Goal: catalogs, insertion errors, reading phrases and tips for each learner language, with metrics on synthetic speech.

- **2.1 Catalogs.** `voicetutor/data/l1/<lang>/catalog.json` with the SPEC 12 entries (`expected`, `heard`, `position`, `detect`, `default_level`, `priority`, `title`, `tip`, `examples`, `pairs`); tips refer to native sounds correctly for LatAm Spanish / Brazilian Portuguese; American tolerances kept.
  *Check:* `tests/test_catalogs.py`: schema, entry sets per language as in SPEC, every symbol in the phoneme inventory.
- **2.2 Insertion errors.** Competitor hypotheses with an inserted vowel at catalog positions; same windowed CTC likelihood ratio; diagnosis `heard: "+e"`; window shows the extra sound.
  *Check:* `tests/test_pron_logic.py::test_insertion_*` on synthetic posteriors; e2e reading shows an insertion.
- **2.3 Reading phrases.** 30 phrases (shared or per language), 6–12 words, American vocabulary; each non-manual entry covered by ≥ 2 phrases of its language.
  *Check:* `tests/test_catalogs.py::test_reading_coverage`.
- **2.4 Accent fixtures.** Kokoro from modified phoneme strings in carrier phrases (`espeak`, `bigi`, `berry`); entries Kokoro cannot render are marked unverifiable on synthesis.
  *Check:* fixtures generate; unverifiable list in the report.
- **2.5 Metrics per language.** Three American voices; false alarms, detection, naming as in Targets; unreliable entries with percentages.
  *Check:* `tests/gpu/test_pron.py` parametrized by language; `docs/reports/stage2.md` table per catalog entry.
- **2.6 Window.** Reading screen per language (tips, pairs, insertion display), feedback "That was right" still works.
  *Check:* e2e reading per language.

Acceptance (`check_stage.ps1 2`): earlier checks; metrics per language meet the targets; `stage2.md` with the per-entry table.

---

## Stage 3. Hardware

Goal: the app knows whether a machine is supported, picks a profile, and never crashes on missing or shrinking VRAM.

- **3.1 Hardware detector.** One module (NVML/`nvidia-smi`, Win32 APIs): GPU, VRAM total/free, driver, compute capability, RAM, free disk, AC/battery. Injected as a dependency; one point of compute-device configuration.
  *Check:* `tests/test_hardware.py` with fake detectors.
- **3.2 Profiles.** `completo` (≥ 7 GB free), `compacto` (5–7 GB: STT `int8_float16`, phoneme model loaded on demand and unloaded after 5 min idle, conversation pronunciation marks off by default), unsupported (< 5 GB, no NVIDIA, driver or architecture below minimum). Manual override in Settings → Performance.
  *Check:* `tests/test_profiles.py`; gpu tests run under both profiles.
- **3.3 VRAM shortage.** Unload the phoneme model on pressure; STT out-of-memory → clear message suggesting closing other programs; no process crash.
  *Check:* fast tests with injected OOM; gpu test.
- **3.4 Installer requirements check.** `scripts/requirements.ps1`, called by `setup.ps1` before any download; clear messages per failed item with a docs link.
  *Check:* `tests/test_requirements_ps1.py` feeds fake inputs to the PowerShell functions.
- **3.5 First-run wizard.** Eight steps (language, hardware, models, benchmark, microphone, sound and voice, LLM, level); re-runnable from Settings; table `hardware_profile`; nothing leaves the machine.
  *Check:* e2e wizard in both languages.
- **3.6 Unsupported screen.** Core receives a fake detector by dependency injection in a test and shows reasons with what to do.
  *Check:* `tests/test_unsupported.py` + window check.
- **3.7 Runtime warnings.** Battery once; driver or GPU change → offer steps 2 and 4.
  *Check:* fast tests.
- **3.8 Profile acceptance on the dev machine.** `compacto` peak VRAM ≤ 5.0 GB (10 turns + 5 readings, `nvidia-smi`); both profiles pass `gpu`, `e2e` and latency targets; WER delta ≤ 2 pp.
  *Check:* `scripts/bench_profiles.py` + gpu test; `docs/reports/stage3.md`.

Acceptance (`check_stage.ps1 3`): earlier checks; profile acceptance; wizard e2e in both languages; unsupported test.

---

## Stage 4. Distribution and publication readiness

Goal: a user without Python installs from a release zip by double-click; docs in three languages; CI and repository files ready; nothing published.

- **4.1 Installer.** `install.cmd` → `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1`; pinned uv from the Astral GitHub release with SHA-256 from the repo; `uv python install 3.12`; `uv sync --locked`; models by commit hash with resume and SHA-256; fonts/VAD by sha512; path check (spaces, non-ASCII) before downloads; shortcuts (desktop and Start menu after console confirmation); launch → wizard. `uninstall.cmd` removes shortcuts and environment, user data only after confirmation.
  *Check:* `scripts/check_clean_install.py` from the release zip with Mark of the Web into a clean directory with clean `LOCALAPPDATA`/`TEMP`; path tests; resume after interrupted download.
- **4.2 Release packaging.** `scripts/make_release.ps1` → `VoiceTutor-<version>.zip` (no models, no environment, no espeak-ng binaries), `SHA256SUMS.txt`, release notes in three languages (draft).
  *Check:* `tests/test_release.py` inspects the archive content.
- **4.3 Privacy hardening.** No turn text in logs by default; verbose-log setting with warning; network test kept.
  *Check:* fast test on log content; `tests/gpu/test_network.py`.
- **4.4 Documentation.** READMEs and `docs/<lang>/{install,hardware,api-keys,usage,troubleshooting,privacy}.md` in en/es/pt-BR; `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md`; token usage per turn measured on the mock and a cost formula without prices.
  *Check:* `tests/test_docs.py`: relative links resolve; every `docs/en/*.md` has `es` and `pt-BR` twins with the same `##` headings.
- **4.5 Screenshots.** Playwright on sample data, Spanish and Portuguese UI, no keys or personal data.
  *Check:* screenshot test produces the files referenced by the READMEs.
- **4.6 GitHub files.** `.github/workflows/ci.yml` (windows-latest: ruff, fast, i18n, JSON schemas, doc links, secret/personal-data scan); issue templates in three languages (bug with GPU/VRAM/driver/profile/version/log excerpt; feature); PR template in English; `scripts/ci_local.ps1`; `scripts/check_release.ps1` for `gpu` + `e2e`.
  *Check:* `scripts/ci_local.ps1` exits 0; YAML templates parse.
- **4.7 Diagnostics.** `scripts/collect_diagnostics.ps1`: versions, profile, logs without turn text and keys.
  *Check:* test plants a key marker and verifies it is absent from the archive.
- **4.8 Final regression.** All suites; `docs/reports/final.md`; release notes draft.
  *Check:* `check_stage.ps1 4`.

Acceptance (`check_stage.ps1 4`): all earlier checks; clean install from a MOTW-marked archive; `ci_local.ps1` green; `final.md`.
