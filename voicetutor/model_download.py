"""Model downloads for the installer (plan item 4.1): pinned revisions, resume, SHA-256.

Only ``python -m voicetutor.setup_models`` (run by ``scripts/setup.ps1``) calls this module; the
app never downloads anything. Each file comes from
``https://huggingface.co/<repo>/resolve/<revision>/<path>`` and is stored as
``<models dir>/<key>/<revision>/<path>``. A partial download stays as ``<path>.part`` and is
resumed with an HTTP ``Range`` request. Every file is checked against
``voicetutor/data/model_files.json`` (size and SHA-256, cross-checked against the hashes Hugging
Face publishes for the pinned revision); a damaged file is deleted and downloaded once more.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from voicetutor.paths import models_dir

HF_BASE = "https://huggingface.co"
CHUNK = 1 << 20
MANIFEST_PATH = Path(__file__).resolve().parent / "data" / "model_files.json"

Progress = Callable[[str, int, int], None]  # (file, bytes done, bytes total)


class ChecksumError(RuntimeError):
    """A downloaded file does not match the manifest."""


@dataclass(frozen=True)
class FileSpec:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class ModelSpec:
    key: str
    repo_id: str
    revision: str
    files: tuple[FileSpec, ...]


def manifest(path: Path = MANIFEST_PATH) -> dict[str, ModelSpec]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, ModelSpec] = {}
    for key, m in data["models"].items():
        files = tuple(
            FileSpec(name, int(f["size"]), str(f["sha256"])) for name, f in m["files"].items()
        )
        out[key] = ModelSpec(key, m["repo_id"], m["revision"], files)
    return out


def model_root(spec: ModelSpec, root: Path | None = None) -> Path:
    return (root or models_dir()) / spec.key / spec.revision


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(CHUNK):
            h.update(block)
    return h.hexdigest()


def is_present(spec: ModelSpec, root: Path | None = None) -> bool:
    """Quick check used by the app: every file exists with the expected size."""
    base = model_root(spec, root)
    return all(
        (base / f.path).is_file() and (base / f.path).stat().st_size == f.size for f in spec.files
    )


def download_file(
    client: httpx.Client,
    url: str,
    dest: Path,
    spec: FileSpec,
    progress: Progress | None = None,
) -> None:
    """Download one file into ``dest``, resuming ``dest.part``; verify size and SHA-256."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    offset = part.stat().st_size if part.exists() else 0
    if offset > spec.size:
        part.unlink()
        offset = 0
    if offset < spec.size:
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with client.stream("GET", url, headers=headers, follow_redirects=True) as r:
            if r.status_code == 206 and offset:
                mode = "ab"
            elif r.status_code == 200:
                mode, offset = "wb", 0  # the server ignored the range: start over
            else:
                r.raise_for_status()
                raise httpx.HTTPStatusError(
                    f"unexpected status {r.status_code}", request=r.request, response=r
                )
            done = offset
            with part.open(mode) as f:
                for block in r.iter_bytes(CHUNK):
                    f.write(block)
                    done += len(block)
                    if progress:
                        progress(spec.path, done, spec.size)
    if part.stat().st_size != spec.size or sha256_of(part) != spec.sha256:
        part.unlink(missing_ok=True)
        raise ChecksumError(f"{spec.path}: size or SHA-256 does not match the manifest")
    part.replace(dest)


def ensure(
    spec: ModelSpec,
    *,
    root: Path | None = None,
    base_url: str = HF_BASE,
    client: httpx.Client | None = None,
    progress: Progress | None = None,
    adopt: Callable[[FileSpec], Path | None] | None = None,
) -> Path:
    """Make every file of ``spec`` present and verified. ``adopt`` may offer an existing copy
    of a file (an older installation's cache); it is used only if its SHA-256 matches."""
    base = model_root(spec, root)
    own = client is None
    client = client or httpx.Client(timeout=httpx.Timeout(60.0, connect=20.0))
    try:
        for f in spec.files:
            dest = base / f.path
            if dest.is_file() and dest.stat().st_size == f.size and sha256_of(dest) == f.sha256:
                continue
            dest.unlink(missing_ok=True)
            if adopt is not None and (src := adopt(f)) is not None:
                dest.parent.mkdir(parents=True, exist_ok=True)
                _link_or_copy(src, dest)
                if sha256_of(dest) == f.sha256:
                    continue
                dest.unlink()
            url = f"{base_url}/{spec.repo_id}/resolve/{spec.revision}/{f.path}"
            try:
                download_file(client, url, dest, f, progress)
            except ChecksumError:
                download_file(client, url, dest, f, progress)  # once more, from scratch
    finally:
        if own:
            client.close()
    return base


def _link_or_copy(src: Path, dest: Path) -> None:
    import shutil

    try:
        dest.hardlink_to(src)
    except OSError:
        shutil.copyfile(src, dest)
