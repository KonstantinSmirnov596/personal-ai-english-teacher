"""Installs the pinned models (``scripts/setup.ps1``, step 5). Safe to run repeatedly.

Every file is checked against ``voicetutor/data/model_files.json`` (size and SHA-256). Missing
files are downloaded from Hugging Face at the pinned commit, resuming a broken download; a copy
in the Hugging Face cache of an earlier installation is reused when its SHA-256 matches.
"""

from __future__ import annotations

import sys

from voicetutor import model_download as md
from voicetutor.model_registry import ALL_MODELS, hf_snapshot_path
from voicetutor.paths import configure_model_env


class Progress:
    """One line per file and roughly every 5 % (the installer console is not a terminal UI)."""

    def __init__(self) -> None:
        self.last: dict[str, float] = {}

    def __call__(self, name: str, done: int, total: int) -> None:
        pct = 100.0 * done / max(total, 1)
        if done >= total or pct - self.last.get(name, -100.0) >= 5.0:
            self.last[name] = pct
            print(
                f"    {name}: {done / 2**20:,.0f} / {total / 2**20:,.0f} MB ({pct:.0f} %)",
                flush=True,
            )


def main() -> int:
    models_dir = configure_model_env()
    print(f"models directory: {models_dir}")
    manifest = md.manifest()
    progress = Progress()
    for model in ALL_MODELS:
        spec = manifest[model.key]
        print(f"  {model.key}: {spec.repo_id}@{spec.revision[:8]}", flush=True)

        def adopt(f: md.FileSpec, model=model):  # noqa: ANN001, ANN202
            try:
                path = hf_snapshot_path(model) / f.path
            except Exception:
                return None
            return path if path.is_file() and path.stat().st_size == f.size else None

        try:
            root = md.ensure(spec, progress=progress, adopt=adopt)
        except md.ChecksumError as e:
            print(f"checksum: {e}", file=sys.stderr)
            return 2
        print(f"  {model.key}: verified -> {root}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
