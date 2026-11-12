# Stage 2 report: pronunciation for Spanish and Portuguese speakers

## Result

Stage 2 is closed: `scripts/check_stage.ps1 2` exits with 0. Each learner language has its own catalog of typical mistakes (20 entries each, SPEC 12), a new mistake type "inserted sound" is detected, 30 reading phrases cover every automatic entry of both languages at least twice, and the SPEC 12 metrics are met for both languages on synthetic speech of three American voices. The Russian catalog is gone; the repository has no Cyrillic left.

## Measurements

Synthetic speech: Kokoro voices `af_heart`, `af_bella`, `am_michael`. Accent variants are synthesized from modified phoneme strings inside the carrier phrases "I said {word}." and "Say {word} for me." (misaki override `[speak](/ɛspˈik/)`). Raw data: `docs/reports/data/pron_stage2_es-419.json`, `pron_stage2_pt-BR.json` (written by `scripts/pron_eval.py` and by the `gpu` suite).

| Metric | Target | es-419 | pt-BR |
| --- | --- | --- | --- |
| False "error" on correct reading of all 30 phrases (3 voices) | ≤ 3 % of phones | 0.00 % (0 of 2361) | 0.00 % (0 of 2361) |
| False "close" on correct reading | not a target | 0.25 % (6 of 2361) | 0.25 % (6 of 2361) |
| Catalog substitution, deletion or insertion flagged "error" (all error-level entries together) | ≥ 80 % | 91.8 % (306 cases) | 87.9 % (354 cases) |
| Heard sound named correctly (same cases) | ≥ 60 % | 93.1 % | 88.1 % |
| Close-level entries flagged at least "close" | reported | 67.6 % (108 cases) | 51.2 % (84 cases) |
| Assessment of a 5 s phrase | ≤ 1 s (predecessor target) | 0.048 s median | 0.039 s median |

"Named correctly" means the judgement names the pair's catalog entry and one of the pair's accepted names (catalog field `names`): an American phoneme model hears a Spanish or Portuguese tap as the flap /t, d/, and an inserted vowel before "s" as /ɛ/ or /ə/; both name the same mistake.

## Per catalog entry

Assessment: reliable — "error" (or, for close-level entries, flagged) in at least 80 % and named in at least 60 %; weaker — 50 to 80 %; unreliable — below 50 %.

### Latin American Spanish (es-419)

False alarms: 0 of 2361 scored phones got "error" (0.00 %), 6 got "close" (0.25 %).

Error-level entries together: 306 cases, "error" 91.8 %, named 93.1 %. Close-level entries: 108 cases, flagged 67.6 %, named 63.9 %.

| Entry | Kind | Level | Cases | "Error" | Flagged | Named | Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `short_i` | substitution | error | 24 | 96 % | 96 % | 96 % | reliable |
| `ae_vowel` | substitution | error | 24 | 100 % | 100 % | 96 % | reliable |
| `strut_vowel` | substitution | error | 24 | 96 % | 100 % | 100 % | reliable |
| `schwa_reduction` | substitution | approx | 18 | 0 % | 39 % | 28 % | unreliable |
| `short_u` | substitution | approx | 18 | 0 % | 100 % | 100 % | reliable |
| `nurse_vowel` | substitution | error | 18 | 89 % | 89 % | 89 % | reliable |
| `b_v` | substitution | error | 24 | 100 % | 100 % | 100 % | reliable |
| `th_voiceless` | substitution | error | 24 | 100 % | 100 % | 100 % | reliable |
| `th_voiced` | substitution | error | 24 | 92 % | 92 % | 92 % | reliable |
| `z_devoicing` | substitution | approx | 18 | 0 % | 100 % | 100 % | reliable |
| `sh_ch` | substitution | error | 24 | 88 % | 92 % | 92 % | reliable |
| `j_sound` | substitution | error | 24 | 92 % | 100 % | 92 % | reliable |
| `h_to_x` | substitution | approx | 18 | 0 % | 0 % | 0 % | unreliable |
| `r_tap_trill` | substitution | error | 24 | 62 % | 62 % | 62 % | weaker |
| `s_cluster_epenthesis` | insertion | error | 24 | 100 % | 100 % | 100 % | reliable |
| `ed_suffix` | substitution | error | 24 | 100 % | 100 % | 100 % | reliable |
| `ng_ending` | substitution | error | 24 | 79 % | 92 % | 92 % | weaker |
| `final_consonant_drop` | deletion | approx | 18 | 6 % | 67 % | 61 % | weaker |
| `w_gw` | insertion | approx | 18 | 6 % | 100 % | 94 % | reliable |
| `aspiration` | manual | approx | 0 | — | — | — | not detected automatically (tip in the sound help only) |

