# Troubleshooting

Most problems show a message in the app window or in the installer console, in your language. This page explains the common ones. If none fits, see "Reporting a problem" at the end.

## Installation

<a id="install-warning"></a>
### Windows shows a security warning

The release is not signed with a code-signing certificate, so Windows may warn when you open `install.cmd` from a downloaded archive. Before extracting, right-click the `.zip` file → Properties → tick "Unblock" → OK; or choose "Run" (or "More info" → "Run anyway") in the warning. The scripts are plain text: you can read them before running.

<a id="install-requirements"></a>
### The installer stops at the requirements check

It lists what is missing (graphics card, driver, video memory, disk space) and links to the matching section of `hardware.md`. Nothing has been downloaded at that point. Fix the item and run `install.cmd` again.

<a id="install-path"></a>
### The installer complains about the folder

Extract the archive to a folder you own, for example `C:\VoiceTutor` or `Documents\VoiceTutor`, not into `Program Files` (it needs administrator rights) and not into a folder synchronized by OneDrive. Spaces in the path are fine. Accented letters are fine when Windows keeps a short name for the folder; if the installer says otherwise, choose a path without accents.

<a id="install-network"></a>
### A download fails or stops

Run `install.cmd` again: every step checks what is already in place, and the models continue where they stopped. Every file is checked against a checksum; a damaged file is downloaded again. A company proxy or firewall may block GitHub, PyPI or Hugging Face; try another network.

<a id="antivirus"></a>
### An antivirus removed files

Some antivirus programs quarantine files inside the app's Python environment. Restore them, add the Voice Tutor folder to the exceptions, and run `install.cmd` again.

## Starting the app

<a id="window"></a>
### The window does not open

The app uses Microsoft Edge as its window. If Edge was removed, install it again from microsoft.com/edge. If you start the app while it is already running, the open window comes to the front instead of a second copy.

<a id="problems"></a>
### "The conversation is not available"

| Message | What to do |
| --- | --- |
| The computer does not meet the minimum requirements | See the wizard's hardware step (the "See details" button) and `hardware.md` |
| No compatible NVIDIA graphics card | Install or update the NVIDIA driver, restart the computer and the app |
| The models were not found | Run `install.cmd` again; then open the wizard's model step and click "Check again" |
| The models could not be loaded | Restart the computer; if it repeats, run `install.cmd` again and report the problem with the diagnostics archive |

## Microphone and sound

<a id="microphone"></a>
### The tutor does not hear me

1. Windows: Settings → Privacy & security → Microphone: turn on "Microphone access" and "Let desktop apps access your microphone".
2. In the app window: click the lock icon next to the address and allow the microphone.
3. Settings → Sound and voice: choose the right microphone. The wizard's microphone step (Settings → Performance → "Run the wizard again") measures the level and the room noise.

<a id="sound"></a>
### I do not hear the tutor

Settings → Sound and voice → speakers or headphones; click "Listen" to test. Check the Windows volume mixer.

<a id="auto-mode"></a>
### Automatic mode sends my answer too early or not at all

Settings → Conversation → raise the allowed pause. In a noisy room run the wizard's microphone step again: it makes the voice detector stricter. With speakers, use manual mode or headphones; otherwise the microphone hears the tutor.

## Speed and memory

<a id="slow"></a>
### Replies are slow

- On battery a laptop slows its graphics card down: plug in the charger.
- Games, video editors and other programs that use the graphics card take its memory: close them. Settings → Performance → `compacto` uses less video memory.
- The language model's speed depends on the provider and the model: Settings → API connections → "Test" shows the time of one request.

<a id="vram"></a>
### "Not enough video memory"

Close programs that use the graphics card and repeat the answer. If it happens often, choose `compacto` in Settings → Performance. See `hardware.md`.

## The language model

<a id="llm"></a>

Messages about keys, balance, waiting or unreachable providers are explained in `api-keys.md` ("When something goes wrong").

## Reporting a problem

<a id="report"></a>

1. Run `scripts\collect_diagnostics.ps1` (right-click → Run with PowerShell). It creates an archive with versions, the hardware profile and the logs, without keys and without the text of your conversations.
2. Describe what you did, what you expected and what happened; attach the archive.

The logs are in `%LOCALAPPDATA%\VoiceTutor\logs`. Never post an API key.

## Updating and reinstalling

<a id="update"></a>

Extract the new version over the old folder (or into a new one) and run `install.cmd`. Your sessions, settings, keys and models stay in `%LOCALAPPDATA%\VoiceTutor` and the Windows Credential Manager. `uninstall.cmd` removes the app and asks before deleting your data.
