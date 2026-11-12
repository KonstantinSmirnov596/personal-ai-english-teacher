# Progress log

Maintained by Claude Code. Read at the start of every session, updated after every closed plan item.

## State

- Current stage: 0
- Current item: 0.1
- Last stage check: none yet

## Plan items

Mark `[x]` only after the item's check passed.

### Stage 0

- [ ] 0.1 Transfer
- [ ] 0.2 Rename
- [ ] 0.3 Environment
- [ ] 0.4 Cleanup
- [ ] 0.5 Predecessor suites under the new name
- [ ] 0.6 Hardware facts
- [ ] 0.7 License audit
- [ ] 0.8 Provider templates
- [ ] 0.9 Benchmarks under the new name

### Stage 1

- [ ] 1.1 Language registry
- [ ] 1.2 Window i18n
- [ ] 1.3 Prompts with a language parameter
- [ ] 1.4 `note_ru` → `note_l1`
- [ ] 1.5 Language guard before TTS
- [ ] 1.6 Scenarios
- [ ] 1.7 Recurring-mistake keys
- [ ] 1.8 Corrector sets
- [ ] 1.9 Window behaviour
- [ ] 1.10 Drop the Russian locale

### Stage 2

- [ ] 2.1 Catalogs
- [ ] 2.2 Insertion errors
- [ ] 2.3 Reading phrases
- [ ] 2.4 Accent fixtures
- [ ] 2.5 Metrics per language
- [ ] 2.6 Window

### Stage 3

- [ ] 3.1 Hardware detector
- [ ] 3.2 Profiles
- [ ] 3.3 VRAM shortage
- [ ] 3.4 Installer requirements check
- [ ] 3.5 First-run wizard
- [ ] 3.6 Unsupported screen
- [ ] 3.7 Runtime warnings
- [ ] 3.8 Profile acceptance

### Stage 4

- [ ] 4.1 Installer
- [ ] 4.2 Release packaging
- [ ] 4.3 Privacy hardening
- [ ] 4.4 Documentation
- [ ] 4.5 Screenshots
- [ ] 4.6 GitHub files
- [ ] 4.7 Diagnostics
- [ ] 4.8 Final regression

## Decisions

Format: date, item, decision, reason. Deviations from SPEC, PLAN or `docs/design.md` and changed criteria go here too.

| Date | Item | Decision | Reason |
| --- | --- | --- | --- |
| 2026-11-12 | setup | The brief and the baseline arrived as `OSS_SPEC.md` and `BASELINE_REPORT.md` in the project root; moved to `docs/SPEC.md` and `docs/BASELINE_REPORT.md` as the brief's "how to start" section prescribes | The kickoff prompt reads `docs/SPEC.md` |
| 2026-11-12 | setup | `docs/SPEC.md` and `docs/BASELINE_REPORT.md` stay untracked (`.git/info/exclude`) | They are the owner's private brief in Russian with references to the owner's machine; the public history must not contain them. The owner decides whether to publish them (HUMAN_TASKS) |
| 2026-11-12 | setup | All repository documents, including PLAN, PROGRESS, HUMAN_TASKS and reports, are in English; summaries to the owner in chat are in Russian | SPEC 3: no Russian in code, comments or documentation of the public repository |
| 2026-11-12 | setup | Owner-specific notes (predecessor path, dev machine, chat language) live in untracked `CLAUDE.local.md`; read-only rules for the predecessor path in untracked `.claude/settings.local.json` | They name the owner's folders and machine; SPEC 3 removes such references from the public repository |
| 2026-11-12 | 0.1 | Transfer = `git ls-files` of the predecessor for the listed paths, copied with `tar`; `docs/data` and `docs/prompts` not transferred | SPEC 3 lists the paths; the data and prompts already live in `voicetutor/data` and `voicetutor/prompts`, the docs copies were drafts |
| 2026-11-12 | 0.2 | `uv.lock` re-locked with uv 0.13.7 only to rename the project package; all 122 dependency pins unchanged | The lock records the project name; a diff showed only the renamed block |
| 2026-11-12 | 0.2 | Cookie renamed `voicetutor_session`; shortcut and window title "Voice Tutor"; PowerShell helpers `Get-AppDataDir`, `Set-AppEnv` | No predecessor name left in code |
| 2026-11-12 | 0.2 | `README.md` and MIT `LICENSE` ("Voice Tutor contributors") created in stage 0 | hatchling refuses to build the package without the README declared in `pyproject.toml`; the copyright line is an owner question |
| 2026-11-12 | 0.4 | UI mockups in `docs/ui/` translated to Latin American Spanish, not English | They show the real UI, which is always in a learner language; prose docs are English |
| 2026-11-12 | 0.4 | Stage 0 keeps the predecessor's Russian locale as allowlisted data (`CYRILLIC_ALLOWED` in `tests/test_hygiene.py`, per file with a reason); item 1.10 empties the list | SPEC 3 allows Russian as ru-locale data while the locale exists; predecessor tests need it until stage 1 replaces the locale |
| 2026-11-12 | 0.4 | Hygiene scan covers tracked and untracked-but-not-ignored files (`git ls-files --cached --others --exclude-standard`); `uv.lock` is skipped for e-mail and base64 checks; hex digests, SRI hashes and explicit `sk-test-` fakes are not secrets; the current Windows user name must not appear | What git would publish is what matters; the lock file holds only public package hashes |
| 2026-11-12 | 0.4 | `scripts/uia_click.ps1` takes the Edge button labels as a parameter (English default) instead of embedding Russian labels | Developer probe for localized Windows; no Russian in scripts |
| 2026-11-12 | 0.5 | Predecessor's required tests kept verbatim as `PREDECESSOR_TESTS` in `scripts/check_stage.py`; `test_cuda_device_is_rtx5060` replaced by `test_cuda_device_meets_minimum` (NVIDIA, compute capability ≥ 7.5) | The public app supports any NVIDIA GPU from Turing on; the dev machine still passes |
| 2026-11-12 | 0.6 | Minimum architecture stays Turing (compute capability 7.5); minimum driver 572.61 | torch 2.11 cu128 Windows is built for `7.5;8.0;8.6;9.0;10.0;12.0` (build script and local `get_arch_list`); CTranslate2 4.9.0 has native sm_75 code (build script and `cuobjdump` on the installed DLL); its wheels are built with CUDA 12.8.1, whose Windows driver minimum is 572.61 |
| 2026-11-12 | 0.7 | License table of Python packages generated by `scripts/license_audit.py` and checked by `tests/test_licenses.py`; packages without license metadata reviewed by hand (`REVIEWED` map) | Reproducible after every relock; facts come from each package's own metadata |
| 2026-11-12 | 0.8 | Provider templates moved to `voicetutor/data/providers.json` (six templates); connection field `json_mode` (bool) replaced by `json_format` (`json_object`, `json_schema`, `none`), migration 4 | LM Studio documents only `json_schema`, OpenAI prefers it, DeepSeek accepts only `json_object` (`docs/reports/providers.md`) |
| 2026-11-12 | 0.8 | Empty API key accepted for `http://127.0.0.1` and `http://localhost` URLs; then no `Authorization` header is sent | Ollama ignores the key, LM Studio needs none by default; remote URLs still require a key |

## Failed checks

Format: check, what was tried, what was seen, next step.

- none yet

## Measurements

Latest values of the targets in `docs/PLAN.md`.

| Metric | Target | Measured | Date |
| --- | --- | --- | --- |
| STT of a 10 s turn | ≤ 0.4 s | not measured yet | — |