### Brazilian Portuguese (pt-BR)

False alarms: 0 of 2361 scored phones got "error" (0.00 %), 6 got "close" (0.25 %).

Error-level entries together: 354 cases, "error" 87.9 %, named 88.1 %. Close-level entries: 84 cases, flagged 51.2 %, named 44.0 %.

| Entry | Kind | Level | Cases | "Error" | Flagged | Named | Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `short_i` | substitution | error | 24 | 96 % | 96 % | 96 % | reliable |
| `ae_vowel` | substitution | error | 24 | 54 % | 62 % | 62 % | weaker |
| `strut_vowel` | substitution | error | 24 | 96 % | 100 % | 79 % | reliable |
| `schwa_reduction` | substitution | approx | 18 | 0 % | 39 % | 28 % | unreliable |
| `short_u` | substitution | approx | 18 | 0 % | 100 % | 100 % | reliable |
| `nurse_vowel` | substitution | error | 18 | 89 % | 89 % | 89 % | reliable |
| `th_voiceless` | substitution | error | 24 | 100 % | 100 % | 100 % | reliable |
| `th_voiced` | substitution | error | 24 | 92 % | 92 % | 92 % | reliable |
| `sh_ch` | substitution | error | 24 | 96 % | 96 % | 96 % | reliable |
| `h_dropped` | deletion | error | 24 | 100 % | 100 % | 100 % | reliable |
| `r_initial` | substitution | error | 24 | 100 % | 100 % | 75 % | reliable |
| `r_tap_trill` | substitution | error | 24 | 62 % | 75 % | 75 % | weaker |
| `s_cluster_epenthesis` | insertion | error | 24 | 75 % | 83 % | 83 % | weaker |
| `final_epenthesis` | insertion | error | 24 | 100 % | 100 % | 100 % | reliable |
| `ed_suffix` | substitution | error | 24 | 100 % | 100 % | 100 % | reliable |
| `t_d_palatal` | substitution | error | 24 | 79 % | 88 % | 88 % | weaker |
| `final_l` | substitution | approx | 24 | 0 % | 8 % | 0 % | unreliable |
| `final_m_nasal` | deletion | approx | 24 | 0 % | 67 % | 58 % | weaker |
| `ng_ending` | substitution | error | 24 | 79 % | 88 % | 88 % | weaker |
| `aspiration` | manual | approx | 0 | — | — | — | not detected automatically (tip in the sound help only) |

## Where the method is weak

| Entry | Language | Rate | Cause | Consequence |
| --- | --- | --- | --- | --- |
| `h_to_x` (h → Spanish jota) | es-419 | 0 % flagged | Kokoro's /x/ in an American voice is not separated from /h/ by the phoneme model, so the mistake cannot be verified on synthesis | Close-level entry: no false alarms; calibration needs real speech |
| `r_tap_trill`, trill part (road said with a trill) | es-419 | 0 of 6 | Kokoro renders /r/ close to an American /ɹ/ | Unverifiable on synthesis; word-initial and cluster taps are reliable (red, around: 12 of 12) |
| `r_tap_trill`, tap between vowels (very, sorry, story) | es-419, pt-BR | 50 % | Between vowels the tap is acoustically the American flap of /t, d/ | Weaker |
| `final_l` (l → w) | pt-BR | 8 % flagged | The American syllable-final dark /ɫ/ is itself velarized and close to /w/ for the phoneme model | Unreliable; close-level, so it never shows as an error |
| `ae_vowel` (æ → ɛ) | pt-BR | 54 % "error" | American /æ/ is raised toward /ɛ/ before nasals and in many words (bad/bed 2 of 6, sad/said 3 of 6); the predecessor measured the same 54 % | Weaker; the Spanish variant (æ → a) is reliable (100 %) |
| `schwa_reduction` | es-419, pt-BR | 39 % flagged | Full vowels in unstressed syllables are accepted variants of weak vowels in fluent American speech | Close-level hint only |
| `final_m_nasal` (m → nasal vowel) | pt-BR | 0 % "error", 67 % flagged | A nasalized vowel keeps part of the /m/ evidence | Close-level, as designed |
| `ng_ending`, ŋ → ŋɡ | es-419, pt-BR | 1 of 6 "error" | The added /ɡ/ is short after a nasal; it is mostly marked "close" | The ŋ → n part is reliable (18 of 18) |
| `s_cluster_epenthesis` with /i/ (ispeak) | pt-BR | 67 to 100 % per word | A short /i/ before /s/ leaves less evidence than /ɛ/ | Weaker for Portuguese (75 %); Spanish /ɛ/ 100 % |
| `aspiration` | es-419, pt-BR | not detected | Manual entry, as in the predecessor | Tip only in the sound help |

