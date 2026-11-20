# Progress log

Maintained by Claude Code. Read at the start of every session, updated after every closed plan item.

## State

- Current stage: done (stages 0–4 accepted); first publication approved by the owner on 2026-11-20 (repository and release v0.1.0)
- Current item: none open; owner tasks in `docs/HUMAN_TASKS.md`
- Last stage check: `check_stage.ps1 4` — exit 0, 2026-11-12, clean worktree of `554066c` with its own environment (repeated setup OK; fast 328, gpu 29, e2e 20, gpu@compacto 29, e2e@compacto 20; profile benchmark, `ci_local.ps1` and the clean install from the release archive passed; live skipped: no key)

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

- [x] 4.1 Installer
- [x] 4.2 Release packaging
- [x] 4.3 Privacy hardening
- [x] 4.4 Documentation
- [x] 4.5 Screenshots
- [x] 4.6 GitHub files
- [x] 4.7 Diagnostics
- [x] 4.8 Final regression

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
| 2026-11-12 | 3.8 | Test sessions and bench scripts use their own credential service `VoiceTutor-test-<pid>`; a session-end fixture sweeps it | The first stage 3 acceptance run failed in `e2e@compacto` with "Authentication Fails": fast tests run in parallel deleted `connection-1..10` of the shared `VoiceTutor-test` service, i.e. the running e2e core's key |
| 2026-11-12 | 3.8 | Stage 3 acceptance is rerun from a clean git worktree of the commit (junctions to `.venv`, `web/fonts`, `web/vendor`) while stage 4 continues in the main tree | The acceptance run must see the committed stage 3 state, not stage 4 work in progress |
| 2026-11-12 | 4.1 | uv 0.13.7 from its GitHub release, SHA-256 `0cdc5b38…e021` pinned in `scripts/installer.ps1`; Python through `uv python install 3.12 --no-bin --no-registry` into `.tools\python`; package cache in `.tools\uv-cache` unless `UV_CACHE_DIR` is set | No system Python; nothing outside the app folder except data; the digest matches both the release's `.sha256` file and the GitHub API; uv verifies Python downloads against SHA-256s it ships (`HashMismatch` in `crates/uv-python-managed/src/downloads.rs` at 0.13.7) |
| 2026-11-12 | 4.1 | Models are downloaded by the app's own installer step (`voicetutor/model_download.py`) from `huggingface.co/<repo>/resolve/<commit>/<file>`, resumed with HTTP Range, checked against `voicetutor/data/model_files.json`; the app resolves models from `<models>/<key>/<commit>` first and an older Hugging Face cache second | huggingface_hub gives no SHA-256 check of our own and resume could not be tested without network; the manifest hashes are cross-checked against the LFS SHA-256 and git blob SHA-1 Hugging Face publishes for the pinned commits; a verified file in an old cache is hard-linked instead of downloaded again |
| 2026-11-12 | 4.1 | Accented app folders: espeak-ng gets the 8.3 short path through its own `ESPEAK_DATA_PATH`, and `espeakng_loader.get_data_path()` returns `None` so phonemizer passes no path (`voicetutor/espeak_path.py`); the installer refuses a folder without an ASCII short name, longer than 80 characters (without long paths) or not writable | Measured: espeak-ng fails with any non-ASCII data path (it uses the ANSI file API) and phonemizer expands short names with `Path.resolve()`; CTranslate2 loads models from accented paths fine; the deepest file in `.venv` is 138 characters below it |
| 2026-11-12 | 4.1 | The clean-install check installs the release archive into a folder with spaces and accents with empty `LOCALAPPDATA`/`TEMP`, but without a Mark of the Web; resume after an interrupted download is tested with a local server (`tests/test_model_download.py`) | Writing `Zone.Identifier` streams and force-killing the installer tree were refused by the session's safety classifier; a run from a browser-downloaded archive is an owner task in HUMAN_TASKS |
| 2026-11-12 | 4.1 | `uninstall.cmd` removes `.venv`, `.tools`, downloaded window assets and the shortcuts that point to this app; data and keys only after a separate "yes" | SPEC: user data only after confirmation; keys need the app's Python, so they are deleted before the environment |
| 2026-11-12 | 4.3 | Conversation text is logged only through the `voicetutor.turns` logger and only with Settings → Data → "Detailed log" (warning shown); diagnostics drop that logger's lines | SPEC: no turn text in logs by default; a bug report sometimes needs the text, and then the user decides |
| 2026-11-12 | 4.4 | Token estimate from a mock session (`scripts/token_usage.py`) with DeepSeek's 0.3 tokens per English character: tutor 850 → 1300 input tokens over 10 answers, correction about 1450, summary about 1000; output given as the `max_tokens` bound | The mock's answers say nothing about real output lengths; prices are left to the provider's page |
| 2026-11-12 | 4.6 | CI runs on `windows-latest` with `setup.ps1 -NoHardwareCheck -SkipModels`, then `ci_local.ps1`; `actions/checkout` pinned to the v7.0.1 commit `3d3c42e5…`; no secrets | GitHub runners have no NVIDIA GPU; gpu and e2e run locally in `check_release.ps1` |
| 2026-11-12 | 4.7 | Diagnostics are built in Python (`voicetutor/diagnostics.py`): saved keys are read from the Credential Manager only to remove exact matches, plus key-like patterns; the Windows user name in paths becomes `<user>` | The strongest guarantee that a key cannot slip through a pattern |
| 2026-11-12 | 3.8 | Reading fixture "estart" → "es-TART" (`[start](/ɛsˈtɑɹt/)`); e2e recordings are armed right after a phrase ended; generated fixtures are rebuilt when their spec changes | The reading e2e test failed in 3 of 6 full runs: the old fixture's inserted vowel scored 1.4–4.2 nats through Edge's microphone path against the 2.0 error margin (3.3 on the file itself); "es-TART" scores 7.0. Waiting for any 1 s of silence could also end just before the looping file restarted. The check is unchanged: both words must be errors |
| 2026-11-12 | 4.1 | Shortcuts are written and read through `IShellLinkW` (`scripts/shortcut.ps1`, a C# helper loaded with `Add-Type`) instead of `WScript.Shell` | The clean install into "José Ñ" failed: WScript.Shell goes through the ANSI code page, could not save the shortcut and reported its target mangled |
| 2026-11-12 | 4.1 | `setup.ps1` installs the test tools only with `-Dev` (CI, developers); `install.cmd` runs `uv sync --no-dev` | Users do not need pytest, ruff or Playwright |
| 2026-11-12 | 4.1 | The `.cmd` wrappers clear `PSModulePath`; the installer hashes, downloads and unzips through .NET | Windows PowerShell started from a PowerShell 7 terminal inherited PS7's module path and could not load `Get-FileHash` |
| 2026-11-12 | 4.1 | `.gitattributes` keeps CRLF for `.cmd`, `.bat`, `.ps1` | `* text=auto eol=lf` would give batch files LF endings on checkout, which cmd.exe can misread |
| 2026-11-12 | 4.5 | Of two neighbouring insertions "added after" and "added before" (the same vowel between two words) only the one with the larger margin is reported | The Portuguese README screenshot showed a false mark on "should" before "es-TART"; the stage 2 metrics of both languages are unchanged |
| 2026-11-12 | 4.8 | `check_stage.ps1` runs the developer setup (`-Dev -Shortcuts no -NoLaunch`); the acceptance worktree builds its own environment from the package cache instead of a junction to the main `.venv` | The first stage 4 run used the user setup, which rebuilt `.venv` without test tools through the junction (the main environment was rebuilt with `setup.ps1 -Dev`) and would have created Desktop shortcuts |
| 2026-11-20 | publication | Product name "Personal AI English Teacher" (window title, UI, shortcut, docs); the full title "Personal AI English Teacher (ES/PT) for Desktop/Notebook with GPU" for the README heading, the repository description and the release; internal identifiers (`voicetutor`, `%LOCALAPPDATA%\VoiceTutor`, keyring service, `VOICETUTOR_*`) unchanged | Owner's answer; renaming internal identifiers would move users' data and keys for no gain |
| 2026-11-20 | publication | Release archive and suggested folder `EnglishTeacher-<version>` | Explorer extracts into a folder named after the archive; a short name keeps the nested path under the installer's 80-character limit |
| 2026-11-20 | publication | License MIT, "Copyright (c) 2026 Konstantin Smirnov"; GPL components listed in `THIRD_PARTY_NOTICES.md` | Owner left the license to Claude Code and accepted the default on the GPL question; MIT gives users and contributors the widest permission; the GPL components are installed from PyPI on the user's machine and never shipped |
| 2026-11-20 | publication | `docs/SPEC.md` and `docs/BASELINE_REPORT.md` tracked; the hygiene test allows Cyrillic only in these two files and still forbids `CLAUDE.local.md`; the release archive keeps excluding them | Owner's answer; users do not need the Russian brief in the archive |
| 2026-11-20 | publication | Before the first push all commits are rewritten to author and committer `Konstantin Smirnov <GitHub noreply address>` with dates kept and the Claude co-author trailer; branch `master` renamed to `main` | Owner's answer; the personal e-mail address must not reach the public history; CI triggers on `main` |
| 2026-11-20 | publication | v0.1.0 is published as a pre-release | Texts not proofread by native speakers, `live` suite not run, only one GPU tested |
| 2026-11-20 | publication | The hygiene rule for profile paths requires a folder name after `Users\` (`test_user_path_pattern` checks both sides) | The published brief quotes the bare prefix when it describes this check; a prefix without a name is not personal data, and every real profile path still matches |

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
| End of turn → first audio, mock 0 ms, `completo` / `compacto` | ≤ 0.9 s | 0.482 s / 0.476 s median (acceptance run) | 2026-11-12 |
| End of turn → first audio, mock 500 ms, `completo` / `compacto` | ≤ 1.5 s | 0.993 s / 0.994 s median (acceptance run) | 2026-11-12 |
| STT of a 10 s phrase, `completo` / `compacto` | ≤ 0.4 s | 0.367 s / 0.323 s (acceptance run) | 2026-11-12 |
| WER TTS → STT loop, `completo` / `compacto` | ≤ 10 %, delta ≤ 2 pp | 0.0 % / 0.0 % | 2026-11-12 |
| Wizard benchmark, first audio without LLM | ≤ 1.2 s keeps `completo` | 0.39–0.41 s | 2026-11-12 |
| Clean install from the release archive (accented folder, empty LOCALAPPDATA/TEMP) | passes | passed: 241 s with cached packages, about 5 min with all downloads; app start, speech, reading, uninstall | 2026-11-12 |
| Release archive | no models, environment or binaries | 0.5 MB, `SHA256SUMS.txt` | 2026-11-12 |
| Input tokens per answer (mock, 0.3 tokens/char) | measured | tutor 850 → 1300 over 10 answers, correction about 1450; session about 26,000 | 2026-11-12 |
| `ci_local.ps1` | green | green: ruff clean, 326 fast tests | 2026-11-12 |
