# Final report: Voice Tutor 0.1.0

## Result

Voice Tutor is an open-source Windows desktop app for practicing spoken American English, for learners who speak Latin American Spanish (`es-419`) or Brazilian Portuguese (`pt-BR`). The tutor speaks only General American English; corrections, translations, hints and tips come in the learner's language. Speech recognition, speech synthesis and pronunciation assessment run on the user's NVIDIA GPU; only dialogue text goes to the LLM provider the user picks.

All five stages of `docs/PLAN.md` are done. Stages 0–3 were accepted by `scripts/check_stage.ps1 <N>` (exit 0); the stage 4 acceptance run is recorded in `docs/PROGRESS.md` ("State"). Nothing is published: the work is in the local git repository, and publishing is the owner's decision (`docs/HUMAN_TASKS.md`, "Before publication").

## Stages

| Stage | What it delivered | Report |
| --- | --- | --- |
| 0 | The predecessor's code under the new name, a pinned environment, hardware facts, license audit, provider templates, baseline benchmarks | `stage0.md`, `licenses.md`, `providers.md` |
| 1 | Learner languages as files (Spanish, Portuguese); window and core messages in both; a language guard before speech synthesis | `stage1.md` |
| 2 | Pronunciation catalogs per learner language (20 typical mistakes each), inserted sounds, 30 reading phrases, metrics per language | `stage2.md` |
| 3 | Hardware detection, `completo` / `compacto` profiles, first-run wizard, unsupported screen, video-memory shortage handling, installer requirements check | `stage3.md` |
| 4 | Installer without system Python, release archive, privacy hardening, documentation in three languages, screenshots, GitHub files, diagnostics | this report |

## Targets and measurements

Development machine: RTX 5060 Laptop GPU 8 GB, driver 610.47, 16 GB RAM, Windows 11. Raw data in `docs/reports/data/`.

| Metric | Target | Measured |
| --- | --- | --- |
| STT of a 10 s turn | ≤ 0.4 s | 0.30 s (stage 0); 0.37 s `completo`, 0.32 s `compacto` in the stage 3 acceptance run |
| TTS first sentence | ≤ 0.3 s | 0.086 s |
| End of turn → first audio, mock LLM 0 ms | ≤ 0.9 s | 0.40–0.48 s median (stages 0, 1, 3, both profiles) |
| End of turn → first audio, mock LLM 500 ms | ≤ 1.5 s | 0.91–0.99 s median (stages 0, 1, 3, both profiles) |
| Video memory, all models (`completo`) | ≤ 6.5 GB | 3.69 GB peak over a full session |
| Video memory peak (`compacto`, 10 turns + 5 readings) | ≤ 5.0 GB | 2.48 GB |
| WER of the TTS → STT loop | ≤ 10 %; `compacto` ≤ `completo` + 2 pp | 0.0 % and 0.0 % |
| Startup to models ready | ≤ 20 s warm | 15.1–15.9 s |
| Pronunciation false "error" on correct reading | ≤ 3 % per language | 0.00 % (es-419), 0.00 % (pt-BR) |
| Catalog mistakes flagged "error" | ≥ 80 % per language | 91.8 % (es-419), 87.9 % (pt-BR) |
| Heard sound named correctly | ≥ 60 % per language | 93.1 % (es-419), 88.1 % (pt-BR) |
| Outbound connections in a full session | only the LLM host | only the mock LLM on 127.0.0.1 (`network_audit.json`) |
| Interface strings in both learner languages | 100 % | 100 % |
| Corrector quality on a real provider | thresholds in `docs/testing.md` | not run: no key saved (owner task) |

## Stage 4 items

