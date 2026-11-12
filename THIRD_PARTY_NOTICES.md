# Third-party notices

Voice Tutor's own code is licensed under the MIT license (`LICENSE`). The repository and the release archive contain only that code. The installer (`install.cmd`) downloads the components below onto your computer from their official distribution points; each keeps its own license. The full license audit with sources is in `docs/reports/licenses.md`.

## Models

| Component | License | Source |
| --- | --- | --- |
| faster-whisper-large-v3-turbo (CTranslate2 conversion by Mobius Labs of OpenAI's Whisper large-v3-turbo) | MIT; Whisper: Copyright (c) 2022 OpenAI | [Hugging Face](https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo), [Whisper license](https://github.com/openai/whisper/blob/main/LICENSE) |
| Kokoro-82M by hexgrad, weights and American English voices | Apache-2.0 | [Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M) |
| wav2vec2-lv-60-espeak-cv-ft by Facebook AI | Apache-2.0 | [Hugging Face](https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft) |
| en_core_web_sm 3.8.0 by Explosion | MIT | [GitHub release](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0) |

## Copyleft components

These are installed as Python packages from PyPI and used at run time. Voice Tutor does not modify them.

| Component | License | Source code |
| --- | --- | --- |
| espeak-ng 1.52 (library and data, inside the `espeakng-loader` package) | GPL-3.0-or-later | [github.com/espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng) |
| phonemizer-fork | GPL-3.0-or-later | [pypi.org/project/phonemizer-fork](https://pypi.org/project/phonemizer-fork/) |
| num2words | LGPL (version not stated in its metadata) | [pypi.org/project/num2words](https://pypi.org/project/num2words/) |
| soxr | LGPL-2.1-or-later | [pypi.org/project/soxr](https://pypi.org/project/soxr/) |

## Window assets

| Component | License | Source |
| --- | --- | --- |
| Inter font (The Inter Project Authors) | SIL Open Font License 1.1 | [@fontsource/inter 5.3.0](https://www.npmjs.com/package/@fontsource/inter) |
| JetBrains Mono font (The JetBrains Mono Project Authors) | SIL Open Font License 1.1 | [@fontsource/jetbrains-mono 5.3.0](https://www.npmjs.com/package/@fontsource/jetbrains-mono) |
| vad-web 0.0.31 (Ricky Samore) | ISC | [@ricky0123/vad-web](https://www.npmjs.com/package/@ricky0123/vad-web) |
| Silero VAD v5 model (Silero Team), inside vad-web | MIT | [snakers4/silero-vad](https://github.com/snakers4/silero-vad) |
| ONNX Runtime Web 1.31.1 (Microsoft Corporation) | MIT | [onnxruntime-web](https://www.npmjs.com/package/onnxruntime-web) |

## Runtime and system components

| Component | License | Note |
| --- | --- | --- |
| Python 3.12 (python-build-standalone) | Python Software Foundation License | Installed by `uv` into the app folder |
| uv 0.13.7 (Astral) | MIT or Apache-2.0 | Installer tool, downloaded from its GitHub release |
| PyTorch 2.11.0 (CUDA 12.8 build) | BSD-3-Clause | Its wheel carries its own third-party notices |
| NVIDIA CUDA and cuDNN runtime libraries | NVIDIA CUDA EULA and cuDNN license (proprietary) | Shipped inside the PyTorch and CTranslate2 wheels; Voice Tutor does not redistribute them |
| Microsoft Edge | Microsoft software license | Part of Windows; used as the app window |

## Python packages installed at run time

Generated from `uv.lock` by `scripts/license_audit.py --notices THIRD_PARTY_NOTICES.md`; the evidence for each license is in `docs/reports/licenses.md`.

<!-- runtime-packages:start -->
| Package | Version | License |
| --- | --- | --- |
| [addict](https://pypi.org/project/addict/2.4.0/) | 2.4.0 | MIT |
| [annotated-doc](https://pypi.org/project/annotated-doc/0.0.6/) | 0.0.6 | MIT |
| [annotated-types](https://pypi.org/project/annotated-types/0.8.0/) | 0.8.0 | MIT |
| [anyio](https://pypi.org/project/anyio/4.16.0/) | 4.16.0 | MIT |
| [attrs](https://pypi.org/project/attrs/26.1.0/) | 26.1.0 | MIT |
| [av](https://pypi.org/project/av/19.0.2/) | 19.0.2 | BSD-3-Clause |
| [babel](https://pypi.org/project/babel/2.18.0/) | 2.18.0 | BSD-3-Clause |
| [blis](https://pypi.org/project/blis/1.3.4/) | 1.3.4 | BSD |
| [catalogue](https://pypi.org/project/catalogue/2.0.10/) | 2.0.10 | MIT |
| [certifi](https://pypi.org/project/certifi/2026.10.23/) | 2026.10.23 | MPL-2.0 |
| [cffi](https://pypi.org/project/cffi/2.1.1/) | 2.1.1 | MIT-0 |
| [charset-normalizer](https://pypi.org/project/charset-normalizer/3.5.2/) | 3.5.2 | MIT |
| [click](https://pypi.org/project/click/8.5.1/) | 8.5.1 | BSD-3-Clause |
| [cloudpathlib](https://pypi.org/project/cloudpathlib/0.26.0/) | 0.26.0 | MIT |
| [cloudpickle](https://pypi.org/project/cloudpickle/3.1.2/) | 3.1.2 | BSD-3-Clause |
| [colorama](https://pypi.org/project/colorama/0.4.6/) | 0.4.6 | BSD |
| [confection](https://pypi.org/project/confection/1.3.4/) | 1.3.4 | MIT |
| [csvw](https://pypi.org/project/csvw/4.2.0/) | 4.2.0 | Apache 2.0 |
| [ctranslate2](https://pypi.org/project/ctranslate2/4.9.0/) | 4.9.0 | MIT |
| [curated-tokenizers](https://pypi.org/project/curated-tokenizers/0.0.10/) | 0.0.10 | MIT |
| [curated-transformers](https://pypi.org/project/curated-transformers/0.1.1/) | 0.1.1 | MIT |
| [cymem](https://pypi.org/project/cymem/2.0.16/) | 2.0.16 | MIT |
| [dlinfo](https://pypi.org/project/dlinfo/2.0.0/) | 2.0.0 | MIT |
| [docopt](https://pypi.org/project/docopt/0.6.2/) | 0.6.2 | MIT |
| [en-core-web-sm](https://pypi.org/project/en-core-web-sm/3.8.0/) | 3.8.0 | MIT |
| [espeakng-loader](https://pypi.org/project/espeakng-loader/0.2.4/) | 0.2.4 | MIT (loader); bundles espeak-ng GPL-3.0-or-later |
| [fastapi](https://pypi.org/project/fastapi/0.162.4/) | 0.162.4 | MIT |
| [faster-whisper](https://pypi.org/project/faster-whisper/1.2.1/) | 1.2.1 | MIT |
| [filelock](https://pypi.org/project/filelock/4.2.10/) | 4.2.10 | MIT |
| [flatbuffers](https://pypi.org/project/flatbuffers/25.12.19/) | 25.12.19 | Apache 2.0 |
| [fsspec](https://pypi.org/project/fsspec/2026.9.0/) | 2026.9.0 | BSD-3-Clause |
| [h11](https://pypi.org/project/h11/0.16.0/) | 0.16.0 | MIT |
| [hf-xet](https://pypi.org/project/hf-xet/1.8.0/) | 1.8.0 | Apache-2.0 |
| [httpcore](https://pypi.org/project/httpcore/1.0.9/) | 1.0.9 | BSD-3-Clause |
| [httpcore2](https://pypi.org/project/httpcore2/2.16.0/) | 2.16.0 | BSD-3-Clause |
| [httpx](https://pypi.org/project/httpx/0.28.1/) | 0.28.1 | BSD-3-Clause |
| [httpx2](https://pypi.org/project/httpx2/2.16.0/) | 2.16.0 | BSD-3-Clause |
| [huggingface-hub](https://pypi.org/project/huggingface-hub/2.4.0/) | 2.4.0 | Apache-2.0 |
| [idna](https://pypi.org/project/idna/3.20/) | 3.20 | BSD-3-Clause |
| [isodate](https://pypi.org/project/isodate/0.7.2/) | 0.7.2 | BSD |
| [jaraco-classes](https://pypi.org/project/jaraco-classes/3.4.0/) | 3.4.0 | MIT |
| [jaraco-context](https://pypi.org/project/jaraco-context/6.1.2/) | 6.1.2 | MIT |
| [jaraco-functools](https://pypi.org/project/jaraco-functools/4.6.0/) | 4.6.0 | MIT |
| [jinja2](https://pypi.org/project/jinja2/3.1.6/) | 3.1.6 | BSD |
| [joblib](https://pypi.org/project/joblib/1.6.0/) | 1.6.0 | BSD-3-Clause |
| [jsonschema](https://pypi.org/project/jsonschema/4.26.0/) | 4.26.0 | MIT |
| [jsonschema-specifications](https://pypi.org/project/jsonschema-specifications/2025.9.1/) | 2025.9.1 | MIT |
| [keyring](https://pypi.org/project/keyring/25.7.0/) | 25.7.0 | MIT |
| [kokoro](https://pypi.org/project/kokoro/0.9.4/) | 0.9.4 | Apache-2.0 |
| [language-tags](https://pypi.org/project/language-tags/1.3.2/) | 1.3.2 | MIT |
| [loguru](https://pypi.org/project/loguru/0.7.3/) | 0.7.3 | MIT |
| [markdown-it-py](https://pypi.org/project/markdown-it-py/4.3.0/) | 4.3.0 | MIT |
| [markupsafe](https://pypi.org/project/markupsafe/3.0.4/) | 3.0.4 | BSD-3-Clause |
| [mdurl](https://pypi.org/project/mdurl/0.1.2/) | 0.1.2 | MIT |
| [misaki](https://pypi.org/project/misaki/0.9.4/) | 0.9.4 | Apache-2.0 |
| [more-itertools](https://pypi.org/project/more-itertools/11.2.1/) | 11.2.1 | MIT |
| [mpmath](https://pypi.org/project/mpmath/1.3.0/) | 1.3.0 | BSD |
| [murmurhash](https://pypi.org/project/murmurhash/1.0.16/) | 1.0.16 | MIT |
| [networkx](https://pypi.org/project/networkx/3.7/) | 3.7 | BSD-3-Clause |
| [num2words](https://pypi.org/project/num2words/0.5.14/) | 0.5.14 | LGPL |
| [numpy](https://pypi.org/project/numpy/2.5.4/) | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| [onnxruntime](https://pypi.org/project/onnxruntime/1.31.1/) | 1.31.1 | MIT License |
| [opentelemetry-api](https://pypi.org/project/opentelemetry-api/1.45.2/) | 1.45.2 | Apache-2.0 |
| [packaging](https://pypi.org/project/packaging/26.3/) | 26.3 | Apache-2.0 OR BSD-2-Clause |
| [phonemizer-fork](https://pypi.org/project/phonemizer-fork/3.3.2/) | 3.3.2 | GNU General Public License v3 or later (GPLv3+) |
| [preshed](https://pypi.org/project/preshed/3.0.15/) | 3.0.15 | MIT |
| [protobuf](https://pypi.org/project/protobuf/7.36.2/) | 7.36.2 | 3-Clause BSD License |
| [pycparser](https://pypi.org/project/pycparser/3.12/) | 3.12 | BSD-3-Clause |
| [pydantic](https://pypi.org/project/pydantic/2.14.3/) | 2.14.3 | MIT |
| [pydantic-core](https://pypi.org/project/pydantic-core/2.50.4/) | 2.50.4 | MIT |
| [pygments](https://pypi.org/project/pygments/2.21.0/) | 2.21.0 | BSD-2-Clause |
| [pyparsing](https://pypi.org/project/pyparsing/3.3.3/) | 3.3.3 | MIT |
| [python-dateutil](https://pypi.org/project/python-dateutil/4.0.0/) | 4.0.0 | BSD-3-Clause |
| [python-multipart](https://pypi.org/project/python-multipart/0.0.33/) | 0.0.33 | Apache-2.0 |
| [pywin32-ctypes](https://pypi.org/project/pywin32-ctypes/0.2.3/) | 0.2.3 | BSD-3-Clause |
| [pyyaml](https://pypi.org/project/pyyaml/6.0.3/) | 6.0.3 | MIT |
| [rdflib](https://pypi.org/project/rdflib/7.6.0/) | 7.6.0 | BSD-3-Clause |
| [referencing](https://pypi.org/project/referencing/0.37.0/) | 0.37.0 | MIT |
| [regex](https://pypi.org/project/regex/2026.11.9/) | 2026.11.9 | Apache-2.0 AND CNRI-Python |
| [requests](https://pypi.org/project/requests/2.34.2/) | 2.34.2 | Apache-2.0 |
| [rfc3986](https://pypi.org/project/rfc3986/1.5.0/) | 1.5.0 | Apache 2.0 |
| [rich](https://pypi.org/project/rich/15.0.0/) | 15.0.0 | MIT |
| [rpds-py](https://pypi.org/project/rpds-py/2026.9.1/) | 2026.9.1 | MIT |
| [safetensors](https://pypi.org/project/safetensors/0.8.0/) | 0.8.0 | Apache-2.0 |
| [segments](https://pypi.org/project/segments/2.4.0/) | 2.4.0 | Apache 2.0 |
| [setuptools](https://pypi.org/project/setuptools/81.0.0/) | 81.0.0 | MIT |
| [shellingham](https://pypi.org/project/shellingham/1.5.4/) | 1.5.4 | ISC License |
| [smart-open](https://pypi.org/project/smart-open/9.0.3/) | 9.0.3 | MIT |
| [soundfile](https://pypi.org/project/soundfile/0.14.0/) | 0.14.0 | BSD 3-Clause License |
| [soxr](https://pypi.org/project/soxr/1.1.0/) | 1.1.0 | LGPL-2.1-or-later |
| [spacy](https://pypi.org/project/spacy/3.8.18/) | 3.8.18 | MIT |
| [spacy-curated-transformers](https://pypi.org/project/spacy-curated-transformers/0.3.1/) | 0.3.1 | MIT |
| [spacy-legacy](https://pypi.org/project/spacy-legacy/3.0.12/) | 3.0.12 | MIT |
| [spacy-loggers](https://pypi.org/project/spacy-loggers/1.0.5/) | 1.0.5 | MIT |
| [srsly](https://pypi.org/project/srsly/2.5.6/) | 2.5.6 | MIT |
| [starlette](https://pypi.org/project/starlette/1.10.0/) | 1.10.0 | BSD-3-Clause |
| [sympy](https://pypi.org/project/sympy/1.14.0/) | 1.14.0 | BSD |
| [termcolor](https://pypi.org/project/termcolor/3.3.0/) | 3.3.0 | MIT |
| [thinc](https://pypi.org/project/thinc/8.3.14/) | 8.3.14 | MIT |
| [tokenizers](https://pypi.org/project/tokenizers/0.23.3/) | 0.23.3 | Apache-2.0 |
| [torch](https://pypi.org/project/torch/2.11.0+cu128/) | 2.11.0+cu128 | BSD-3-Clause |
| [tqdm](https://pypi.org/project/tqdm/4.70.1/) | 4.70.1 | MPL-2.0 AND MIT |
| [transformers](https://pypi.org/project/transformers/5.22.2/) | 5.22.2 | Apache 2.0 License |
| [truststore](https://pypi.org/project/truststore/0.10.5/) | 0.10.5 | MIT |
| [typer](https://pypi.org/project/typer/0.29.0/) | 0.29.0 | MIT |
| [typing-extensions](https://pypi.org/project/typing-extensions/4.16.0/) | 4.16.0 | PSF-2.0 |
| [typing-inspection](https://pypi.org/project/typing-inspection/0.4.5/) | 0.4.5 | MIT |
| [tzdata](https://pypi.org/project/tzdata/2026.6/) | 2026.6 | Apache-2.0 |
| [uritemplate](https://pypi.org/project/uritemplate/4.2.0/) | 4.2.0 | BSD 3-Clause OR Apache-2.0 |
| [urllib3](https://pypi.org/project/urllib3/2.8.0/) | 2.8.0 | MIT |
| [uvicorn](https://pypi.org/project/uvicorn/0.54.0/) | 0.54.0 | BSD-3-Clause |
| [wasabi](https://pypi.org/project/wasabi/1.1.3/) | 1.1.3 | MIT |
| [weasel](https://pypi.org/project/weasel/1.0.1/) | 1.0.1 | MIT |
| [websockets](https://pypi.org/project/websockets/17.4/) | 17.4 | BSD-3-Clause |
| [win32-setctime](https://pypi.org/project/win32-setctime/1.2.1/) | 1.2.1 | MIT license |
| [wrapt](https://pypi.org/project/wrapt/2.5.2/) | 2.5.2 | BSD-2-Clause |
<!-- runtime-packages:end -->
