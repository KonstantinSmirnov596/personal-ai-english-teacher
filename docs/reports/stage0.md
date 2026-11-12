# Stage 0 report: transfer and foundation check

## Result

Stage 0 is closed: `scripts/check_stage.ps1 0` exits with 0 (repeated setup, `fast`, `gpu` and `e2e` green under the new name, all required tests passed). Open owner questions do not block stage 1.

## Hardware facts (SPEC 7)

Checked on 2026-11-12 against official sources and the installed packages.

| Question | Answer | Evidence |
| --- | --- | --- |
| Compute capabilities in the torch `cu128` Windows wheel (2.11.0) | sm_75, sm_80, sm_86, sm_90, sm_100, sm_120 — native code only, no PTX; Turing (7.5) is the oldest | Build script [`cuda_config.bat` at v2.11.0](https://github.com/pytorch/pytorch/blob/v2.11.0/.ci/pytorch/windows/internal/cuda_config.bat): `CUDA_ARCH_LIST=7.5;8.0;8.6;9.0;10.0;12.0`; [RELEASE.md](https://github.com/pytorch/pytorch/blob/release/2.12/RELEASE.md): 2.11 supports "Turing(7.5), Ampere(8.0, 8.6), Hopper(9.0), Blackwell(10.0, 12.0)"; [2.11 release notes](https://github.com/pytorch/pytorch/releases/tag/v2.11.0): Volta dropped from the 12.8 binaries; local `torch.cuda.get_arch_list()` returns the same list (`tests/gpu/test_stage0.py::test_torch_arch_list_covers_minimum`) |
| CUDA version of the torch Windows wheel | CUDA 12.8.0, cuDNN 9.19 | [`cuda_install.bat` at v2.11.0](https://github.com/pytorch/pytorch/blob/v2.11.0/.ci/pytorch/windows/internal/cuda_install.bat); local `torch.version.cuda` = 12.8, `cudnn.version()` = 91900 |
| Compute capabilities in the CTranslate2 4.9.0 Windows wheel | Native code for sm_53, sm_60, sm_61, sm_70, sm_75, sm_80, sm_86 plus PTX for compute_86 (newer GPUs such as sm_120 run the PTX through the driver's JIT) | Build script [`prepare_build_environment_windows.sh` at v4.9.0](https://github.com/OpenNMT/CTranslate2/blob/v4.9.0/python/tools/prepare_build_environment_windows.sh): `-DCMAKE_CUDA_ARCHITECTURES="53-real;60-real;61-real;70-real;75-real;80-real;86"`; [CMake: no suffix = real and virtual](https://cmake.org/cmake/help/latest/prop_tgt/CUDA_ARCHITECTURES.html); local `cuobjdump --list-elf/--list-ptx` on the installed `ctranslate2.dll` shows exactly these targets |
| CUDA version of the CTranslate2 4.9.0 Windows wheel | CUDA 12.8.1 (installer `cuda_12.8.1_572.61_windows.exe`); cuBLAS is loaded at runtime (`cublas64_12.dll`, here from `torch\lib`), `cudnn64_9.dll` is in the wheel | Same build script; [`cublas_stub.cc` at v4.9.0](https://github.com/OpenNMT/CTranslate2/blob/v4.9.0/src/cuda/cublas_stub.cc); [faster-whisper README, GPU](https://github.com/SYSTRAN/faster-whisper/blob/v1.2.1/README.md): "cuBLAS for CUDA 12" and "cuDNN 9 for CUDA 12" |
| Minimum NVIDIA driver on Windows for CUDA 12.8 | 12.8 GA: ≥ 570.65; 12.8 Update 1: ≥ 572.61. **Requirement set to 572.61 or newer**, because CTranslate2 4.9.0 is built with 12.8.1 and newer GPUs need the PTX JIT, which minor-version compatibility does not cover | [CUDA release notes, "Corresponding Driver Versions"](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html): "CUDA 12.8 Update 1 … >=572.61", "CUDA 12.8 GA … >=570.65"; [12.8.0 archive](https://docs.nvidia.com/cuda/archive/12.8.0/cuda-toolkit-release-notes/index.html); [minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html): "Applications that compile device code to PTX will not work on older drivers." The [12.8.1 archive](https://docs.nvidia.com/cuda/archive/12.8.1/cuda-toolkit-release-notes/index.html) lists GA as ≥ 572.30 (NVIDIA's own inconsistency); 572.61 satisfies both |
| `float16` and `int8_float16` in CTranslate2 on the minimum architecture | Both supported on Turing: float16 needs compute capability ≥ 7.0; on 7.0–7.9 `int8_float16` and `float16` run as requested, only `bfloat16` falls back to `float32` | [CTranslate2 quantization (4.9.0 docs)](https://opennmt.net/CTranslate2/quantization.html): "NVIDIA GPU with Compute Capability >= 7.0" for float16 and int8; bfloat16 needs ≥ 8.0; fallback table row ">= 7.0, < 8.0" |
| Development machine | NVIDIA GeForce RTX 5060 Laptop GPU, compute capability 12.0, 8151 MiB, driver 610.47 | `nvidia-smi`, `torch.cuda.get_device_capability` |

Conclusion: the SPEC minimum stands — NVIDIA Turing (GTX 1660 / RTX 2060 class) with 6 GB of VRAM — and no document needs to move to Ampere. The minimum driver is 572.61. Not confirmed: NVIDIA's [CUDA GPUs page](https://developer.nvidia.com/cuda-gpus) lists GeForce RTX 2060 and GTX 1650 Ti under 7.5 but not the GTX 1660 by name; the user docs therefore give "RTX 2060" as the confirmed Turing example and tell users to check their card's compute capability with the installer's requirement check (stage 3) rather than rely on the model name. PyTorch publishes no driver minimum of its own.

## Measurements

Development machine: RTX 5060 Laptop GPU 8 GB, driver 610.47. All runs on 2026-11-12, under the new package name. Raw data: `docs/reports/data/bench_stage0.json`, `bench_turn.json`, `startup.json`, `network_audit.json`.

During every run another process (the predecessor's windowless core, see "Did not work") held about 3.9 GB of VRAM; Windows moved part of it to system memory when the tests needed room. Latency was not visibly affected (the numbers match or beat the predecessor's), but the VRAM deltas below are device-wide differences measured while another process's allocations could be evicted, so they are lower bounds. Stage 3 repeats the VRAM measurements on a free GPU.

| Metric | Target | Measured | How |
| --- | --- | --- | --- |
| STT of a 10 s turn | ≤ 0.4 s | 0.299 s warm median (max 0.301 s); 0.306 s cold | `scripts/bench.py`, 5 warm runs, `beam_size=1` |
| STT of a 4.5 s turn | — | 0.257 s warm median | `scripts/bench.py` |
| TTS first sentence | ≤ 0.3 s | 0.086 s warm median; 1.149 s cold (first call after load) | `scripts/bench.py`, 5.15 s of audio |
| End of turn → first audio, mock 0 ms | ≤ 0.9 s | 0.399 s median, 0.402 s max (window clock); cold 0.687 s | `scripts/bench_turn.py`, 5 runs, `turn_basic` fixture |
| End of turn → first audio, mock 500 ms | ≤ 1.5 s | 0.907 s median, 0.925 s max; cold 0.897 s | `scripts/bench_turn.py`, 5 runs |
| VRAM, all three models | ≤ 6.5 GB of 8 | 3.56 GB device-wide delta (STT 2.15 GB, TTS 0.76 GB, phoneme 0.37 GB, CUDA context 0.11 GB); lower bound, see above | `nvidia-smi` before and after each load in `scripts/bench.py` |
| WER, TTS → STT loop, 10 phrases | ≤ 10 % | 0.0 % | `scripts/bench.py` and `tests/gpu/test_stage0.py::test_tts_stt_loop_wer` |
| Phoneme model, 5 s phrase | — | 0.013 s warm median | `scripts/bench.py` |
| Startup to models ready | ≤ 20 s | 15.1–15.9 s (window 2.2–2.3 s) | `tests/gpu/test_startup.py`, 2 runs |
| Outbound connections in a full scenario | only the LLM host | 0 outside `127.0.0.1` (3 connections: 2 to the mock LLM, 1 local) | `tests/gpu/test_network.py` |

## Checks

`scripts/check_stage.ps1 0` on 2026-11-12: repeated `scripts/setup.ps1` OK, then:

| Suite | Passed | Failed | Skipped | Note |
| --- | --- | --- | --- | --- |
| `fast` | 128 | 0 | 0 | Includes `test_hygiene` (9), `test_licenses` (4), `test_providers` (2), the new connection, client and launcher tests |
| `gpu` | 26 | 0 | 0 | Includes `test_cuda_device_meets_minimum`, `test_torch_arch_list_covers_minimum`, loop WER, network audit, startup |
| `e2e` | 11 | 0 | 0 | Edge with fake microphone: conversation, auto mode, helpers, summary, reading, pronunciation marks, shortcut |
| `live` | — | — | — | Not part of stage 0; no key saved |

Required tests: the predecessor's 60 required tests (its stages 0–4) under the new name plus 19 new ones (`scripts/check_stage.py`, `STAGES[0]`). Reports checked: `stage0.md`, `licenses.md`, `providers.md` (no placeholders, no empty table cells).

## Decisions and deviations

- Package `voicetutor`, data dir `%LOCALAPPDATA%\VoiceTutor`, env prefix `VOICETUTOR_`, keyring service `VoiceTutor`, cookie `voicetutor_session`; `uv.lock` re-locked only for the project name (122 pins unchanged).
- Developer docs (`design.md`, `protocol.md`, `testing.md`, `docs/ui/README.md`) rewritten in English without owner-specific content (laptop, ERP/ECM, document workflow, Russian-speaker framing); the UI mockups now show Latin American Spanish.
- The predecessor's Russian locale stays as allowlisted data until item 1.10; every other file is free of Cyrillic (`tests/test_hygiene.py`).
- The predecessor's required tests are kept verbatim (`PREDECESSOR_TESTS` in `scripts/check_stage.py`) except the dev-machine check `test_cuda_device_is_rtx5060`, replaced by `test_cuda_device_meets_minimum` (NVIDIA, capability ≥ 7.5).
- Provider templates (`docs/reports/providers.md`): six templates; connections get `json_format` (`json_object`, `json_schema`, `none`, migration 4) because LM Studio documents only `json_schema` and OpenAI prefers it; local servers may run without a key.
- License audit (`docs/reports/licenses.md`): no third-party binaries or weights in the repository; GPL-3.0-or-later components (espeak-ng via `espeakng-loader`, `phonemizer-fork`) are installed from PyPI on the user's machine; the compatibility question goes to the owner without a legal conclusion.
- All decisions with reasons: `docs/PROGRESS.md` → Decisions.

## Did not work

- **Unstable `e2e` while another process holds VRAM.** The predecessor's core has been running without a window since 2026-11-11 22:12 and holds about 3.9 GB of VRAM. Its own log says "window closed and not reconnected for 10 s: exiting" at 23:24, but the process never ended. With it running, the test core (about 3.6 GB) and the other process together exceed the 8 GB card; Windows then pages video memory and some end-to-end runs hit their 60 s timeouts. Two of three `e2e` runs had one or three failures, the acceptance run passed completely; each failing test passed when run again alone. Not stopped by Claude Code because it is the owner's process outside the project; question in `docs/HUMAN_TASKS.md`.
- **The same shutdown hang exists in the inherited launcher.** Fixed: uvicorn now drops open connections after 5 s of graceful shutdown, and an exit watchdog ends the process 30 s after the core decided to exit (`tests/test_launcher.py::test_exit_watchdog_ends_a_process_with_a_stuck_thread`).
- **VRAM per model** cannot be measured precisely while another process's allocations are being evicted; repeated in stage 3.

## Needed from the owner

- Decide whether the predecessor's windowless core may be stopped (it holds 3.9 GB of VRAM and makes GPU tests flaky and stage 3 measurements impossible).
- GPL compatibility question from the license audit.
- Author identity for the public git history; copyright line in `LICENSE`; whether `docs/SPEC.md` and `docs/BASELINE_REPORT.md` are published.
- Details and defaults: `docs/HUMAN_TASKS.md` → Question queue.
