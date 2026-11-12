# Testing without a human

Goal: every check in `docs/PLAN.md` runs as a command and returns an exit code. A human is needed only to judge by ear and for live speech (see `docs/HUMAN_TASKS.md`).

Three techniques replace the human:

- **Speech** is synthesized by Kokoro: generated WAV files serve both as user turns and as the reference for recognition checks.
- **Microphone**: in end-to-end tests a WAV file is fed to Edge as the input device.
- **LLM**: a local mock server with an OpenAI-compatible interface.

## Suites

| Suite | pytest marker | Needs | Checks | Time |
| --- | --- | --- | --- | --- |
| `fast` | no marker | Python only | Logic without models: protocol, storage, LLM client against the mock, security, sentence splitting, schemas, data files, i18n, repository hygiene | ≤ 1 min |
| `gpu` | `gpu` | NVIDIA GPU and models | STT, TTS, a turn through the WebSocket with the mock LLM, pronunciation assessment, network audit | ≤ 10 min |
| `e2e` | `e2e` | Edge, Playwright, GPU | The whole window with a fake microphone and the mock LLM | ≤ 10 min |
| `live` | `live` | Saved key and network | The real provider: streaming, JSON mode, corrector quality | ≤ 3 min |

`scripts/test.ps1 <suite>` runs a suite; `all` runs `fast`, `gpu`, `e2e` and `live`. Without an active connection with a key, `live` is skipped (`skipped`), not failed.

`live` spends the owner's money: at most 80 requests per run, no retry loops. It runs only on the owner's word.

### Model profiles

SPEC 7 requires both profiles to pass `gpu` and `e2e`. `pytest --vt-profile completo|compacto` (default `auto`; `scripts\test.ps1 gpu --vt-profile compacto`) is an option of the tests, read by `tests/profile_opt.py`: before a launcher starts, the profile is stored in its temporary data directory as if the user had chosen it in Settings → Performance, and models built directly in a test get the profile's compute type. The app reads no flag or variable for this. `scripts/check_stage.ps1 3` runs `gpu@compacto` and `e2e@compacto` next to the default suites.

### Hardware the machine does not have

Unsupported hardware, other drivers, batteries and out-of-memory errors are produced by test doubles passed to the `Core` constructor (`detector=`, `stt=`, `tts=`; `tests/hw_fakes.py`), never by a switch in the app. `tests/e2e/test_unsupported_window.py` runs such a core in the test process (uvicorn in a thread) and opens it in Edge. `tests/gpu/test_vram.py` fills the real GPU from the test process while a real core runs. `tests/test_requirements_ps1.py` feeds fake facts to the PowerShell functions of the installer's requirements check.

## Isolation from user data

Tests never use the real data directory or real keys.

| Environment variable | Purpose | Value in tests |
| --- | --- | --- |
| `VOICETUTOR_DATA_DIR` | Data directory | A temporary directory |
| `VOICETUTOR_KEYRING_SERVICE` | keyring service name | `VoiceTutor-test` |
| `VOICETUTOR_MODELS_DIR` | Models directory | The shared real directory, so models are not downloaded again |

This is ordinary configuration, not a security bypass. Routes, flags and variables that disable the cookie, `Origin` or `Host` checks, substitute text for recognition, or otherwise change core behaviour "for tests only" are forbidden. Hardware fakes (stage 3) are injected through dependency injection in unit tests, never through the running app.

The `live` suite reads the key from the real keyring service read-only and never prints it.

## Speech fixtures

`tests/fixtures/make_fixtures.py` synthesizes WAV files into `tests/fixtures/audio/generated/` (not tracked by git). The list is in `tests/fixtures/phrases.json`. Generation is as deterministic as Kokoro allows; a file is regenerated only when missing.

| File | Content | Purpose |
| --- | --- | --- |
| `loop_01` … `loop_10` | 10 phrases of 3–10 s, voice `af_heart` | TTS → STT loop, word error rate |
| `turn_basic` | "I have worked on this project since two years." and 5 s of silence | Manual-mode end-to-end test |
| `turn_pause_1200` | Phrase, 1.2 s silence, second phrase, 5 s silence | Pause threshold in auto mode |
| `silence_5s`, `noise_5s` | Silence and pink noise | Empty recognition |
| `too_short` | 0.2 s of speech | Code `audio_too_short` |
| `read_<phrase_id>_<voice>` | Every reading phrase in three American voices | False alarms of pronunciation assessment |
| `pair_<expected>_<actual>` | Catalog minimal pairs: the second word is synthesized | Substitution detection |

Fake-microphone format: WAV, PCM 16-bit, mono, 48 kHz. For direct requests to the core, Kokoro's 24 kHz is fine: the core resamples.

Word error rate is computed after normalization: lower case, no punctuation, numbers as words (own Levenshtein implementation in `voicetutor/wer.py`).

Limitation: synthetic speech is cleaner than live speech. Measurements on it show that the pipeline works but do not replace a check on a learner's voice.

## Mock LLM

`tests/mock_llm/` is a separate app that a pytest fixture starts on a free `127.0.0.1` port. A test creates a connection with `http://127.0.0.1:<port>/v1` and a test key like `sk-test-<random>`.

Route `POST /v1/chat/completions`:

- With `stream: true` it answers with an OpenAI-format SSE stream: `data: {...}` lines with `choices[0].delta.content`, ending with `data: [DONE]`. The text is split into chunks of 2–3 words with a configurable delay.
- With `response_format` it answers with a JSON object. For the corrector the mock builds a correction from the turn itself: `quote` is the first two words of the user's text, so the substring check passes for any recognition result.
- It checks `Authorization: Bearer <test key>` and answers 401 on mismatch.
- It records all requests: a test reads them via `GET /__mock/requests` and checks the body (no audio, `extra_params` present, stable `messages` prefix).

