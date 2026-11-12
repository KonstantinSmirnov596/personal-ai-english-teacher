# Stage 3 report: hardware

## Result

Stage 3 makes the app aware of the computer it runs on. The installer checks the requirements before downloading anything; the core detects the GPU at every start, picks the `completo` or `compacto` profile, refuses to load models on unsupported hardware and explains why; a first-run wizard with eight steps measures this GPU and sets the microphone, voice, LLM connection and level; video-memory shortages produce a clear message instead of a crash. Both profiles pass the `gpu` and `e2e` suites and the latency targets; `compacto` stays at 2.5 GB of video memory at its peak (limit 5.0 GB).

Acceptance: `scripts/check_stage.ps1 3` runs `fast`, `gpu`, `e2e`, `gpu@compacto`, `e2e@compacto` (the suites under the `compacto` profile, `tests/profile_opt.py`), the required tests of items 3.1–3.8 and `scripts/bench_profiles.py`. It exited with 0 on 2026-11-12 from a clean worktree of commit `7a1f328`: fast 291, gpu 29, e2e 18, gpu@compacto 29, e2e@compacto 18 passed; `live` skipped (no saved key).

## Requirements and their sources

| Requirement | Value | Blocking | Source |
| --- | --- | --- | --- |
| NVIDIA GPU | present (`nvidia-smi`, installed with the driver) | yes | The models run on CUDA (stage 0) |
| Driver | ≥ 572.61 | yes | [CUDA release notes, "Corresponding Driver Versions"](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html): CUDA 12.8 Update 1 ≥ 572.61; CTranslate2 4.9.0 is built with 12.8.1 (`docs/reports/stage0.md`) |
| Compute capability | ≥ 7.5 (Turing) | yes | torch 2.11.0 `cu128` wheel: sm_75 … sm_120; CTranslate2 4.9.0: sm_75 and PTX 8.6 (`docs/reports/stage0.md`) |
| Video memory | installer: ≥ 5800 MiB total (a 6 GB card); wizard: ≥ 5 GB free for `compacto`, ≥ 7 GB free for `completo` | yes | SPEC 7 thresholds |
| RAM | ≥ 15000 MB visible (16 GB installed) | warning | SPEC 7 |
| Disk | installer: about 15 GB (5.5 GB next to the app, 10 GB in local app data, measured: environment 4.9 GB, models 3.1 GB, uv cache 4.9 GB); run time: 2 GB free | installer: yes; run time: warning | Measured on the development machine |
| Power | mains | warning | SPEC 7 |
| Windows | build ≥ 19045 (Windows 10 22H2) | warning | SPEC 7 |

`nvidia-smi --help-query-gpu` on driver 610.47 marks `driver_version` as deprecated in favour of `kmd_version`; both the installer and the core keep `driver_version`, which still answers on 610.47 and is the only one older drivers know.

## Measurements

Development machine: RTX 5060 Laptop GPU 8 GB, driver 610.47. Raw data: `docs/reports/data/bench_profiles.json` (`scripts/bench_profiles.py`, the run inside the acceptance check, 2026-11-12). Full scenario per profile: launcher with a fresh data directory and the profile stored as a user choice, 10 conversation turns with the mock LLM (5 at 0 ms, 5 at 500 ms first chunk), then 5 "Reading" phrases; `nvidia-smi` sampled every 200 ms.

| Metric | Target | `completo` | `compacto` |
| --- | --- | --- | --- |
| Peak video memory of the core (device used minus before start) | `compacto` ≤ 5.0 GB | 3.69 GB | 2.48 GB |
| Video memory after loading (STT + TTS, warm) | — | 2.76 GB | 1.77 GB |
| End of turn → first audio, mock 0 ms (client, median of 5) | ≤ 0.9 s | 0.482 s | 0.476 s |
| End of turn → first audio, mock 500 ms (client, median of 5) | ≤ 1.5 s | 0.993 s | 0.994 s |
| STT of a 10.1 s phrase (warm median of 5) | ≤ 0.4 s | 0.367 s | 0.323 s |
| WER of the TTS → STT loop (10 phrases) | ≤ 10 %, `compacto` ≤ `completo` + 2 pp | 0.0 % | 0.0 % |
| Reading round trip of 5 phrases | — | 57–100 ms | 2066 ms first (model loads on demand), then 64–72 ms |
| Pronunciation marks in the conversation | — | on | off (SPEC 7 default) |

