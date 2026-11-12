# Window–core contract

The window (frontend in Edge) and the core (Python) talk over HTTP and one WebSocket on `127.0.0.1`. This document refines the message summary in `docs/design.md`; where names or fields differ, this document wins. Messages are pydantic models in `voicetutor/protocol.py`; a contract change goes here in the same commit.

## Launch and access

1. The launcher picks a port (the first free one of 47613–47622), creates a random token (at least 32 bytes, `secrets.token_urlsafe`) and starts the core.
2. The launcher opens the window at `http://127.0.0.1:<port>/?t=<token>`.
3. The core checks the token, sets the cookie `voicetutor_session` (`HttpOnly; SameSite=Strict; Path=/`) and answers with a `303` redirect to `/`. The token is single-use: a second request with it gets `403`.
4. All other routes, static files and the WebSocket require this cookie.

Checks on every request, including the WebSocket handshake:

| Check | Condition | Response on violation |
| --- | --- | --- |
| `Host` | Exactly `127.0.0.1:<port>` or `localhost:<port>` | `421` |
| Cookie | Equals the one issued at launch | `401` |
| `Origin` | If present, equals `http://127.0.0.1:<port>` or `http://localhost:<port>`. Mandatory for the WebSocket and for state-changing requests | `403` |

The core sends no CORS headers. Every HTML response carries a CSP header: `default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; connect-src 'self' ws://127.0.0.1:<port>; media-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'`. `wasm-unsafe-eval` is needed by the WebAssembly build of the voice activity detector; string `eval` stays forbidden.

## WebSocket

Address: `ws://127.0.0.1:<port>/ws`. One connection per window; a second connection closes the first with code `4001`.

Two kinds of frames:

- Text frame: a JSON object with a `type` field.
- Binary frame: audio. It always follows a text message that contains an `audio` object with a `bytes` field and carries exactly that many bytes. There are no other binary frames.

Audio format in both directions: PCM, signed 16-bit, little-endian, mono. The sample rate is given in the message.

Limits: a turn is 0.3–60 s; a text frame up to 256 KB; a binary frame up to 8 MB. The server's maximum message size allows this.

### Window → core

| `type` | Fields | Meaning |
| --- | --- | --- |
| `session.start` | `scenario_id`, `level?` | Start a session. The core answers `session.started` and the tutor's first line |
| `session.end` | — | End the session. The core answers `summary` |
| `turn.begin` | `turn_id`, `mode: "manual" \| "auto"` | The window started recording. If the core is `thinking` or `speaking`, this acts as `interrupt` |
| `turn.audio` | `turn_id`, `audio: {sample_rate, format: "pcm_s16le", bytes}` + binary frame | The whole turn. Sample rate 16000–48000; the core resamples to 16 kHz |
| `turn.cancel` | `turn_id` | Recording cancelled (Esc). The core returns to `idle` |
| `turn.retry` | `turn_id` | Repeat the tutor's reply to a turn after an LLM error ("Retry" and "Switch to…" buttons). The turn is already in the history and is not recognized again |
| `interrupt` | — | Stop the current reply: close the LLM stream, clear the synthesis queue. The corrector request is not cancelled |
| `playback.started` | `turn_id`, `client_first_audio_ms` | The window started playing the reply. The number is the time from sending `turn.audio` to the first sound, by the window's clock |
| `playback.ended` | `turn_id`, `interrupted: bool` | The playback queue is empty. The core goes to `idle` |
| `helper.hint` | `request_id` | Two or three possible answers to the tutor's last line |
| `helper.translate` | `request_id`, `turn_id` | Translation of a tutor line into the learner's language |
| `helper.how_to_say` | `request_id`, `text_l1` | How to say this phrase in English |
| `tutor.replay` | `turn_id`, `speed: 1.0 \| 0.8` | Replay a tutor line. The core sends `tutor.sentence` again with `replay: true` |
| `exercise.answer` | `request_id`, `audio: {...}` + binary frame | Spoken answer to the summary exercise |

