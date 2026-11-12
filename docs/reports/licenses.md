# License audit

Plan item 0.7, checked on 2026-11-12. Code license of this repository: MIT (`LICENSE`). Every third-party component keeps its own license. This report records facts from primary sources; it is not legal advice and draws no legal conclusion.

## Summary

- Nothing third-party is committed to the repository or put into the release archive except source code written for this project. Model weights, espeak-ng binaries, PyTorch with its NVIDIA libraries, fonts and the browser voice activity detector are downloaded on the user's machine by `scripts/setup.ps1` from their official distribution points (`tests/test_licenses.py::test_no_weights_or_gpl_binaries_tracked`).
- Copyleft components installed on the user's machine:
  - **espeak-ng** (GPL-3.0-or-later): a DLL and its data, bundled inside the `espeakng-loader` wheel from PyPI. Kokoro (through `misaki`) and the pronunciation reference use it.
  - **phonemizer-fork** (GPL-3.0-or-later): a Python package imported at runtime by `misaki` (the English G2P used by Kokoro).
  - **num2words** (LGPL), **soxr** (LGPL-2.1-or-later): Python libraries imported at runtime.
  - **certifi**, **tqdm** (MPL-2.0, tqdm also MIT): Python libraries.
- Owner question (no conclusion here): whether an MIT-licensed app that is installed together with, and imports at runtime, GPL-3.0-or-later components (espeak-ng through espeakng-loader, phonemizer-fork) needs a different license, an additional notice, or a different packaging. See `docs/HUMAN_TASKS.md`.
- Findings that differ from common assumptions: `@ricky0123/vad-web` is ISC (not MIT); the `espeakng-loader` wheel ships espeak-ng without a GPL text or source offer, and its PyPI metadata has no license field; Fontsource npm packages declare only OFL-1.1 for the fonts.

## Models, binaries and browser assets

