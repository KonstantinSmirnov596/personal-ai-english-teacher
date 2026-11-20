# Owner tasks

Claude Code turns to the owner only through this list. New questions go to "Question queue" and are asked in one message at the end of a stage.

## Before publication (SPEC 14)

- [x] Final name and license (answered 2026-11-20): "Personal AI English Teacher (ES/PT) for Desktop/Notebook with GPU"; license chosen by Claude Code for public use: MIT, "Copyright (c) 2026 Konstantin Smirnov".
- [x] Repository and release (command given 2026-11-20: "create it yourself, do it and publish"): `KonstantinSmirnov596/personal-ai-english-teacher`, release v0.1.0. Every later push or release needs a new command.
- [ ] Proofread the Spanish UI texts, tips and documentation.
- [ ] Find a native Brazilian Portuguese speaker to proofread the Portuguese texts.
- [x] GPL-3.0 question for espeak-ng (answered 2026-11-20): keep MIT and list the GPL components in `THIRD_PARTY_NOTICES.md`.
- [ ] If possible, install on a second machine with a different NVIDIA GPU (ideally 6 GB) and attach the `scripts\collect_diagnostics.ps1` archive.
- [ ] Run the `live` suite for both learner languages with your own key (`scripts\test.ps1 live`; paid, up to 80 requests per language).
- [ ] Record a short demo video or GIF for the README, if wanted.

## Stage 1

- [ ] Proofread `web/i18n/es-419.js` (Latin American Spanish, tú) and `web/i18n/pt-BR.js` (Brazilian Portuguese, você), plus `voicetutor/data/l1/*/messages.json`, `patterns.json` and the scenario titles in `voicetutor/data/scenarios.json`.
- [ ] After entering a key in the app: `scripts\test.ps1 live` (corrector quality for both languages, up to 80 requests per language) and send the summary line it prints.

## Stage 2

- [ ] Proofread the pronunciation catalogs (`voicetutor/data/l1/es-419/catalog.json`, `voicetutor/data/l1/pt-BR/catalog.json`), especially the comparisons with native sounds in the tips.
- [ ] If possible: read 10 phrases in the Reading screen per language and press "That was right" on marks you disagree with; tell Claude Code how many marks felt wrong.

## Stage 3

- [ ] Proofread the new Spanish and Portuguese texts: the first-run wizard and Settings → Performance (`web/i18n/es-419.js`, `web/i18n/pt-BR.js`, sections `wizard`, `performance`, `notices`), the installer messages (`scripts/requirements.messages.json`) and `docs/es/hardware.md`, `docs/pt-BR/hardware.md`.
- [ ] If possible: run the wizard once yourself (Settings → Performance → "Run the wizard again") and say whether any step is unclear.

## Stage 4

- [ ] Install once the way a user would: download the release archive with a browser (so Windows marks it as downloaded from the internet), extract it with Explorer into a new folder, double-click `install.cmd`, and say whether any warning or step was confusing. Claude Code cannot add the "downloaded from the internet" mark itself in this session.
- [ ] Proofread `README.es.md`, `README.pt-BR.md` and `docs/es/*.md`, `docs/pt-BR/*.md`.

## API key

- [ ] Create a separate key with a spending limit at the provider and type it into the app window (Settings → API connections → Add → template → paste key → Save → Test). Never send the key in chat.

## Question queue

Format: date, stage, question, options, default until answered.

| Date | Stage | Question | Options | Default |
| --- | --- | --- | --- | --- |
| 2026-11-12 | 0 | Should `docs/SPEC.md` and `docs/BASELINE_REPORT.md` (Russian brief and baseline, mention your machine) be published in the repository? | Keep them local / publish | Answered 2026-11-20: publish them |
| 2026-11-12 | 0 | The predecessor's core (`english_teacher_local`, `pythonw -m trainer.launcher`, started 2026-11-11 22:12) runs without a window and holds 3.9 GB of VRAM. Stage 3 measures free VRAM and the `compacto` peak; with it running, the dev machine would look like a 4 GB card. May Claude Code stop that process, or will you close it? | Claude Code stops it / you close it / leave it | Leave it; stage 0–2 tests pass with it running; stage 3 measurements wait |
| 2026-11-12 | 0 | Commits use your global git identity (name and e-mail). The history is local; before the first push it can be rewritten. Which author identity should the public history carry? | Keep as is / GitHub noreply address / another name | Answered 2026-11-20: author Konstantin Smirnov (GitHub noreply address), Claude as co-author, dates kept |
| 2026-11-12 | 0 | Copyright line in `LICENSE`: "Copyright (c) 2026 Konstantin Smirnov". | Keep / your name / another holder | Answered 2026-11-20: Konstantin Smirnov |
| 2026-11-12 | 0 | GPL question from the license audit: the app (MIT) is installed together with and imports GPL-3.0-or-later components (espeak-ng via `espeakng-loader`, `phonemizer-fork`), all downloaded from PyPI on the user's machine and never in the repository or release archive. Keep MIT, change the license, or ask a lawyer? | Keep MIT with notices / relicense (e.g. GPL-3.0) / legal review first | Answered 2026-11-20: keep MIT with notices |
| 2026-11-12 | 3 | SPEC 7 asks the wizard to download missing models; CLAUDE.md allows downloads only at install time and no run-time traffic except the LLM. Claude Code followed CLAUDE.md: the wizard sends the user to `install.cmd` (resume and checksums there, stage 4) and loads the models afterwards. Keep it that way? | Keep install-only downloads / allow the wizard to download | Install-only downloads |
| 2026-11-12 | 4 | CI (`.github/workflows/ci.yml`) installs the full Python environment on `windows-latest` (about 5 GB of packages; its duration on GitHub is not measured yet, nothing was pushed) to run lint and the fast suite; GPU suites stay local (`scripts/check_release.ps1`). Keep it, or run CI only on pull requests / by hand? | On every push and pull request / pull requests only / manual only | Every push to `main` and every pull request |
| 2026-11-20 | 4 | An installer `.exe` instead of the archive with `install.cmd`? A single exe with everything is impossible (GitHub limits a release file to 2 GiB; the environment and models are about 8 GB). A small unsigned `Setup.exe` that downloads like `install.cmd` is possible; Windows SmartScreen warns about it as about the script, and a code-signing certificate costs money every year. | Small unsigned Setup.exe / keep install.cmd / buy a certificate later | Keep install.cmd until you decide |
