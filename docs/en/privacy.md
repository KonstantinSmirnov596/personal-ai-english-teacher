# Privacy

Voice Tutor is a desktop app without accounts, analytics or telemetry. This page lists exactly what leaves your computer, what stays on it and how to delete it.

## What leaves the computer

<a id="llm"></a>
### While you practice

Only one kind of traffic: HTTPS requests to the base URL of your active API connection (or `http://127.0.0.1` for a local server such as Ollama). They contain:

- the text of the conversation: the tutor's lines and the transcript of your answers;
- the scenario and your level, so the tutor can adapt;
- for corrections, translations, hints and the summary: the sentences they are about.

They never contain audio, your name, your Windows user name, hardware details or the keys of your other connections. The provider's own privacy policy applies to what it receives; read it before choosing a provider, or use a local server.

The app does not check for updates, does not send crash reports, and loads no fonts, scripts or images from the internet. A test (`tests/gpu/test_network.py`) records every connection the app opens during a full session and fails if any goes elsewhere than the LLM.

<a id="install"></a>
### During installation

`install.cmd` downloads, once: the `uv` tool from its GitHub release, Python from the `python-build-standalone` releases on GitHub, Python packages from PyPI and the PyTorch package index, the speech models from Hugging Face, and the fonts and voice detector from the npm registry. Every download is pinned to an exact version and checked against a checksum. Nothing about you is sent beyond what any download sends (your IP address).

## What stays on the computer

<a id="local"></a>

Everything else lives in `%LOCALAPPDATA%\VoiceTutor`:

| What | Where | How long |
| --- | --- | --- |
| Sessions, transcripts, corrections, vocabulary, pronunciation results, settings, hardware measurements | `voicetutor.db` (SQLite) | Until you delete them |
| Recordings of your answers | `audio\` | 30 days by default (Settings → Data; 0 keeps none) |
| Logs | `logs\` | At most 6 files of 2 MB; the oldest is replaced |
| Speech models | `models\` | Until you uninstall |
| The app window's browser profile (microphone permission) | `edge-profile\` | Until you uninstall |

API keys are stored in the Windows Credential Manager under the name `VoiceTutor`, never in a file, a log or the database. The window only receives the last four characters of a key.

<a id="logs"></a>
### Logs

By default the logs contain no text of your conversations: only events, timings and error codes. For a bug report you can turn on Settings → Data → "Detailed log", which also writes the text of each turn; the window warns you, and you should turn it off again afterwards. `scripts\collect_diagnostics.ps1` packs versions, the profile and the logs for a bug report and removes keys and turn text from them.

<a id="server"></a>
### The local server

The app's core listens only on `127.0.0.1` (your own computer), on the first free port from 47613 to 47622. It accepts only the app window: a one-time launch token, a session cookie and checks of the `Origin` and `Host` headers keep other websites and programs out.

## Deleting your data

<a id="delete"></a>

- Settings → Data → "Delete all data" removes sessions, corrections, statistics, vocabulary and recordings; tick the box to remove API connections and their keys too. Settings stay.
- Settings → Data → "Export all data" saves everything as JSON or CSV first, if you want a copy.
- `uninstall.cmd` removes the app, its Python environment and shortcuts; it asks before removing `%LOCALAPPDATA%\VoiceTutor` and your keys.
