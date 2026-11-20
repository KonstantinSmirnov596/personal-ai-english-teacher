# Hardware requirements

Personal AI English Teacher recognizes your speech, speaks as the tutor and checks your pronunciation on your own computer, with your NVIDIA graphics card. No audio leaves the computer. This page explains each item that the installer (`install.cmd`) and the first-run wizard check, and what to do when one is not met.

## Minimum and recommended

| Component | Minimum | Recommended |
| --- | --- | --- |
| Windows | Windows 10 22H2 (build 19045) or Windows 11, 64-bit | Windows 11 |
| Graphics card | NVIDIA, Turing architecture or newer (GeForce RTX 20 series and newer), 6 GB of video memory | NVIDIA with 8 GB or more |
| NVIDIA driver | 572.61 or newer | The latest stable driver |
| Memory (RAM) | 16 GB | 16 GB or more |
| Disk | 15 GB free for the installation, an SSD | 20 GB free |
| Microphone | Any | A headset or headphones |
| Network | For the installation and for the language model | — |

The installer stops before downloading anything when a blocking item is not met, and says which one. The wizard shows the same items again on its second step, with the free video memory measured at that moment.

## What each check means

<a id="gpu"></a>
### Graphics card

Speech recognition (Whisper), the tutor's voice (Kokoro) and the pronunciation check (wav2vec2) run on an NVIDIA graphics card with CUDA. A computer with only Intel or AMD graphics cannot run them. If your computer has two graphics cards (a laptop with Intel and NVIDIA), make sure the NVIDIA driver is installed: the check uses the first NVIDIA card it finds.

<a id="driver"></a>
### NVIDIA driver

The app uses CUDA 12.8 Update 1, which needs driver 572.61 or newer ([CUDA release notes, "Corresponding Driver Versions"](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)). Update the driver from [nvidia.com/drivers](https://www.nvidia.com/drivers) or the NVIDIA app, restart the computer and run the installer again. When the check says the driver is missing, Windows is using a generic display driver: install NVIDIA's.

<a id="architecture"></a>
### Card architecture

The CUDA libraries the app uses contain code for compute capability 7.5 (Turing) and newer. The GeForce RTX 20 series (for example the RTX 2060) is the oldest confirmed generation. Older cards (GTX 10 series, compute capability 6.1) are not supported. The check reads the compute capability from the driver, so you do not need to look up your model.

<a id="vram"></a>
### Video memory

The installer and the app need a card with about 6 GB of video memory. The wizard measures the *free* video memory, because the Windows desktop, browsers and games use part of it:

- 7 GB free or more: profile `completo`;
- 5 to 7 GB free: profile `compacto`;
- less than 5 GB free on a card that is otherwise fine: close games, video editors and other programs that use the graphics card, then click "Check again". If you continue, the app uses `compacto`.

On the development computer (8 GB card) the app used at most 3.7 GB in `completo` and 2.5 GB in `compacto` during a full session.

<a id="ram"></a>
### Memory (RAM)

With less than 16 GB the app still runs, but loading the models and the app window together with other programs can make it slow. This is a warning, not a blocker.

<a id="disk"></a>
### Disk space

The installation needs about 15 GB: the Python environment (about 5 GB), the models (about 3.2 GB) and the package cache (about 5 GB). While the app runs, recordings, logs and the database need some space: keep at least 2 GB free.

<a id="power"></a>
### Power

On battery, a laptop slows its graphics card down to save energy, and the tutor answers later. The app shows a one-time notice; plug in the charger for the best speed.

<a id="windows"></a>
### Windows version

The app is tested on Windows 10 22H2 and Windows 11. An older build only produces a warning; if something does not work, update Windows first.

## Profiles

<a id="profiles"></a>

| Profile | When | Speech recognition | Pronunciation model |
| --- | --- | --- | --- |
| `completo` | 7 GB of video memory free or more | Whisper turbo, `float16` | Stays in memory once loaded; pronunciation marks in the conversation are on |
| `compacto` | 5 to 7 GB free | Whisper turbo, `int8_float16` (less memory, the same accuracy in our tests) | Loaded when "Reading" or a check needs it, unloaded after 5 minutes idle; pronunciation marks in the conversation are off by default |

The wizard's measurement step (about a minute) confirms the profile. `completo` is lowered to `compacto` when the time from the end of your answer to the tutor's first sound (without the language model) is above 1.2 s, or when less than 0.8 GB of video memory stays free after loading.

To choose a profile yourself, open Settings → Performance. "Automatic" follows the measurement. The page also shows the last measurement and runs the wizard again.

## When video memory runs short

If you start a game or another program that uses the graphics card while practicing:

- the app first frees the pronunciation model;
- if speech recognition still runs out of memory, the app says so and asks you to close other programs; it does not close itself;
- recent NVIDIA drivers on Windows can also borrow system memory when video memory is full ([NVIDIA: system memory fallback](https://nvidia.custhelp.com/app/answers/detail/a_id/5490/~/system-memory-fallback-for-stable-diffusion)). Everything keeps working, only slower.

When the graphics card or its driver changes, the app offers to run the hardware check and the measurement again at the next start.