`turn_id` and `request_id` are created by the window (UUID). Tutor lines get their `turn_id` from the core.

### Core → window

| `type` | Fields | Meaning |
| --- | --- | --- |
| `hello` | `protocol: 1`, `app_version`, `state`, `active_connection: {id, name, model} \| null`, `settings`, `models_ready: bool` | First message after connecting. `models_ready` is false while the STT and TTS models load |
| `session.started` | `session_id`, `scenario: {id, title_l1}`, `connection: {id, name, model}` | Session opened |
| `state` | `value: "idle" \| "listening" \| "transcribing" \| "thinking" \| "speaking"`, `turn_id?` | Every core state change |
| `user.transcript` | `turn_id`, `text`, `words: [{w, start, end, p}]`, `low_conf: [word indexes]` | Turn text. `p` is the word confidence from 0 to 1; `low_conf` lists words below the threshold |
| `tutor.delta` | `turn_id`, `text` | Next raw fragment of the reply text for the feed |
| `tutor.sentence` | `turn_id`, `index`, `text`, `replay?: bool`, `audio: {sample_rate: 24000, format: "pcm_s16le", bytes}` + binary frame | A reply sentence with audio |
| `tutor.done` | `turn_id`, `text`, `interrupted: bool` | The reply is finished; `text` is the cleaned text that was spoken or sent |
| `corrections` | `turn_id`, `status: "ok" \| "empty" \| "failed" \| "disabled"`, `items: [{id, quote, start, end, fix, type, note_l1, pattern}]`, `better` | Corrections. `start` and `end` are character positions of `quote` in `text`; `null` when the fragment is not found |
| `pron.flags` | `turn_id`, `items: [{word_index, expected, heard, tip_l1}]` | Pronunciation marks in conversation |
| `helper.result` | `request_id`, `kind: "hint" \| "translate" \| "how_to_say" \| "exercise"`, `data` | Helper answer. `hint`: `{options: [{en}]}`; `translate`: `{translation_l1, turn_id}`; `how_to_say`: `{en, alt, note_l1}`; `exercise`: `{correct, note_l1, answer_en, heard}` |
| `summary` | `session_id`, `key_takeaway`, `exercise`, `corrections`, `patterns`, `sounds`, `phrases` | Session summary |
| `timing` | `turn_id`, `stt_ms`, `llm_first_sentence_ms`, `tts_first_ms`, `first_audio_ms` | Core timings of a turn. `first_audio_ms` runs from receiving `turn.audio` to sending the first `tutor.sentence` |
| `error` | `code`, `message_l1`, `retryable: bool`, `turn_id?`, `request_id?` | Error. Afterwards the core is `idle` |

Correction `type` values: `grammar`, `vocabulary`, `phrasing`. `pattern` values are keys of `voicetutor/data/patterns.json`.

### Error codes

| Code | When | What the window shows |
| --- | --- | --- |
| `no_active_connection` | No active connection | Link to "API connections" |
| `llm_unauthorized` | Provider answered 401, 402 or 403 | Message and a "Switch to…" button |
| `llm_rate_limited` | 429 | Message and a "Retry" button |
| `llm_unreachable` | No network, DNS, TLS, timeout | Message, "Retry" and "Switch to…" buttons |
| `llm_bad_response` | 5xx, broken stream, empty answer | Message and a "Retry" button |
| `stt_failed` | Recognition failed | Message; the turn can be repeated |
| `tts_failed` | Synthesis failed | Reply text stays in the feed without audio |
| `audio_too_short` | Turn shorter than 0.3 s | Quiet hint in the panel, nothing in the feed |
| `audio_too_long` | Turn longer than 60 s | Message |
| `bad_request` | Message failed schema validation | Log entry; nothing in the feed |
| `internal` | Everything else | Message and log entry |

The provider's error text is never copied into `message_l1` verbatim: it is cut to 200 characters and passes the key filter.

### Message order of one turn

