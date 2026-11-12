"""Writes voicetutor/data/model_files.json: size and SHA-256 of every model file the app uses.

For each pinned model (voicetutor/model_registry.py) the file list and the hashes Hugging Face
publishes for that revision come from ``GET https://huggingface.co/api/models/<repo>/tree/<rev>``:
large files carry their SHA-256 (``lfs.oid``), small files their git blob SHA-1 (``oid``). The
script hashes the local copies (from an earlier download) and refuses to write the manifest
unless every local file matches the published hash.

    .venv\\Scripts\\python.exe scripts\\model_manifest.py [--source <dir with the files>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()


def published(repo_id: str, revision: str) -> dict[str, dict[str, Any]]:
    import httpx

    url = f"https://huggingface.co/api/models/{repo_id}/tree/{revision}?recursive=true"
    r = httpx.get(url, timeout=60, follow_redirects=True)
    r.raise_for_status()
    return {x["path"]: x for x in r.json() if x.get("type") == "file"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "voicetutor" / "data" / "model_files.json"))
    args = ap.parse_args()

    from voicetutor.model_download import sha256_of
    from voicetutor.model_registry import ALL_MODELS, hf_snapshot_path

    models: dict[str, Any] = {}
    for model in ALL_MODELS:
        tree = published(model.repo_id, model.revision)
        local = hf_snapshot_path(model)
        files: dict[str, Any] = {}
        for name in model.allow_patterns:
            entry = tree[name]
            path = local / name
            size = path.stat().st_size
            sha256 = sha256_of(path)
            if size != entry["size"]:
                raise SystemExit(f"{model.key}/{name}: size {size} != published {entry['size']}")
            if entry.get("lfs"):
                if sha256 != entry["lfs"]["oid"]:
                    raise SystemExit(f"{model.key}/{name}: SHA-256 differs from the published one")
                source = "lfs sha256"
            else:
                if git_blob_sha1(path) != entry["oid"]:
                    raise SystemExit(f"{model.key}/{name}: git blob SHA-1 differs")
                source = "git blob sha1"
            files[name] = {"size": size, "sha256": sha256, "verified_by": source}
            print(f"  {model.key}/{name}: {size} bytes, matches the {source}")
        models[model.key] = {
            "repo_id": model.repo_id,
            "revision": model.revision,
            "license": model.license,
            "files": files,
        }
    out = Path(args.out)
    out.write_text(
        json.dumps(
            {
                "note": "Written by scripts/model_manifest.py; every hash was checked against "
                "the hashes Hugging Face publishes for the pinned revision.",
                "models": models,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
