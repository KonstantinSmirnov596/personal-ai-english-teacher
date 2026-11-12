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