```text
window → turn.begin
core   → state listening
window → turn.audio + audio
core   → state transcribing
core   → user.transcript
core   → state thinking              (the corrector request runs in parallel from here)
core   → tutor.delta ...
core   → tutor.sentence + audio      (first sentence)
core   → state speaking
core   → timing
window → playback.started
core   → tutor.sentence + audio ...
core   → tutor.done
core   → corrections                 (any time after user.transcript)
window → playback.ended
core   → state idle
```

An empty transcript (silence, noise) gives `user.transcript` with empty `text` and a return to `idle` without an LLM request.

## HTTP

All routes are under `/api`, bodies and answers are JSON unless noted. Error: status 4xx or 5xx and body `{"error": {"code", "message_l1"}}`.

### Connections

Connection object in answers: `{id, name, base_url, model, extra_params, json_format, key_last4, is_active, last_test: {ok, latency_ms, message_l1, at} | null}`. A field with the full key does not exist in any answer. `json_format` is `json_object`, `json_schema` or `none` (`docs/reports/providers.md`). `api_key` may be empty only for `http://127.0.0.1` and `http://localhost` URLs (local model servers); then no `Authorization` header is sent.

| Method and path | Body | Action |
| --- | --- | --- |
| `GET /api/connections` | — | List of rows |
| `POST /api/connections` | `{name, base_url, model, api_key, extra_params?}` | Create a row. The first row becomes active |
| `PATCH /api/connections/{id}` | Any fields; `api_key` only when the key changes | Change a row |
| `DELETE /api/connections/{id}` | — | Delete the row and its key. The active row cannot be deleted: `409` |
| `POST /api/connections/{id}/activate` | — | Make the row active |
| `POST /api/connections/{id}/test` | — | Short request to the provider; answer `{ok, latency_ms, message_l1}` |
| `POST /api/connections/test` | `{base_url, model, api_key, extra_params?}` | Test an unsaved row. The key is not stored anywhere |
| `GET /api/connections/templates` | — | Provider templates (see `docs/reports/providers.md`) |

`base_url` check: scheme `https`; scheme `http` is allowed only for `127.0.0.1` and `localhost` (local model servers and the test mock). `extra_params` is a JSON object; the keys `model`, `messages`, `stream` are forbidden in it.

### Settings, scenarios, history

| Method and path | Action |
| --- | --- |
| `GET /api/settings`, `PATCH /api/settings` | All settings as one object; `l1` is the learner language code (`es-419`, `pt-BR`) or empty until confirmed |
| `GET /api/languages` | `{current, confirmed, available: [{code, name_native, name_en, html_lang}]}` — learner languages found in `voicetutor/data/l1/`; `current` is the setting or the Windows-locale suggestion |
| `GET /api/voices` | American Kokoro voices to choose from |
| `POST /api/voices/preview` | `{voice, speed}` → a short phrase in the chosen voice, `audio/wav` |
| `GET /api/scenarios`, `POST /api/scenarios`, `PATCH /api/scenarios/{id}`, `DELETE /api/scenarios/{id}` | Scenarios; built-in ones cannot be deleted |
| `GET /api/sessions` | Sessions, newest first |
| `GET /api/sessions/{id}` | Session feed with corrections and summary |
| `GET /api/sessions/{id}/export?format=json\|csv` | Session export |
| `DELETE /api/sessions/{id}` | Delete a session and its audio |
| `GET /api/turns/{id}/audio` | Turn recording, `audio/wav`; `404` when storage is off or the retention period has passed |
| `GET /api/patterns` | Recurring mistakes with counters and state |
| `GET /api/vocab`, `POST /api/vocab`, `PATCH /api/vocab/{id}`, `DELETE /api/vocab/{id}` | Vocabulary |
| `GET /api/vocab/due` | Phrases due for review today |
| `DELETE /api/data` | `{confirm: "DELETE", include_keys: bool}` — delete all data |
| `GET /api/health` | `{status, gpu: {name, vram_used_mb, vram_total_mb}, models: {stt, tts, phoneme}, active_connection, problems}`; `problems` lists startup problems (`no_gpu`, `models_missing`, `model_load_failed`) with a localized message |

