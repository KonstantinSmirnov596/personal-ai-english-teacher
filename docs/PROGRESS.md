# Progress log

Maintained by Claude Code. Read at the start of every session, updated after every closed plan item.

## State

- Current stage: 3
- Current item: stage 3 acceptance (`check_stage.ps1 3`)
- Last stage check: `check_stage.ps1 2` — exit 0, 2026-11-12 (fast 248, gpu 28, e2e 13, live skipped: no key)

## Plan items

Mark `[x]` only after the item's check passed.

### Stage 0

- [x] 0.1 Transfer
- [x] 0.2 Rename
- [x] 0.3 Environment
- [x] 0.4 Cleanup
- [x] 0.5 Predecessor suites under the new name
- [x] 0.6 Hardware facts
- [x] 0.7 License audit
- [x] 0.8 Provider templates
- [x] 0.9 Benchmarks under the new name

### Stage 1

- [x] 1.1 Language registry
- [x] 1.2 Window i18n
- [x] 1.3 Prompts with a language parameter
- [x] 1.4 `note_ru` → `note_l1`
- [x] 1.5 Language guard before TTS
- [x] 1.6 Scenarios
- [x] 1.7 Recurring-mistake keys
- [x] 1.8 Corrector sets
- [x] 1.9 Window behaviour
- [x] 1.10 Drop the Russian locale

### Stage 2

- [x] 2.1 Catalogs
- [x] 2.2 Insertion errors
- [x] 2.3 Reading phrases
- [x] 2.4 Accent fixtures
- [x] 2.5 Metrics per language
- [x] 2.6 Window

### Stage 3