Behaviour control: `POST /__mock/script` — first-chunk delay, inter-chunk delay, reply text, error code (401, 429, 500), stream break at chunk N, empty answer, invalid JSON, hang until timeout. These routes exist only in the mock; the core has none of them.

## End-to-end tests: Edge and a fake microphone

Playwright for Python, channel `msedge`, persistent profile in a temporary directory, headless. Chromium flags:

```text
--use-fake-device-for-media-stream
--use-fake-ui-for-media-stream
--use-file-for-fake-audio-capture=<absolute path>.wav
```

- The file is set at browser launch and loops by default. One file — one browser instance; tests with different files relaunch the browser.
- The `%noloop` suffix after the path disables looping.
- The second flag removes the microphone permission prompt. In a real launch the prompt stays and the user accepts it once.
- Autoplay: the test clicks "Start conversation" like a person; `--autoplay-policy` is not used.

Synchronizing with a looping file in manual mode: the test waits until the waveform level stays below the silence threshold for 1 s, presses Space, waits for the level to rise and fall again for 1 s, presses Space. Exactly one phrase gets recorded.

In auto mode with "I'm using headphones" off, the window does not start a new turn while the core is `thinking` or `speaking`; the next loop of the file becomes the next turn. The test ends the session after the needed number of turns.

The test starts the app with the same launcher as a user, but opens the browser itself: the launcher gets `--no-window` and prints the address with the token to stdout. This is the only difference from a normal launch; security stays fully on.

## Window observability

Tests look at the same attributes the layout uses. There are no separate test interfaces.

| Attribute | Where | Values |
| --- | --- | --- |
| `data-state` | Root element of the bottom panel | `idle`, `listening`, `transcribing`, `thinking`, `speaking` |
| `data-level` | Waveform element | Current signal level 0–100, updated at least 10 times per second |
| `data-source` | Waveform element | `mic` or `tutor` |
| `data-testid` | Interactive elements and feed blocks | `start-session`, `mic-button`, `mode-toggle`, `turn-user`, `turn-tutor`, `correction-mark`, `correction-card`, `pron-mark`, `error-banner`, `switch-connection`, `conn-row`, `conn-add`, `conn-key-input`, `conn-test`, `conn-activate`, `conn-delete` and others |
| `data-turn-id` | Turn block | Turn id |
| `data-first-audio-ms` | Tutor turn block | Time from end of turn to first audio by the window's clock |
| `lang` | Every text block | `en` for turns, the learner language for corrections and hints |

Check "learner language only in cards": elements with `lang="en"` contain no learner-language text; synthesis never receives it (separate service-level test).

## Security checks

`fast` suite, no models:

- `/api/health` without the cookie → `401`. With the cookie and `Host: evil.example` → `421`. With `Origin: http://evil.example` → `403`.
- WebSocket handshake without the cookie, with a foreign `Origin`, with a foreign `Host` → rejected.
- Reusing the launch token → `403`.
- No response contains `Access-Control-*` headers.
- HTML is served with a CSP header; files in `web/` contain no `http://` or `https://` addresses except license comments.
- **Secret.** The test saves a connection with a marker key, runs a turn and a connection test with a 401 from the mock, then searches for the marker in the database file, logs, export, the answers of all `GET` routes and the core's stdout. The marker may only be in the `VoiceTutor-test` keyring service and in the requests recorded by the mock.
- **Network.** The test intercepts connection creation in the core process during a full scenario and checks the addresses: only `127.0.0.1` and the host of the active connection. In the test the active connection is the mock, so any external address is a failure.

## Latency measurements

Measurement points match the fields of the `timing` message in `docs/protocol.md`. The window adds its own: from sending `turn.audio` to the start of playback.

- With the mock LLM and 0 ms first-chunk delay we get the app's own latency: target ≤ 0.9 s.
- With a 500 ms delay we approximate a cloud provider: target ≤ 1.5 s.
- Each measurement is repeated 5 times; the report gives the median and maximum. The first run after model loading is excluded and recorded separately as cold.

## Corrector quality (`live` suite)

Evaluation sets `voicetutor/data/l1/<code>/corrector_eval.jsonl` hold 40 phrases per learner language: 28 with mistakes typical for its speakers, 8 correct ones (including colloquial forms and fillers) and 4 with low-confidence words. The test runs each set through the real prompt in that language and the active connection; at most 80 requests per language.

| Metric | Threshold |
| --- | --- |
| Answer passes the schema check (with one retry) | 100 % |
| `quote` is a substring of the turn | ≥ 95 % of corrections |
| Correct phrases (`expect: []`) stay without corrections | ≥ 80 % of phrases |
| A phrase with an error gets the expected `pattern` key | ≥ 70 % of phrases |
| Words from `low_conf` never get into `quote` | 100 % |
| `note_l1` is in the learner language (language guard) and at most 25 words | 100 % |

If a threshold is missed, the prompt in the code is changed and the result and the new text go into the stage report. Without a key this check is deferred to `docs/HUMAN_TASKS.md`.

## Stage acceptance

`scripts/check_stage.ps1 <N>` runs the suites needed by the stage and all earlier stages, requires the listed tests to pass (not merely be collected), checks that reports exist without placeholders or empty table cells, prints a summary and returns 0 only on full success. A `live` suite skipped for lack of a key is not a failure but gets its own summary line. A suite name with `@<profile>` runs it with `--vt-profile <profile>`; a stage may also list acceptance scripts (stage 3: `scripts/bench_profiles.py`) whose exit code must be 0.