The first turn of each 0 ms series is slower (first sentence of a new session); the medians are steady state. An earlier run on a quieter machine measured 0.41 / 0.93 s (`completo`) and 0.40 / 0.91 s (`compacto`). The baseline before each start was 0 MiB: the predecessor's idle process that held 2.5 GB earlier in the day had been paged out of video memory by Windows, so the peaks are the core's own usage.

Wizard benchmark (step 4) on the same machine, after a fix described below: recognition of a 7 s phrase 0.30 s, first sentence 0.08–0.11 s, pronunciation check 0.05–0.28 s, first audio without the LLM 0.39–0.41 s. With the predecessor's process still resident (2.5 GB), the measured free memory was 5.2 GB and the wizard chose `compacto`, as SPEC 7 requires.

## Items

| Item | What was built | Check |
| --- | --- | --- |
| 3.1 Hardware detector | `voicetutor/hardware.py`: `nvidia-smi` query (name, memory total and free, driver, compute capability), RAM through `GlobalMemoryStatusEx`, power through `GetSystemPowerStatus`, free disk of the data directory, Windows build; `HardwareDetector` protocol injected into `Core(detector=…)`; the compute device is set in one place (`COMPUTE_DEVICE`) | `tests/test_hardware.py` (fake detectors; the real detector on this machine) |
| 3.2 Profiles | `voicetutor/profiles.py`: per-item checks with numbers for the window, `completo` / `compacto` / unsupported; STT `float16` or `int8_float16`; phoneme model kept or unloaded after 5 minutes idle; conversation marks follow the profile until the user sets them; Settings → Performance with automatic, `completo`, `compacto`; switching reloads STT on the GPU queue | `tests/test_profiles.py`; `gpu` and `e2e` suites under both profiles |
| 3.3 Video memory shortage | Out-of-memory in recognition frees the phoneme model and retries once, then answers `vram_low` (conversation, exercises, pronunciation route); the phoneme model also frees itself below 400 MB free | Fast tests with an injected recognizer that raises out-of-memory; `tests/gpu/test_vram.py` |
| 3.4 Installer requirements check | `scripts/requirements.ps1` (Windows PowerShell 5.1 compatible, ASCII) with messages in English, Spanish and Portuguese in `scripts/requirements.messages.json`; `setup.ps1` runs it first and stops before any download; `-NoHardwareCheck` for developer machines and CI | `tests/test_requirements_ps1.py`: 13 fake computers, the three languages, the doc links, the real facts of this machine, the order in `setup.ps1` |
| 3.5 First-run wizard | `web/js/wizard.js`: language, hardware, models, benchmark, microphone (3 s of silence and a phrase set the voice detector threshold and noise suppression), sound and voice with the headphones question, LLM connection (templates, local-model warning, key checked before saving, skip), level with descriptions; opens while `wizard_done` is false; each step reachable from the stepper and from Settings → Performance; results in table `hardware_profile` | `tests/e2e/test_wizard.py` in Spanish and in Portuguese, each on a fresh data directory |
| 3.6 Unsupported screen | The core loads no model on unsupported hardware, `/api/health` names `unsupported_hardware`; the wizard's hardware step lists every failed item with what to do and `docs/<lang>/hardware.md#<item>`; the conversation screen links to it | `tests/test_unsupported.py` (core with a fake detector); `tests/e2e/test_unsupported_window.py` (that core in Edge: no GPU, old driver, Pascal card; both languages) |
| 3.7 Run-time notices | `on_battery` and `hardware_changed` (GPU or driver differ from the stored measurement) in `hello.hardware.notices`, a banner with "check and measure" for the latter, dismissed once per run | `tests/test_hardware.py` |
| 3.8 Profile acceptance | `scripts/bench_profiles.py` | This report; exit code 0 |

User documentation `docs/en/hardware.md`, `docs/es/hardware.md`, `docs/pt-BR/hardware.md` explains every check under the anchor the wizard and the installer link to (`tests/test_user_docs.py` keeps the three in step).

## Video memory pressure on Windows