| Item | What was built | Check |
| --- | --- | --- |
| 4.1 Installer | `install.cmd` → `scripts/setup.ps1`: requirements and folder checks before any download; uv 0.13.7 from its GitHub release by SHA-256; Python 3.12 through uv into the app folder (no PATH or registry entries); packages from `uv.lock` (users without test tools); models by commit with HTTP Range resume and a SHA-256 manifest cross-checked against the hashes Hugging Face publishes; fonts and voice detector by sha512; shortcuts after a question; the app starts with the wizard. `uninstall.cmd` asks separately before deleting data and keys | `scripts/check_clean_install.py`: release archive into a folder with an accent and a space, empty `LOCALAPPDATA` and `TEMP`, install, install again, app start with speech and a reading check, uninstall — passed in 241 s with cached packages (about 5 minutes with all downloads). Resume and checksum retry: `tests/test_model_download.py`; folder checks, uv verification, shortcuts with accents: `tests/test_installer_ps1.py` |
| 4.2 Release | `scripts/make_release.ps1`: `VoiceTutor-0.1.0.zip` (0.5 MB: code, installer, docs, lock file), `SHA256SUMS.txt`, release notes draft in three languages | `tests/test_release.py` |
| 4.3 Privacy | No conversation text in logs unless Settings → Data → "Detailed log" is on (logger `voicetutor.turns`, with a warning in the window) | `tests/test_privacy_logs.py` runs a real turn with fake speech models; `tests/gpu/test_network.py` |
| 4.4 Documentation | READMEs and `docs/<lang>/{install,hardware,api-keys,usage,troubleshooting,privacy}.md` in English, Spanish and Portuguese; `CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`, `THIRD_PARTY_NOTICES` (runtime packages generated from `uv.lock`), `CHANGELOG`; tokens per answer measured on the mock (tutor 850 → 1300 input tokens over 10 answers, correction about 1450, summary about 1000) with a cost formula and no prices | `tests/test_docs.py`: links and anchors resolve, the three languages have the same structure |
| 4.5 Screenshots | `docs/images/conversation-es.png`, `docs/images/reading-pt-BR.png` from the real window with sample data | `tests/e2e/test_screenshots.py` (no key or user name on the page) |
| 4.6 GitHub files | `.github/workflows/ci.yml` (windows-latest, pinned `actions/checkout`, lint and the fast suite), issue forms for bugs and ideas in three languages, PR template; `scripts/ci_local.ps1`, `scripts/check_release.ps1` | `tests/test_github_files.py`; `ci_local.ps1` green |
| 4.7 Diagnostics | `scripts/collect_diagnostics.ps1`: versions, GPU, profile, settings and logs; saved keys, key-like strings, the Windows user name and conversation text removed | `tests/test_diagnostics.py` plants a key, a user path and turn text |

## Problems found and fixed in stage 4

- **Shortcuts in accented folders.** The clean install into "José Ñ" showed that `WScript.Shell` cannot save a shortcut there. Shortcuts are written through the Unicode shell interface now (`scripts/shortcut.ps1`).
- **espeak-ng and accented folders.** espeak-ng reads its data through the ANSI file API and phonemizer expands short names; the app gives espeak-ng the folder's 8.3 short name through `ESPEAK_DATA_PATH` (`voicetutor/espeak_path.py`), and the installer refuses a folder without an ASCII short name.
- **A vowel counted twice.** The Portuguese screenshot showed a false mark on "should" before "es-TART": one vowel fitted both "added after /d/" and "added before /s/". Only the stronger of two such neighbouring insertions is kept now; the stage 2 metrics of both languages are unchanged.
- **Windows PowerShell started from PowerShell 7** inherits a module path that breaks `Get-FileHash`; the `.cmd` wrappers clear it and the installer hashes and unzips through .NET.
- **Batch files and line endings.** `.gitattributes` keeps CRLF for `.cmd`, `.bat` and `.ps1`.

## Not done or limited

- **Corrector quality on a real provider** (`live` suite) was never run: there is no saved key, and the owner enters keys only in the app window.
- **Mark of the Web.** The clean-install check installs the release archive without the "downloaded from the internet" mark; adding that mark was refused in this session. A browser download and Explorer extraction is an owner task.
- **One machine only.** Everything ran on one RTX 5060 Laptop GPU with 8 GB; a 6 GB card and Windows 10 22H2 are untested.
- **CI on GitHub** has not run (nothing is pushed); its steps run locally through `scripts/ci_local.ps1`.
- **Proofreading** of the Spanish and Portuguese texts by native speakers is still open.
- **License question.** Whether the MIT app may be installed together with GPL-3.0 components (espeak-ng, phonemizer-fork) is an owner decision; the notices list them.

## Needed from the owner

The full list with defaults is in `docs/HUMAN_TASKS.md`. In short: decide on publication (name, repository, push, release), git author identity and the copyright line; answer the GPL question; enter a key in the app and run `scripts\test.ps1 live` once; install once from a browser-downloaded archive; have the Spanish and Portuguese texts proofread; decide whether the predecessor's background core may be stopped; keep or change the CI trigger.
