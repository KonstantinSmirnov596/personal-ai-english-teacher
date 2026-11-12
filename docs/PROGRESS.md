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

## Failed checks

Format: check, what was tried, what was seen, next step.

- none yet

## Measurements

Latest values of the targets in `docs/PLAN.md`.

| Metric | Target | Measured | Date |
| --- | --- | --- | --- |
| STT of a 10 s turn | ≤ 0.4 s | not measured yet | — |
