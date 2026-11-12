# Installing Voice Tutor

Installation takes one double-click and no administrator rights. You do not need Python or any other tool: the installer brings its own. Plan for 20–60 minutes, depending on your internet connection; most of the time goes into downloading about 8 GB.

## Before you start

- Check the requirements in `hardware.md`: an NVIDIA graphics card of the GeForce RTX 20 series or newer with 6 GB of video memory, driver 572.61 or newer, Windows 10 22H2 or Windows 11, 16 GB of RAM.
- Keep about 15 GB free on the drive where you put the app and on the drive with your user profile.
- Have an API key ready, or a local model server (see `api-keys.md`). You can also add it later.

## Download

<a id="download"></a>

Download `VoiceTutor-<version>.zip` from the project's Releases page on GitHub. Next to it, `SHA256SUMS.txt` lists its checksum; to verify it, open PowerShell in the download folder and compare:

```powershell
Get-FileHash .\VoiceTutor-0.1.0.zip -Algorithm SHA256
```

## Extract

<a id="extract"></a>

1. Right-click the `.zip` → Properties → tick "Unblock" → OK. This avoids security warnings for each script.
2. Extract it to a folder of your own with a short path, for example `C:\VoiceTutor` or `Documents\VoiceTutor`. Avoid `Program Files` (needs administrator rights) and folders synchronized by OneDrive.

## Install

<a id="install"></a>

Double-click `install.cmd`. A console window shows each step:

1. **Requirements.** The installer checks the graphics card, driver, video memory, disk space and memory before downloading anything. If something blocking is missing, it says what and stops (see `hardware.md`).
2. **Folders.** It checks that the app folder and your data folder can be written and that the path is usable.
3. **Tools and Python.** It downloads the `uv` tool and Python 3.12 into the app folder. Nothing is added to the system or to `PATH`.
4. **Packages.** About 5 GB of Python packages (PyTorch with CUDA, speech libraries), exactly the versions listed in `uv.lock`.
5. **Models.** About 3.2 GB of speech models into `%LOCALAPPDATA%\VoiceTutor\models`. If the connection drops, run `install.cmd` again: the download continues where it stopped.
6. **Fonts and the voice detector** for the app window.
7. **Shortcuts.** It asks whether to put shortcuts on the Desktop and in the Start menu (press Enter for yes). A shortcut is always created in the app folder.

Every download is pinned to an exact version and checked against a checksum. When everything is done, Voice Tutor starts and its first-run wizard opens.

## First start

<a id="first-start"></a>

The wizard guides you through eight steps: language, hardware check, models, a short measurement, microphone, voice, API connection and level. Each step can be repeated later from Settings → Performance. `usage.md` explains the app.

## Updating

<a id="update"></a>

Download the new version, extract it over the old folder (or into a new one) and run `install.cmd` again. Only what changed is downloaded. Your sessions, settings, keys and models stay.

## Uninstalling

<a id="uninstall"></a>

Double-click `uninstall.cmd`. It removes the Python environment, the downloaded tools and the shortcuts. It asks separately whether to delete your data (`%LOCALAPPDATA%\VoiceTutor`) and your API keys; without a "yes" they stay. Afterwards you can delete the app folder.

## If something goes wrong

See `troubleshooting.md`. `install.cmd` can always be run again: it continues where it stopped.
