# Stage 1 report: learner languages

## Result

Stage 1 is closed: `scripts/check_stage.ps1 1` exits with 0. The app works in Latin American Spanish (`es-419`) and Brazilian Portuguese (`pt-BR`), switched by hand in Settings → Language without a restart; the Russian locale is gone except the pronunciation catalog, which stage 2 replaces. The paid `live` suite did not run: no API key is saved (owner task).

## Measurements

| Metric | Target | Measured | How |
| --- | --- | --- | --- |
| i18n key completeness, `es-419` | 100 % | 100 % (267 keys, every key used by `web/js` present) | `tests/test_i18n.py::test_completeness_is_100_percent` |
| i18n key completeness, `pt-BR` | 100 % | 100 % (same 267 keys, same shapes and parameter counts) | `tests/test_i18n.py` |
| Long UI strings recognized as their own language | ≥ 85 %, none as the other language | es-419 and pt-BR pass; 0 cross-detections | `tests/test_i18n.py::test_strings_are_in_their_language` |
| Language guard: English sentences with Spanish/Portuguese names and places passing | all (≥ 30 cases) | 38 of 38 | `tests/test_lang_guard.py` |
| Language guard: Spanish / Portuguese sentences caught | all | 10 of 10 / 10 of 10 | `tests/test_lang_guard.py` |
| Learner-language text in elements with `lang="en"` | none | none (Spanish and Portuguese sessions) | `tests/e2e/test_conversation.py`, `tests/e2e/test_languages.py` |
| End of turn → first audio, mock 0 ms | ≤ 0.9 s | 0.396 s median, 0.427 s max | `scripts/bench_turn.py`, 5 runs, `docs/reports/data/bench_turn_stage1.json` |
| End of turn → first audio, mock 500 ms | ≤ 1.5 s | 0.908 s median, 0.917 s max | same |
| Corrector quality on the live provider, both languages | thresholds of `docs/testing.md` | not run: no saved key | `tests/live/test_live_llm.py::test_live_corrector_quality[es-419\|pt-BR]` |

## Checks

`scripts/check_stage.ps1 1` runs the repeated setup, `fast`, `gpu`, `e2e` and the optional `live` suite, and requires the stage 0 tests plus 41 stage 1 tests (`scripts/check_stage.py`, `STAGES[1]`).

| Suite | Result | Note |
| --- | --- | --- |
| `fast` | green | i18n, registry, prompts, guard, scenarios, keys, sets, migration, hygiene with a one-file Cyrillic allowlist |
| `gpu` | green | Synthesis rejects Spanish, Portuguese and other scripts before model work; English with "São Paulo" is spoken |
| `e2e` | green | Spanish conversation (default language), language switch to Portuguese without reload, Portuguese corrections and translation, history keeps the session language |
| `live` | skipped | No active connection with a saved key |

## What changed

- **Languages as files.** `voicetutor/l1.py` discovers `voicetutor/data/l1/<code>/` (`meta.json`, `messages.json`, `patterns.json`, `corrector_eval.jsonl`); `web/i18n/<code>.js` holds the window strings. A third language added by copying files is discovered (`test_a_third_language_is_added_by_files_only`).
- **Choice of language.** Setting `l1`; until confirmed, the Windows locale suggests one (`es-*` → Spanish, `pt-*` → Portuguese, anything else → Spanish). `GET /api/languages` lists the languages; Settings → Language switches them. The window loads its strings before the views (`web/js/main.js`), replaces them in place on a switch and re-renders (`web/js/i18n.js`).
- **Prompts.** Corrector, summary and helpers name the learner language (`{l1_name_en}`) and its variety (tú/no vosotros; você/Brazilian spelling). The corrector receives all mistake keys with language marks and a worked example per language ("I have 30 years" for Spanish, "In my city has a big park" for Portuguese). The tutor prompt is language-neutral so its cached prefix survives a switch. Prompts spell "JSON" for OpenAI's JSON mode.
- **Fields.** `note_ru` → `note_l1` and every other `_ru` field → `_l1`; migration 5 renames the columns with their data, adds `session.l1` and per-language titles of built-in scenarios. History shows a session's notes in the language it was held in.
- **Language guard.** `voicetutor/lang_guard.py` replaces the Cyrillic check: before synthesis, for English fields of LLM answers, for vocabulary phrases and for reading texts.
- **Scenarios.** The 11 scenarios of SPEC 6; ERP/ECM and document workflow are gone; interviews follow the backend structure; titles and descriptions in both languages.
- **Mistake keys.** 27 keys of SPEC 12 with `l1` marks, names and hints per language; retired keys stay in old databases but are hidden.
- **Corrector sets.** `corrector_eval.jsonl` per language: 28 typical mistakes, 8 correct utterances (colloquial forms, fillers), 4 with low-confidence words.
- **Mock LLM** answers in the language its prompt names, so the window tests see Spanish or Portuguese text.

## Decisions and deviations

- The Russian locale is removed rather than kept as a third language (cheaper to drop than to port to the new layout).
- All `_ru` fields became `_l1`, not only `note_ru`.
- The i18n language check tolerates up to 15 % unrecognized long strings: the guard is tuned to never call English text Spanish or Portuguese.
- The Russian pronunciation catalog and the Cyrillic font subsets: catalog until item 2.1; fonts now Latin-only.
- Details: `docs/PROGRESS.md` → Decisions.

## Did not work

- The `live` suite (corrector quality per language, first chunk on a real provider) needs the owner's key; deferred to `docs/HUMAN_TASKS.md`.
- The predecessor's windowless core still holds VRAM on the development machine (see stage 0); this stage's GPU and window suites passed regardless.

## Needed from the owner

- Proofread the Spanish and Portuguese UI strings (`web/i18n/es-419.js`, `web/i18n/pt-BR.js`), core messages and mistake-key hints (`voicetutor/data/l1/*/`).
- With your own key: `scripts\test.ps1 live` (up to 80 requests per language).
- Open questions from stage 0 remain in `docs/HUMAN_TASKS.md`.