Synthetic voices are cleaner than learners' speech; thresholds stay those of the predecessor (catalog "error" from LLR 2.0, "close" from 1.25) and are calibrated per learner with "That was right".

## Checks

`scripts/check_stage.ps1 2` runs the repeated setup and the `fast`, `gpu`, `e2e` suites with the stage 0 and 1 required tests and 22 stage 2 tests (`scripts/check_stage.py`, `STAGES[2]`).

| Area | Tests |
| --- | --- |
| Catalogs | `tests/test_catalogs.py`: entry sets per language equal SPEC 12, schema, scoring classes, tips in their language, Latin American and Brazilian variety, reading coverage, insertions only at catalog positions; `tests/test_pron_logic.py::test_catalog_matching` |
| Metrics | `tests/gpu/test_pron.py::test_false_alarms_on_native_reading` and `test_catalog_mistakes_are_flagged_and_named`, each for es-419 and pt-BR |
| Insertion in a phrase | `test_accented_phrase_marks_the_right_words`: p01 with "estart" and "tird" marks exactly start (`s_cluster_epenthesis`, heard `+ə` or `+ɛ`) and third (`t` for `θ`) |
| Window | `tests/e2e/test_reading.py` in Spanish (extra sound "Sobra un sonido", "That was right") and Portuguese (Portuguese tip, `lang="pt-BR"`); `tests/e2e/test_pron_marks.py` ("video" said with /b/ in conversation) |

## What changed

- **Catalogs.** `voicetutor/data/l1/<code>/catalog.json` with the fields of the predecessor (`expected`, `heard`, `position`, `detect`, `default_level`, `priority`, `title`, `tip`, `examples`, `pairs`), texts in the learner language. Tips compare with native sounds checked for the variety: the Latin American intervocalic «d» of «nada» for /ð/, «tch» of «tchau» for /tʃ/, the «r» of «rato» and the «caipira» r for Brazilian speakers. American tolerances (flap, cot–caught, unreleased final /t/, weak vowels, weak forms) are unchanged.
- **New positions.** `s_cluster`, `word_final_obstruent`, `word_final_cluster`, `ed_suffix` (spelled -ed after a consonant other than t, d), `before_high_front_vowel`, `coda`, `word_initial`.
- **Inserted sound.** For `s_cluster_epenthesis`, `final_epenthesis` and `w_gw` the catalog adds competitors with an inserted sound before or after the expected one, only where the entry's position applies; the score is the same windowed CTC likelihood ratio as for substitutions. The diagnosis is `heard: "+ɛ"`; the window says "Sobra un sonido: /ɛ/" or "Sobrou um som: /ɛ/". The -ed suffix is a substitution of /t/ by /ɪd/, /ɛd/ or /əd/.
- **Catalog per language.** The reference carries the learner language; `catalog.match` and the extra competitors use that language's catalog.
- **Reading phrases.** 30 shared phrases (work and daily life, 6 to 12 words, American vocabulary); targets are computed from both catalogs; every automatic entry occurs in at least two phrases of each language.
- **Accent fixtures.** Pairs carry `say` (Kokoro phonemes); `tests/fixtures/make_fixtures.py` synthesizes them inside carrier phrases. The conversation and reading fixtures now carry Spanish-speaker mistakes ("video" with /b/; "estart", "tird").

## Decisions and deviations

- The "flagged error" metric of at least 80 % is computed over error-level entries (close-level entries can never become "error" by design); close-level entries are reported separately.
- Pairs list accepted names (`names`) for the "named correctly" metric where the American phoneme model names the same mistake differently (tap as /t, d/, inserted vowel as /ə/).
- Reading phrases are shared by both languages (coverage allowed it).
- Details: `docs/PROGRESS.md` → Decisions.

## Did not work

- `h_to_x`, the trill part of `r_tap_trill` and `final_l` cannot be verified on synthetic speech (see the table above). They stay in the catalogs because the tips are useful and they produce no false alarms.

## Needed from the owner

- Proofread the catalog titles and tips (`voicetutor/data/l1/es-419/catalog.json`, `pt-BR/catalog.json`), in particular the comparisons with native sounds.
- If possible, read 10 phrases in the Reading screen in each language and mark false alarms with "That was right".