### Pronunciation

| Method and path | Body | Answer |
| --- | --- | --- |
| `GET /api/pron/phrases` | — | Reading phrases with target sounds |
| `POST /api/pron/assess?phrase_id=<id>` | `audio/wav`, mono | Attempt analysis, see below |
| `POST /api/pron/assess-text` | multipart: `text`, `audio` | The same for arbitrary text |
| `GET /api/pron/reference?phrase_id=<id>&speed=1.0` | — | Reference reading by Kokoro, `audio/wav`; `text` instead of `phrase_id` for a single word |
| `POST /api/pron/feedback` | `{attempt_id, word_index, phone_index, verdict: "was_correct"}` | Shift the sensitivity offset of a sound |
| `GET /api/pron/sounds?days=7` | — | Statistics per sound: attempts, errors |

Attempt analysis (shortened):

```json
{
  "attempt_id": "…",
  "text": "I think so.",
  "duration_s": 1.4,
  "analysis_ms": 71,
  "score": 0.82,
  "words": [
    {
      "w": "think",
      "source_index": 1,
      "ipa": "θɪŋk",
      "score": 0.61,
      "level": "error",
      "phones": [
        {"expected": "θ", "heard": "s", "start": 0.42, "end": 0.51, "gop": -3.1, "level": "error", "cls": "θ", "scored": true, "catalog_id": "th_voiceless"},
        {"expected": "ɪ", "heard": "ɪ", "start": 0.51, "end": 0.58, "gop": -0.2, "level": "ok", "cls": "ɪ", "scored": true, "catalog_id": null}
      ],
      "tip": {"catalog_id": "th_voiceless", "phone_index": 0, "expected": "θ", "heard": "s", "title_l1": "…", "tip_l1": "…", "pair": ["think", "sink"]}
    }
  ]
}
```

- `level`: `ok`, `approx`, `error` — shown as "correct", "close", "error".
- Word: `source_index` is the word number in the phrase text split by spaces; `tip` is `null` when there are no marks. `heard` is an empty string when the sound was not produced and `+` followed by the sound when an extra sound was inserted (`+ɛ` in "espeak" for *speak*); the catalog is the learner language's (`voicetutor/data/l1/<code>/catalog.json`).
- Sound: `cls` is the sound class for statistics; `scored: false` means the sound is not assessed (vowels of function words, syllabic consonants); `catalog_id` is the catalog entry or `null`; `gop` is the log likelihood ratio of the expected sound against the best competitor, at most 0.
- `POST /api/pron/feedback` answers `{phone, sensitivity_offset, attempt}`: the updated attempt with the mark removed.
- Errors: `pron_no_speech` (no speech heard), `pron_bad_audio`, `pron_no_text`, `audio_too_short`, `audio_too_long` — status `422`; `pron_unavailable` — `503`.
- `pron.flags` in conversation: `expected` and `heard` are sound symbols, `word_index` is the word number in `user.transcript.words`.

## Learner language

Texts in the learner's language travel in fields ending in `_l1` (`note_l1`, `message_l1`, `tip_l1`, `title_l1`, `translation_l1`, ...). The core writes them in the current learner language (`GET /api/languages`); a session stores the language it was held in (`l1` in `GET /api/sessions`), and its corrections keep that language when the setting changes later. English fields (`quote`, `fix`, `better`, `en`, tutor text) never contain learner-language text: the language guard (`voicetutor/lang_guard.py`) checks LLM answers and every sentence before speech synthesis.

## What the core sends to the LLM provider

The only outbound exchange. Request: `POST {base_url}/chat/completions`, header `Authorization: Bearer <key>`, body `{model, messages, stream, ...extra_params}`. Corrector, summary and helpers add `response_format: {"type": "json_object"}`. `messages` contains the system prompts, the turn texts and the tutor's replies. Audio, file paths, the Windows user name and the settings never go there.
