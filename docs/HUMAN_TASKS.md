# Owner tasks

Claude Code turns to the owner only through this list. New questions go to "Question queue" and are asked in one message at the end of a stage.

## Before publication (SPEC 14)

- [ ] Choose the final name and confirm the code license (default: Voice Tutor, MIT). Check that the name is free on GitHub and does not clash with known products.
- [ ] Create the GitHub repository and give the explicit command to push and to publish a release. Until then everything stays in the local git repository.
- [ ] Proofread the Spanish UI texts, tips and documentation.
- [ ] Find a native Brazilian Portuguese speaker to proofread the Portuguese texts.
- [ ] Decide on the GPL-3.0 question for espeak-ng (see `docs/reports/licenses.md`).
- [ ] If possible, install on a second machine with a different NVIDIA GPU (ideally 6 GB) and attach the `scripts\collect_diagnostics.ps1` archive.
- [ ] Run the `live` suite for both learner languages with your own key (`scripts\test.ps1 live`; paid, up to 80 requests per language).
- [ ] Record a short demo video or GIF for the README, if wanted.

## API key

- [ ] Create a separate key with a spending limit at the provider and type it into the app window (Settings → API connections → Add → template → paste key → Save → Test). Never send the key in chat.

## Question queue

Format: date, stage, question, options, default until answered.

| Date | Stage | Question | Options | Default |
| --- | --- | --- | --- | --- |
| 2026-11-12 | 0 | Should `docs/SPEC.md` and `docs/BASELINE_REPORT.md` (Russian brief and baseline, mention your machine) be published in the repository? | Keep them local / publish | Keep local, untracked |
| 2026-11-12 | 0 | The predecessor's core (`english_teacher_local`, `pythonw -m trainer.launcher`, started 2026-11-11 22:12) runs without a window and holds 3.9 GB of VRAM. Stage 3 measures free VRAM and the `compacto` peak; with it running, the dev machine would look like a 4 GB card. May Claude Code stop that process, or will you close it? | Claude Code stops it / you close it / leave it | Leave it; stage 0–2 tests pass with it running; stage 3 measurements wait |
| 2026-11-12 | 0 | Commits use your global git identity (name and e-mail). The history is local; before the first push it can be rewritten. Which author identity should the public history carry? | Keep as is / GitHub noreply address / another name | Keep as is until you decide; nothing is pushed |
| 2026-11-12 | 0 | Copyright line in `LICENSE`: "Copyright (c) 2026 Voice Tutor contributors". | Keep / your name / another holder | Keep |
| 2026-11-12 | 0 | GPL question from the license audit: the app (MIT) is installed together with and imports GPL-3.0-or-later components (espeak-ng via `espeakng-loader`, `phonemizer-fork`), all downloaded from PyPI on the user's machine and never in the repository or release archive. Keep MIT, change the license, or ask a lawyer? | Keep MIT with notices / relicense (e.g. GPL-3.0) / legal review first | Keep MIT and list the GPL components in THIRD_PARTY_NOTICES; no legal conclusion from Claude Code |