- [x] 3.1 Hardware detector
- [x] 3.2 Profiles
- [x] 3.3 VRAM shortage
- [x] 3.4 Installer requirements check
- [x] 3.5 First-run wizard
- [x] 3.6 Unsupported screen
- [x] 3.7 Runtime warnings
- [x] 3.8 Profile acceptance

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
| 2026-11-12 | 0.5 | Launcher: uvicorn `timeout_graceful_shutdown=5` and an exit watchdog (`os._exit` 30 s after the core decided to exit, and after `main` returns) | The predecessor's log shows "window closed … exiting" at 23:24 while the process is still alive the next morning holding 3.9 GB of VRAM; a stuck worker thread or connection kept it alive |
| 2026-11-12 | 0.8 | Empty API key accepted for `http://127.0.0.1` and `http://localhost` URLs; then no `Authorization` header is sent | Ollama ignores the key, LM Studio needs none by default; remote URLs still require a key |
| 2026-11-12 | 1.1 | The Russian locale is dropped, not kept as a third language | SPEC 5 lets it stay only if cheaper than removal; keeping it would need its own mistake-key marks, scenarios titles, corrector set and pronunciation catalog in the new layout |
| 2026-11-12 | 1.1 | Setting `l1` stays empty until the user confirms a language; meanwhile the core uses the Windows-locale suggestion (`GET /api/languages` reports `confirmed`) | SPEC 5: the language is suggested by the Windows locale and confirmed in the first-run wizard (stage 3) |
| 2026-11-12 | 1.2 | `web/js/main.js` loads the strings before importing the views; `web/js/i18n.js` keeps one shared object `L` and replaces its contents in place on a switch, then the app re-renders; the panel relabels itself | Views alias sections at module level (`const R = L.connections`); in-place replacement keeps those aliases valid, so the switch needs no reload |
| 2026-11-12 | 1.2 | Language files are loaded with a dynamic `import()` by code from `GET /api/languages` | A third language needs files only (SPEC 5 "Extensibility") |
| 2026-11-12 | 1.3 | The tutor prompt is language-neutral ("Never use any language other than English") | Its byte-stable prefix keeps the provider's context cache across a language switch; only the corrector, summary and helpers need the learner language |
| 2026-11-12 | 1.3 | Every `_ru` field renamed `_l1` (not only `note_ru`): `message_l1`, `tip_l1`, `title_l1`, `translation_l1`, `explanation_l1`, `prompt_l1`, `text_l1`, `hint_l1`, `scenario_title_l1`; translation helper answers `{translation}`; summary phrases `translation_l1` | One naming rule for learner-language text; SPEC names `note_l1` explicitly |
| 2026-11-12 | 1.4 | Migration 5 renames the columns (`ALTER TABLE … RENAME COLUMN`), adds `session.l1` and per-language titles of built-in scenarios (`title_l10n`, `description_l10n`); built-ins missing from the data file are deleted at start | Data of existing databases is kept (test `test_migration_note_l1`); removed scenarios (ERP/ECM) disappear |
| 2026-11-12 | 1.5 | Language guard: frequent learner-language words that are not English homographs, plus lower-case words with Iberian letters (ñ ã õ ç á í ó ú â ê ô à ü, not é); names (capitalized mid-sentence) and particles between names are ignored; "a", "no", "me", "do", "as" count for neither side; any non-Latin letter is also "not English" | Must never block English with Spanish/Portuguese names (38 test sentences) while catching learner text; é is left out because of café, résumé |
| 2026-11-12 | 1.5 | The i18n language check requires ≥ 85 % of long UI strings to be recognized as their own language and none as the other | The guard is tuned for no false positives on English, so it misses some short sentences without function words |
| 2026-11-12 | 1.7 | Mistake keys exactly as SPEC 12: 12 new keys plus 15 kept; the predecessor's other 17 keys are retired; old database rows with retired keys are hidden, not deleted | SPEC 12 table; history of a user's earlier sessions is not destroyed |
| 2026-11-12 | 1.8 | `live` budget: at most 80 requests per learner language (40 cases with one retry) | SPEC: live suite for both languages; the predecessor's budget was 80 per run |
| 2026-11-12 | 1.10 | The Russian pronunciation catalog stays until item 2.1 (only file left in the Cyrillic allowlist); fonts keep only the Latin subsets | SPEC puts the es/pt catalogs in stage 2; Cyrillic glyphs are no longer needed |
| 2026-11-12 | 2.1 | Catalog format extended: `detect: insertion` with `insert {where, sounds}`, `expected: "*"` (any consonant allowed by the position), `expected_map` for two-way confusions, multi-sound heard keys (`ɛɾ`, `ɪd`); new positions `s_cluster`, `word_final_obstruent`, `word_final_cluster`, `ed_suffix`, `before_high_front_vowel`, `coda`, `word_initial` | SPEC 12 entries need them (espeak, bigi, worked, party, feel) |
| 2026-11-12 | 2.1 | Default levels: error for clear meaning-changing mistakes; close for z devoicing (final /z/ is partly devoiced by native speakers too), h → x, schwa, short /ʊ/, final consonant drop, w → gw, final l, final m | Same rule as the predecessor: close-level entries never show as errors in conversation |
| 2026-11-12 | 2.2 | Insertions are catalog-driven competitors (inserted sound + expected sound as one variant) added only at the entry's positions; displayed as `+ɛ`; the -ed suffix is modelled as a substitution t → ɪd/ɛd/əd | SPEC 12 "Insertion": same CTC likelihood ratio, insertions only where the catalog says |
| 2026-11-12 | 2.2 | The reference carries the learner language (`RefPhone.lang`, `build_reference(words, lang)`); `catalog.match` reads that language's catalog | No language argument threaded through judge/build_result; a reference is always built for one language |
| 2026-11-12 | 2.3 | One shared set of 30 reading phrases for both languages; targets computed from both catalogs | Coverage of ≥ 2 phrases per automatic entry holds for both languages (SPEC allows shared or per-language) |
| 2026-11-12 | 2.4 | Accent fixtures through misaki's inline override `[word](/phonemes/)`; the synthesis guard checks the override's word, not its IPA | Kokoro's vocabulary has the needed symbols (x, r, ɾ, ʝ, β, combining tilde); IPA letters such as θ, ˈ, ᵊ are not a learner language |
| 2026-11-12 | 2.5 | Evaluation: the target phone is where the catalog entry applies in the expected word; "named" = the judged entry and one of the pair's `names`; the 80 % "error" metric over error-level entries, close-level entries reported separately | Pseudo-words ("espeak") are not reliable espeak input; an American phoneme model names a tap /t, d/ and an inserted vowel /ə/ |
| 2026-11-12 | 2.5 | Conversation fixture "very" → "video" with /b/, reading fixture "estart" + "tird" | In conversation only confidently recognized words are assessed with a strict margin (LLR ≥ 4); "berry" for "very" stayed below it, "video" with /b/ gives LLR 6.3 for two voices; "tink" after "I" was too weak, "tird" gives LLR 9 |
| 2026-11-12 | 3.1 | GPU facts from `nvidia-smi` (installed with the driver), RAM and power through Win32 `ctypes` calls; no NVML binding package | No new dependency or license; the same query works in the installer (PowerShell) and in the core. `driver_version` is kept although driver 610.47 marks it deprecated (`kmd_version`): older drivers know only `driver_version` |
| 2026-11-12 | 3.2 | Before the wizard measured anything, the start-up profile is estimated from total video memory (≥ 7600 MiB → `completo`, ≥ 5800 MiB → `compacto`); the wizard and Settings → Performance use the SPEC 7 free-memory thresholds | A game left open at start-up would otherwise lock the app as unsupported; SPEC 7 assigns the measurement to the wizard |
| 2026-11-12 | 3.2 | Free memory counts the memory held by the app's own models (free before loading minus free now) | SPEC 7 thresholds describe what the desktop and other programs leave; measured with the models loaded, the app would otherwise compete with itself |
| 2026-11-12 | 3.2 | A supported card with only too little free memory is not "unsupported": the wizard explains it, lets the user continue, and the benchmark stores `compacto` | Free memory changes when programs close; only the GPU, driver and architecture are hard limits |
| 2026-11-12 | 3.2 | `pron_in_conversation` follows the profile (on in `completo`, off in `compacto`) until the user sets it | SPEC 7: marks off by default in `compacto`; an explicit user choice must win |
| 2026-11-12 | 3.2 | A profile switch reloads STT on the GPU queue; `SpeechRecognizer.load()` reloads when its compute type changed | Switching while the models load could leave STT on the old compute type |
| 2026-11-12 | 3.3 | Out-of-memory in the pronunciation route answers `vram_low` like recognition does | The same cause deserves the same advice (close other programs) |
| 2026-11-12 | 3.4 | Installer messages live in `scripts/requirements.messages.json` (en, es, pt-BR), the script stays ASCII; the language follows the Windows UI culture (es-* → es, pt-* → pt-BR, otherwise English) | Windows PowerShell 5.1 reads a script without BOM in the ANSI code page; the installer runs before any learner-language choice, so English is the third option |
| 2026-11-12 | 3.4 | `setup.ps1 -NoHardwareCheck` skips the requirements check | Developer machines and CI without an NVIDIA GPU still need the Python environment; the app checks the hardware at every start anyway, so this is not a bypass of a security check |
| 2026-11-12 | 3.4 | Disk need: 5.5 GB next to the app plus 10 GB in local app data (15.5 GB on one drive); less when an earlier installation exists | Measured: environment 4.9 GB, models 3.1 GB, uv cache 4.9 GB, plus 2 GB for run-time data; SPEC 7 says 15 GB |
| 2026-11-12 | 3.5 | The wizard does not download models: it lists missing ones, sends the user to `install.cmd` and then loads them (`POST /api/models/load`) | Contradiction: SPEC 7 step 3 asks for a download in the wizard; CLAUDE.md hard constraints allow downloads only at install time and run-time traffic only to the LLM. The hard constraint wins; resume and checksums move to `install.cmd` (stage 4) |
| 2026-11-12 | 3.5 | Microphone check: median level of 3 s silence and 90th percentile of 4 s speech, raw microphone; room quiet (< 25 of 100, about −45 dBFS) → detector threshold 0.5 and noise suppression off; moderate (25–40) → 0.6, on; noisy (> 40) → 0.7, on | SPEC 7 asks the noise level to set the detector threshold and the noise-suppression default; a quiet room keeps the raw signal, which preserves the consonants the pronunciation check listens for. 0.5 was the predecessor's fixed value (vad-web's own default is 0.3) |
| 2026-11-12 | 3.5 | The LLM step saves a connection only after a successful test; the key field is cleared and never shown | SPEC 7: the key is checked at once; a failed key should not become the active connection |
| 2026-11-12 | 3.5 | First run hides the section navigation until the wizard ends; a re-run from Settings keeps it | A first-run user should not wander off with nothing configured; a returning user should not be trapped |
| 2026-11-12 | 3.5 | `/api/health` reports `ok` only after the warm-up calls | The benchmark queued behind the warm-up and measured 1.3 s for the first sentence instead of 0.08 s, which would have lowered `completo` wrongly |
| 2026-11-12 | 3.7 | Battery and changed-hardware notices are kept in the core's memory and dismissed once per run; the earlier `battery_notice_shown` setting is removed | A battery notice that never comes back after the first time would miss later battery sessions |
| 2026-11-12 | 3.6 | The unsupported window check runs a core with a fake detector inside the test process (uvicorn in a thread) and opens it in Edge | The real launcher has no switch for fake hardware, and must not get one (no test back doors) |
| 2026-11-12 | 3.8 | Tests take `--vt-profile`; the profile is stored in the test's data directory before a launcher starts (as a user choice), directly built recognizers get the profile's compute type | SPEC 7: both profiles pass `gpu` and `e2e`; the app reads no flag for this |
| 2026-11-12 | 3.8 | Core peak memory = device `memory.used` minus the value before the core started, sampled every 200 ms | Windows WDDM reports no per-process memory in `nvidia-smi` (`[N/A]`) |