`tests/gpu/test_vram.py` fills the GPU from the test process until 149 MB stay free while the core runs. Both the pronunciation check (which loads the phoneme model) and a conversation turn still succeeded: since driver 536.40 the Windows driver lets CUDA allocations fall back to shared system memory when video memory is exhausted, and a later driver added the "CUDA - Sysmem Fallback Policy" setting to turn this off ([NVIDIA support article 5490](https://nvidia.custhelp.com/app/answers/detail/a_id/5490/~/system-memory-fallback-for-stable-diffusion)). Every supported driver (≥ 572.61) has it, so on Windows a shortage usually means a slower app, not an error. The `vram_low` path stays for users who disable the fallback; it is covered by the fast tests with an injected out-of-memory error. After the memory was released, the core worked normally again.

## Problems found and fixed during the stage

- **Readiness before warm-up.** `/api/health` reported `ok` as soon as both models were loaded, before the warm-up calls ran. The wizard's benchmark then queued behind the warm-up on the single GPU thread and measured 1.3–1.4 s for the first sentence instead of 0.08 s, which would have lowered `completo` to `compacto` wrongly. Readiness now waits for the warm-up (`ModelStatus.warm`).
- **The core's own memory.** The free-memory threshold has to count the memory the app's own models hold (SPEC 7 talks about what the desktop and other programs leave). The first version counted only STT and TTS; the phoneme model, loaded on demand, was missed. The count is now "free before loading minus free now".
- **Profile switch during loading.** Switching the profile while the models loaded could leave STT on the old compute type. The recognizer now reloads when its compute type changed, and the switch is queued on the GPU thread behind any load.
- **Problems hidden by the missing connection.** On a first start without an LLM connection, the conversation screen showed only "no API connection" and hid the hardware problem. Hardware and model problems now come first.
- **`/api/health` imported torch on the event loop.** It now reads `torch` only once the GPU thread has imported it, and never on unsupported hardware.

## Deviations and decisions

Recorded with reasons in `docs/PROGRESS.md` → Decisions. The main ones:

- **No model download in the app.** SPEC 7 step 3 asks the wizard to download missing models; CLAUDE.md's hard constraints say models are downloaded only at install time and the only run-time traffic goes to the LLM. The hard constraint wins: the wizard lists missing models, sends the user to `install.cmd` (which resumes and verifies downloads, stage 4) and then loads the models without a restart (`POST /api/models/load`).
- **Start-up estimate from total memory.** Before the wizard measured anything, the core picks the profile from the card's total memory, so a game left open at start does not lock the app; the wizard measures free memory as SPEC 7 says. When only free memory is short on a supported card, the wizard explains it and the benchmark stores `compacto`.
- **Per-process memory.** Windows (WDDM) reports no per-process memory in `nvidia-smi`; the core's peak is the device's used memory minus the value before the core started.

## Not done or limited

- The wizard e2e runs on the real GPU of this machine only; a second machine with a 6 GB card (HUMAN_TASKS) would confirm the `compacto` choice from a real measurement.
- The reading e2e test failed in several full runs before the fix: the old fixture's inserted vowel ("estart") scored 1.4–4.2 nats through Edge's microphone path against the 2.0 error margin. The fixture now says "es-TART" (7.0 nats) and recordings start right after a phrase of the looping microphone; the check is unchanged.
- Two acceptance attempts were invalid for reasons outside the app: fast tests run in parallel deleted the e2e core's test key (fixed: one credential service per test session), and junctions to `web/fonts` and `web/vendor` in the acceptance worktree are refused by the static file server (fixed: real copies).
- The installer's requirements check is tested with fake facts and on this machine; `install.cmd`, the uv bootstrap and model checksums are stage 4.

## Needed from the owner

- Whether the predecessor's windowless core (`pythonw -m trainer.launcher`, started 2026-11-11 22:12) may be stopped: it competes for video memory and makes the wizard choose `compacto` on this machine (question in `docs/HUMAN_TASKS.md`).
- Proofreading of the new Spanish and Portuguese texts: the wizard and Settings → Performance in `web/i18n/*.js`, the installer messages in `scripts/requirements.messages.json`, and `docs/es/hardware.md`, `docs/pt-BR/hardware.md`.