| Component | Version | License | What we do with it | Primary source | Notes |
| --- | --- | --- | --- | --- | --- |
| faster-whisper-large-v3-turbo (`mobiuslabsgmbh`) | revision `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf` | MIT | Downloaded at install time into `%LOCALAPPDATA%\VoiceTutor\models` | [Model card at this revision](https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo/raw/0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf/README.md) (`license: mit`) | CTranslate2 conversion of the OpenAI model |
| whisper-large-v3-turbo (OpenAI, upstream weights) | — | MIT | Not downloaded; the converted model above derives from it | [Model card](https://huggingface.co/openai/whisper-large-v3-turbo/raw/main/README.md), [whisper LICENSE](https://raw.githubusercontent.com/openai/whisper/main/LICENSE) | Keep the "Copyright (c) 2022 OpenAI" notice in THIRD_PARTY_NOTICES |
| Kokoro-82M (`hexgrad`), weights and `voices/*.pt` | revision `f3ff3571791e39611d31c381e3a41a3af07b4987` | Apache-2.0 | Downloaded at install time | [Model card](https://huggingface.co/hexgrad/Kokoro-82M/raw/main/README.md) (`license: apache-2.0`) | The card lists CC BY 3.0 / 4.0 audio among the training data; voices have no separate license |
| wav2vec2-lv-60-espeak-cv-ft (`facebook`) | revision `ae45363bf3413b374fecd9dc8bc1df0e24c3b7f4` | Apache-2.0 | Downloaded at install time | [Model card](https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft/raw/main/README.md) (`license: apache-2.0`) | Base model `wav2vec2-large-lv60` is also Apache-2.0 |
| espeak-ng (DLL and `espeak-ng-data`) | 1.52.0, inside `espeakng-loader` 0.2.4 | GPL-3.0-or-later | Installed from PyPI as part of the `espeakng-loader` wheel; never committed or archived | [espeak-ng README](https://raw.githubusercontent.com/espeak-ng/espeak-ng/master/README.md) ("GPL version 3 or later"), [build workflow of the wheel](https://raw.githubusercontent.com/thewh1teagle/espeakng-loader/main/.github/workflows/build.yml) | Wheel content checked: `espeakng_loader/espeak-ng.dll` and 369 data entries, no COPYING file. Source: [espeak-ng 1.52.0](https://github.com/espeak-ng/espeak-ng/tree/1.52.0) |
| espeakng-loader (loader code) | 0.2.4 | MIT | Installed from PyPI | [LICENSE](https://raw.githubusercontent.com/thewh1teagle/espeakng-loader/main/LICENSE) | PyPI metadata has no license field; the table below records the GitHub license |
| phonemizer-fork | 3.3.2 | GPL-3.0-or-later | Installed from PyPI (dependency of `misaki[en]`), imported at runtime | [PyPI JSON](https://pypi.org/pypi/phonemizer-fork/json), [upstream phonemizer README](https://raw.githubusercontent.com/bootphon/phonemizer/master/README.md) | Fork of bootphon/phonemizer |
| en_core_web_sm (spaCy model) | 3.8.0 | MIT | Installed from the GitHub release wheel pinned in `uv.lock` | [Release](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0), [meta](https://raw.githubusercontent.com/explosion/spacy-models/master/meta/en_core_web_sm-3.8.0.json) | Training data note: OntoNotes 5 "licensed by Explosion", WordNet 3.0 License |
| Inter font (`@fontsource/inter`) | 5.3.0 | OFL-1.1 | Downloaded at install time into `web/fonts` (gitignored), sha512-checked | [npm tarball](https://registry.npmjs.org/@fontsource/inter/-/inter-5.3.0.tgz) (`package/LICENSE`) | The Inter Project Authors |
| JetBrains Mono font (`@fontsource/jetbrains-mono`) | 5.3.0 | OFL-1.1 | Downloaded at install time into `web/fonts`, sha512-checked | [npm tarball](https://registry.npmjs.org/@fontsource/jetbrains-mono/-/jetbrains-mono-5.3.0.tgz) | The JetBrains Mono Project Authors |
| vad-web (`@ricky0123/vad-web`) | 0.0.31 | ISC | Downloaded at install time into `web/vendor` (gitignored), sha512-checked | [npm metadata](https://registry.npmjs.org/@ricky0123/vad-web/0.0.31), [repository LICENSE](https://raw.githubusercontent.com/ricky0123/vad/master/LICENSE) | Its bundle embeds ONNX Runtime Web 1.22.0 (MIT) |
| Silero VAD models (inside vad-web) | v5 (`silero_vad_v5.onnx`) | MIT | As vad-web | [silero-vad LICENSE](https://raw.githubusercontent.com/snakers4/silero-vad/master/LICENSE) | Silero Team |
| onnxruntime-web | 1.31.1 | MIT | Downloaded at install time into `web/vendor`, sha512-checked | [npm metadata](https://registry.npmjs.org/onnxruntime-web/1.31.1), [onnxruntime LICENSE](https://raw.githubusercontent.com/microsoft/onnxruntime/main/LICENSE) | Microsoft Corporation; npm dependencies of the package were not audited because only `dist/` WASM and JS files are copied |
| PyTorch | 2.11.0+cu128 | BSD-3-Clause | Installed from `download.pytorch.org` at install time | [LICENSE](https://raw.githubusercontent.com/pytorch/pytorch/main/LICENSE) | The wheel's own license file bundles its third-party notices |
| NVIDIA CUDA libraries in `torch\lib` (cudart, cuBLAS, cuBLASLt, cuFFT, cuRAND, cuSOLVER, cuSPARSE, NVRTC, nvJitLink, CUPTI, NVTX) | CUDA 12.8 | NVIDIA CUDA EULA (proprietary) | Shipped by PyTorch inside its wheel; this project does not redistribute them | [CUDA EULA, Attachment A](https://docs.nvidia.com/cuda/eula/index.html) | Not confirmed in Attachment A: `nvperf_host.dll`, `cusolverMg64_11.dll`, `nvrtc64_120_0.alt.dll`, `zlibwapi.dll` |
| NVIDIA cuDNN libraries in `torch\lib` and `ctranslate2` | 9.x | NVIDIA cuDNN SLA (proprietary) | Shipped by PyTorch and CTranslate2 inside their wheels; not redistributed by this project | [cuDNN license](https://docs.nvidia.com/deeplearning/cudnn/latest/reference/eula.html) | "the runtime files .so and .dll" are distributable |
| Microsoft Edge | system component | Microsoft software license | Used as the window (`--app` mode); not distributed | [Microsoft Edge](https://www.microsoft.com/edge) | Preinstalled on Windows 10 22H2 and Windows 11 |

## Python packages

Generated by `scripts/license_audit.py` from the installed distributions' own metadata (`License-Expression`, `License`, trove classifiers, bundled license files) for every package pinned in `uv.lock`. Group `runtime` ships to users; `dev` is only for tests and linting. `tests/test_licenses.py` fails when the table no longer matches the lock file. Packages whose metadata has no license are reviewed above (`espeakng-loader`).

<!-- python-table:start -->
| Package | Version | Group | License | Evidence |
| --- | --- | --- | --- | --- |
| [addict](https://pypi.org/project/addict/2.4.0/) | 2.4.0 | runtime | MIT | classifier |
| [annotated-doc](https://pypi.org/project/annotated-doc/0.0.6/) | 0.0.6 | runtime | MIT | License-Expression |
| [annotated-types](https://pypi.org/project/annotated-types/0.8.0/) | 0.8.0 | runtime | MIT | License-Expression |
| [anyio](https://pypi.org/project/anyio/4.16.0/) | 4.16.0 | runtime | MIT | License-Expression |
| [attrs](https://pypi.org/project/attrs/26.1.0/) | 26.1.0 | runtime | MIT | License-Expression |
| [av](https://pypi.org/project/av/19.0.2/) | 19.0.2 | runtime | BSD-3-Clause | License-Expression |
| [babel](https://pypi.org/project/babel/2.18.0/) | 2.18.0 | runtime | BSD-3-Clause | License field (BSD) |
| [blis](https://pypi.org/project/blis/1.3.4/) | 1.3.4 | runtime | BSD | License field (BSD) |
| [catalogue](https://pypi.org/project/catalogue/2.0.10/) | 2.0.10 | runtime | MIT | License field (MIT) |
| [certifi](https://pypi.org/project/certifi/2026.10.23/) | 2026.10.23 | runtime | MPL-2.0 | License field (MPL-2.0) |
| [cffi](https://pypi.org/project/cffi/2.1.1/) | 2.1.1 | runtime | MIT-0 | License-Expression |
| [charset-normalizer](https://pypi.org/project/charset-normalizer/3.5.2/) | 3.5.2 | runtime | MIT | License field |
| [click](https://pypi.org/project/click/8.5.1/) | 8.5.1 | runtime | BSD-3-Clause | License-Expression |
| [cloudpathlib](https://pypi.org/project/cloudpathlib/0.26.0/) | 0.26.0 | runtime | MIT | classifier |
| [cloudpickle](https://pypi.org/project/cloudpickle/3.1.2/) | 3.1.2 | runtime | BSD-3-Clause | License field (BSD) |
| [colorama](https://pypi.org/project/colorama/0.4.6/) | 0.4.6 | runtime | BSD | classifier |
| [confection](https://pypi.org/project/confection/1.3.4/) | 1.3.4 | runtime | MIT | License field (MIT) |
| [csvw](https://pypi.org/project/csvw/4.2.0/) | 4.2.0 | runtime | Apache 2.0 | License field (Apache-2.0) |
| [ctranslate2](https://pypi.org/project/ctranslate2/4.9.0/) | 4.9.0 | runtime | MIT | License field |
| [curated-tokenizers](https://pypi.org/project/curated-tokenizers/0.0.10/) | 0.0.10 | runtime | MIT | License field (MIT) |
| [curated-transformers](https://pypi.org/project/curated-transformers/0.1.1/) | 0.1.1 | runtime | MIT | License field |
| [cymem](https://pypi.org/project/cymem/2.0.16/) | 2.0.16 | runtime | MIT | License field (MIT) |
| [dlinfo](https://pypi.org/project/dlinfo/2.0.0/) | 2.0.0 | runtime | MIT | License field |
| [docopt](https://pypi.org/project/docopt/0.6.2/) | 0.6.2 | runtime | MIT | License field (MIT) |
| [en-core-web-sm](https://pypi.org/project/en-core-web-sm/3.8.0/) | 3.8.0 | runtime | MIT | License field |
| [espeakng-loader](https://pypi.org/project/espeakng-loader/0.2.4/) | 0.2.4 | runtime | MIT (loader); bundles espeak-ng GPL-3.0-or-later | reviewed: GitHub LICENSE and wheel content |
| [fastapi](https://pypi.org/project/fastapi/0.162.4/) | 0.162.4 | runtime | MIT | License-Expression |
| [faster-whisper](https://pypi.org/project/faster-whisper/1.2.1/) | 1.2.1 | runtime | MIT | License field (MIT) |
| [filelock](https://pypi.org/project/filelock/4.2.10/) | 4.2.10 | runtime | MIT | License-Expression |
| [flatbuffers](https://pypi.org/project/flatbuffers/25.12.19/) | 25.12.19 | runtime | Apache 2.0 | License field (Apache-2.0) |
| [fsspec](https://pypi.org/project/fsspec/2026.9.0/) | 2026.9.0 | runtime | BSD-3-Clause | License-Expression |
| [greenlet](https://pypi.org/project/greenlet/3.5.6/) | 3.5.6 | dev | MIT AND PSF-2.0 | License-Expression |
| [h11](https://pypi.org/project/h11/0.16.0/) | 0.16.0 | runtime | MIT | License field (MIT) |
| [hf-xet](https://pypi.org/project/hf-xet/1.8.0/) | 1.8.0 | runtime | Apache-2.0 | License-Expression |
| [httpcore](https://pypi.org/project/httpcore/1.0.9/) | 1.0.9 | runtime | BSD-3-Clause | License-Expression |
| [httpcore2](https://pypi.org/project/httpcore2/2.16.0/) | 2.16.0 | runtime | BSD-3-Clause | License-Expression |
| [httpx](https://pypi.org/project/httpx/0.28.1/) | 0.28.1 | runtime | BSD-3-Clause | License field (BSD) |
| [httpx2](https://pypi.org/project/httpx2/2.16.0/) | 2.16.0 | runtime | BSD-3-Clause | License-Expression |
| [huggingface-hub](https://pypi.org/project/huggingface-hub/2.4.0/) | 2.4.0 | runtime | Apache-2.0 | License field (Apache-2.0) |
| [idna](https://pypi.org/project/idna/3.20/) | 3.20 | runtime | BSD-3-Clause | License-Expression |
| [iniconfig](https://pypi.org/project/iniconfig/2.3.1/) | 2.3.1 | dev | MIT | License-Expression |
| [isodate](https://pypi.org/project/isodate/0.7.2/) | 0.7.2 | runtime | BSD | classifier |
| [jaraco-classes](https://pypi.org/project/jaraco-classes/3.4.0/) | 3.4.0 | runtime | MIT | classifier |
| [jaraco-context](https://pypi.org/project/jaraco-context/6.1.2/) | 6.1.2 | runtime | MIT | License-Expression |
| [jaraco-functools](https://pypi.org/project/jaraco-functools/4.6.0/) | 4.6.0 | runtime | MIT | License-Expression |
| [jinja2](https://pypi.org/project/jinja2/3.1.6/) | 3.1.6 | runtime | BSD | classifier |
| [joblib](https://pypi.org/project/joblib/1.6.0/) | 1.6.0 | runtime | BSD-3-Clause | License-Expression |
| [jsonschema](https://pypi.org/project/jsonschema/4.26.0/) | 4.26.0 | runtime | MIT | License-Expression |
| [jsonschema-specifications](https://pypi.org/project/jsonschema-specifications/2025.9.1/) | 2025.9.1 | runtime | MIT | License-Expression |
| [keyring](https://pypi.org/project/keyring/25.7.0/) | 25.7.0 | runtime | MIT | License-Expression |
| [kokoro](https://pypi.org/project/kokoro/0.9.4/) | 0.9.4 | runtime | Apache-2.0 | classifier |
| [language-tags](https://pypi.org/project/language-tags/1.3.2/) | 1.3.2 | runtime | MIT | License-Expression |
| [loguru](https://pypi.org/project/loguru/0.7.3/) | 0.7.3 | runtime | MIT | classifier |
| [markdown-it-py](https://pypi.org/project/markdown-it-py/4.3.0/) | 4.3.0 | runtime | MIT | classifier |
| [markupsafe](https://pypi.org/project/markupsafe/3.0.4/) | 3.0.4 | runtime | BSD-3-Clause | License-Expression |
| [mdurl](https://pypi.org/project/mdurl/0.1.2/) | 0.1.2 | runtime | MIT | classifier |
| [misaki](https://pypi.org/project/misaki/0.9.4/) | 0.9.4 | runtime | Apache-2.0 | classifier |
| [more-itertools](https://pypi.org/project/more-itertools/11.2.1/) | 11.2.1 | runtime | MIT | License-Expression |
| [mpmath](https://pypi.org/project/mpmath/1.3.0/) | 1.3.0 | runtime | BSD | License field (BSD) |
| [murmurhash](https://pypi.org/project/murmurhash/1.0.16/) | 1.0.16 | runtime | MIT | License field (MIT) |
| [networkx](https://pypi.org/project/networkx/3.7/) | 3.7 | runtime | BSD-3-Clause | License-Expression |
| [num2words](https://pypi.org/project/num2words/0.5.14/) | 0.5.14 | runtime | LGPL | License field (GNU Library or Lesser General Public License (LGPL)) |
| [numpy](https://pypi.org/project/numpy/2.5.4/) | 2.5.4 | runtime | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | License-Expression |
| [onnxruntime](https://pypi.org/project/onnxruntime/1.31.1/) | 1.31.1 | runtime | MIT License | License field (MIT) |
| [opentelemetry-api](https://pypi.org/project/opentelemetry-api/1.45.2/) | 1.45.2 | runtime | Apache-2.0 | License-Expression |
| [packaging](https://pypi.org/project/packaging/26.3/) | 26.3 | runtime | Apache-2.0 OR BSD-2-Clause | License-Expression |
| [phonemizer-fork](https://pypi.org/project/phonemizer-fork/3.3.2/) | 3.3.2 | runtime | GNU General Public License v3 or later (GPLv3+) | classifier |
| [playwright](https://pypi.org/project/playwright/1.65.0/) | 1.65.0 | dev | Apache-2.0 | License-Expression |
| [pluggy](https://pypi.org/project/pluggy/1.7.0/) | 1.7.0 | dev | MIT | License field (MIT) |
| [preshed](https://pypi.org/project/preshed/3.0.15/) | 3.0.15 | runtime | MIT | License field (MIT) |
| [protobuf](https://pypi.org/project/protobuf/7.36.2/) | 7.36.2 | runtime | 3-Clause BSD License | License field |
| [pycparser](https://pypi.org/project/pycparser/3.12/) | 3.12 | runtime | BSD-3-Clause | License-Expression |
| [pydantic](https://pypi.org/project/pydantic/2.14.3/) | 2.14.3 | runtime | MIT | License-Expression |
| [pydantic-core](https://pypi.org/project/pydantic-core/2.50.4/) | 2.50.4 | runtime | MIT | License-Expression |
| [pygments](https://pypi.org/project/pygments/2.21.0/) | 2.21.0 | runtime | BSD-2-Clause | License-Expression |
| [pyparsing](https://pypi.org/project/pyparsing/3.3.3/) | 3.3.3 | runtime | MIT | License-Expression |
| [pytest](https://pypi.org/project/pytest/9.2.0/) | 9.2.0 | dev | MIT | License-Expression |
| [python-dateutil](https://pypi.org/project/python-dateutil/4.0.0/) | 4.0.0 | runtime | BSD-3-Clause | License-Expression |
| [python-multipart](https://pypi.org/project/python-multipart/0.0.33/) | 0.0.33 | runtime | Apache-2.0 | License-Expression |
| [pywin32-ctypes](https://pypi.org/project/pywin32-ctypes/0.2.3/) | 0.2.3 | runtime | BSD-3-Clause | License field |
| [pyyaml](https://pypi.org/project/pyyaml/6.0.3/) | 6.0.3 | runtime | MIT | License field (MIT) |
| [rdflib](https://pypi.org/project/rdflib/7.6.0/) | 7.6.0 | runtime | BSD-3-Clause | License field (BSD) |
| [referencing](https://pypi.org/project/referencing/0.37.0/) | 0.37.0 | runtime | MIT | License-Expression |
| [regex](https://pypi.org/project/regex/2026.11.9/) | 2026.11.9 | runtime | Apache-2.0 AND CNRI-Python | License-Expression |
| [requests](https://pypi.org/project/requests/2.34.2/) | 2.34.2 | runtime | Apache-2.0 | License field (Apache-2.0) |
| [rfc3986](https://pypi.org/project/rfc3986/1.5.0/) | 1.5.0 | runtime | Apache 2.0 | License field (Apache-2.0) |
| [rich](https://pypi.org/project/rich/15.0.0/) | 15.0.0 | runtime | MIT | License field (MIT) |
| [rpds-py](https://pypi.org/project/rpds-py/2026.9.1/) | 2026.9.1 | runtime | MIT | License-Expression |
| [ruff](https://pypi.org/project/ruff/0.17.4/) | 0.17.4 | dev | MIT | License-Expression |
| [safetensors](https://pypi.org/project/safetensors/0.8.0/) | 0.8.0 | runtime | Apache-2.0 | classifier |
| [segments](https://pypi.org/project/segments/2.4.0/) | 2.4.0 | runtime | Apache 2.0 | License field (Apache-2.0) |
| [setuptools](https://pypi.org/project/setuptools/81.0.0/) | 81.0.0 | runtime | MIT | License-Expression |
| [shellingham](https://pypi.org/project/shellingham/1.5.4/) | 1.5.4 | runtime | ISC License | License field (ISC) |
| [smart-open](https://pypi.org/project/smart-open/9.0.3/) | 9.0.3 | runtime | MIT | classifier |
| [soundfile](https://pypi.org/project/soundfile/0.14.0/) | 0.14.0 | runtime | BSD 3-Clause License | License field (BSD) |
| [soxr](https://pypi.org/project/soxr/1.1.0/) | 1.1.0 | runtime | LGPL-2.1-or-later | License-Expression |
| [spacy](https://pypi.org/project/spacy/3.8.18/) | 3.8.18 | runtime | MIT | License field (MIT) |
| [spacy-curated-transformers](https://pypi.org/project/spacy-curated-transformers/0.3.1/) | 0.3.1 | runtime | MIT | License field |
| [spacy-legacy](https://pypi.org/project/spacy-legacy/3.0.12/) | 3.0.12 | runtime | MIT | License field (MIT) |
| [spacy-loggers](https://pypi.org/project/spacy-loggers/1.0.5/) | 1.0.5 | runtime | MIT | License field |
| [srsly](https://pypi.org/project/srsly/2.5.6/) | 2.5.6 | runtime | MIT | License field (MIT) |
| [starlette](https://pypi.org/project/starlette/1.10.0/) | 1.10.0 | runtime | BSD-3-Clause | License-Expression |
| [sympy](https://pypi.org/project/sympy/1.14.0/) | 1.14.0 | runtime | BSD | License field (BSD) |
| [termcolor](https://pypi.org/project/termcolor/3.3.0/) | 3.3.0 | runtime | MIT | License-Expression |
| [thinc](https://pypi.org/project/thinc/8.3.14/) | 8.3.14 | runtime | MIT | License field (MIT) |
| [tokenizers](https://pypi.org/project/tokenizers/0.23.3/) | 0.23.3 | runtime | Apache-2.0 | classifier |
| [torch](https://pypi.org/project/torch/2.11.0+cu128/) | 2.11.0+cu128 | runtime | BSD-3-Clause | License field |
| [tqdm](https://pypi.org/project/tqdm/4.70.1/) | 4.70.1 | runtime | MPL-2.0 AND MIT | License field |
| [transformers](https://pypi.org/project/transformers/5.22.2/) | 5.22.2 | runtime | Apache 2.0 License | License field |
| [truststore](https://pypi.org/project/truststore/0.10.5/) | 0.10.5 | runtime | MIT | License-Expression |
| [typer](https://pypi.org/project/typer/0.29.0/) | 0.29.0 | runtime | MIT | License-Expression |
| [typing-extensions](https://pypi.org/project/typing-extensions/4.16.0/) | 4.16.0 | runtime | PSF-2.0 | License-Expression |
| [typing-inspection](https://pypi.org/project/typing-inspection/0.4.5/) | 0.4.5 | runtime | MIT | License-Expression |
| [tzdata](https://pypi.org/project/tzdata/2026.6/) | 2026.6 | runtime | Apache-2.0 | License field |
| [uritemplate](https://pypi.org/project/uritemplate/4.2.0/) | 4.2.0 | runtime | BSD 3-Clause OR Apache-2.0 | License field |
| [urllib3](https://pypi.org/project/urllib3/2.8.0/) | 2.8.0 | runtime | MIT | License-Expression |
| [uvicorn](https://pypi.org/project/uvicorn/0.54.0/) | 0.54.0 | runtime | BSD-3-Clause | License-Expression |
| [wasabi](https://pypi.org/project/wasabi/1.1.3/) | 1.1.3 | runtime | MIT | License field |
| [weasel](https://pypi.org/project/weasel/1.0.1/) | 1.0.1 | runtime | MIT | License field (MIT) |
| [websockets](https://pypi.org/project/websockets/17.4/) | 17.4 | runtime | BSD-3-Clause | License-Expression |
| [win32-setctime](https://pypi.org/project/win32-setctime/1.2.1/) | 1.2.1 | runtime | MIT license | License field (MIT) |
| [wrapt](https://pypi.org/project/wrapt/2.5.2/) | 2.5.2 | runtime | BSD-2-Clause | License-Expression |
<!-- python-table:end -->