## Failed checks

Format: check, what was tried, what was seen, next step.

- `live` suite (both languages): skipped, no saved key. Next: owner runs `scripts\test.ps1 live` after entering a key in the app.
- `e2e`, stage 3: `test_reading_marks_sounds_and_accepts_feedback` failed once in a full run ("start" marked close instead of error) and passed when rerun alone. Timing-sensitive with the looping fake microphone. Next: watch it in acceptance runs.
- `e2e` flaky while the predecessor's windowless core holds 3.9 GB of VRAM (owner's process outside the project). Tried: rerunning single tests (they pass alone), full suite three times (one, three and zero failures). Seen: 60 s Playwright timeouts waiting for the tutor's first audio when VRAM is oversubscribed. Next: owner decides whether that process may be stopped (HUMAN_TASKS); stage 3 VRAM measurements need a free GPU.

## Measurements

Latest values of the targets in `docs/PLAN.md`.

| Metric | Target | Measured | Date |
| --- | --- | --- | --- |
| STT of a 10 s turn | ≤ 0.4 s | 0.299 s (warm median) | 2026-11-12 |
| TTS first sentence | ≤ 0.3 s | 0.086 s (warm median) | 2026-11-12 |
| End of turn → first audio, mock 0 ms | ≤ 0.9 s | 0.399 s (median), 0.402 s max | 2026-11-12 |
| End of turn → first audio, mock 500 ms | ≤ 1.5 s | 0.907 s (median), 0.925 s max | 2026-11-12 |
| VRAM, all three models | ≤ 6.5 GB | 3.56 GB device-wide delta (lower bound: another process held VRAM) | 2026-11-12 |
| WER TTS → STT loop | ≤ 10 % | 0.0 % | 2026-11-12 |
| Startup to models ready | ≤ 20 s | 15.1–15.9 s (window 2.2 s) | 2026-11-12 |
| Outbound connections | only the LLM host | 0 outside 127.0.0.1 | 2026-11-12 |
| i18n completeness es-419 / pt-BR | 100 % | 100 % / 100 % (267 keys) | 2026-11-12 |
| End of turn → first audio, mock 0 ms (stage 1) | ≤ 0.9 s | 0.396 s median | 2026-11-12 |
| End of turn → first audio, mock 500 ms (stage 1) | ≤ 1.5 s | 0.908 s median | 2026-11-12 |
| Live corrector quality, both languages | `docs/testing.md` thresholds | not run: no key | — |
| Pronunciation false "error", es-419 / pt-BR | ≤ 3 % | 0.00 % / 0.00 % (0 of 2361 each) | 2026-11-12 |
| Catalog mistakes flagged "error", es-419 / pt-BR | ≥ 80 % | 91.8 % / 87.9 % | 2026-11-12 |
| Heard sound named, es-419 / pt-BR | ≥ 60 % | 93.1 % / 88.1 % | 2026-11-12 |
| Core peak video memory, `compacto` (10 turns + 5 readings) | ≤ 5.0 GB | 2.48 GB (`completo`: 3.69 GB) | 2026-11-12 |
| End of turn → first audio, mock 0 ms, `completo` / `compacto` | ≤ 0.9 s | 0.414 s / 0.401 s median | 2026-11-12 |
| End of turn → first audio, mock 500 ms, `completo` / `compacto` | ≤ 1.5 s | 0.933 s / 0.907 s median | 2026-11-12 |
| STT of a 10 s phrase, `completo` / `compacto` | ≤ 0.4 s | 0.326 s / 0.313 s | 2026-11-12 |
| WER TTS → STT loop, `completo` / `compacto` | ≤ 10 %, delta ≤ 2 pp | 0.0 % / 0.0 % | 2026-11-12 |
| Wizard benchmark, first audio without LLM | ≤ 1.2 s keeps `completo` | 0.39–0.41 s | 2026-11-12 |
