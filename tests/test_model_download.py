"""Model downloads of the installer (plan item 4.1): resume after a broken connection, checksums.

A local HTTP server with Range support stands in for Hugging Face; it can cut a response after a
number of bytes. The download function gets its base URL as an argument (installer code, not the
app; the app never downloads).
"""

from __future__ import annotations

import hashlib
import http.server
import json
import os
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest

from voicetutor import model_download as md

REVISION = "0123456789abcdef0123456789abcdef01234567"


class Files(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), Handler)
        self.files: dict[str, bytes] = {}
        self.cut_after: int | None = None  # close the connection after this many body bytes
        self.ranges: list[str | None] = []
        self.corrupt = 0  # serve this many corrupted bodies first


class Handler(http.server.BaseHTTPRequestHandler):
    server: Files

    def log_message(self, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        name = self.path.split(f"/resolve/{REVISION}/", 1)[-1]
        body = self.server.files.get(name)
        if body is None:
            self.send_error(404)
            return
        if self.server.corrupt:
            self.server.corrupt -= 1
            body = bytes(b ^ 0xFF for b in body)
        rng = self.headers.get("Range")
        self.server.ranges.append(rng)
        start = 0
        if rng:
            start = int(rng.removeprefix("bytes=").split("-")[0])
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{len(body) - 1}/{len(body)}")
        else:
            self.send_response(200)
        chunk = body[start:]
        self.send_header("Content-Length", str(len(chunk)))
        self.end_headers()
        if self.server.cut_after is not None:
            self.wfile.write(chunk[: self.server.cut_after])
            self.server.cut_after = None
            self.wfile.flush()
            self.connection.close()
            return
        self.wfile.write(chunk)


@pytest.fixture
def server() -> Iterator[Files]:
    srv = Files()
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv
    srv.shutdown()


def spec_for(srv: Files, files: dict[str, bytes]) -> md.ModelSpec:
    srv.files = files
    return md.ModelSpec(
        key="demo",
        repo_id="org/demo",
        revision=REVISION,
        files=tuple(
            md.FileSpec(name, len(data), hashlib.sha256(data).hexdigest())
            for name, data in files.items()
        ),
    )


def base(srv: Files) -> str:
    return f"http://127.0.0.1:{srv.server_address[1]}"


def test_download_resume_after_a_broken_connection(server: Files, tmp_path: Path) -> None:
    data = os.urandom(3 * md.CHUNK + 12345)
    spec = spec_for(server, {"model.bin": data, "config.json": b'{"a": 1}'})
    server.cut_after = md.CHUNK + 1000
    with pytest.raises(httpx.HTTPError):
        md.ensure(spec, root=tmp_path, base_url=base(server))
    part = tmp_path / "demo" / REVISION / "config.json.part"
    partial = sorted((tmp_path / "demo" / REVISION).glob("*.part"))
    assert partial and partial[0].stat().st_size > 0
    del part
    # second run: continues with a Range request instead of starting over
    root = md.ensure(spec, root=tmp_path, base_url=base(server))
    assert (root / "model.bin").read_bytes() == data
    assert (root / "config.json").read_bytes() == b'{"a": 1}'
    assert any(r and r != "bytes=0-" for r in server.ranges), server.ranges
    assert not list(root.glob("*.part"))
    assert md.is_present(spec, tmp_path)


def test_damaged_download_is_fetched_again_once(server: Files, tmp_path: Path) -> None:
    data = os.urandom(50_000)
    spec = spec_for(server, {"model.bin": data})
    server.corrupt = 1
    root = md.ensure(spec, root=tmp_path, base_url=base(server))
    assert (root / "model.bin").read_bytes() == data
    server.corrupt = 5
    (root / "model.bin").unlink()
    with pytest.raises(md.ChecksumError):
        md.ensure(spec, root=tmp_path, base_url=base(server))
    assert not (root / "model.bin").exists() and not list(root.glob("*.part"))


def test_verified_files_are_not_downloaded_again(server: Files, tmp_path: Path) -> None:
    spec = spec_for(server, {"model.bin": b"x" * 1000})
    md.ensure(spec, root=tmp_path, base_url=base(server))
    server.ranges.clear()
    md.ensure(spec, root=tmp_path, base_url=base(server))
    assert server.ranges == []


def test_an_existing_copy_is_adopted_only_when_it_matches(server: Files, tmp_path: Path) -> None:
    data = b"weights" * 1000
    spec = spec_for(server, {"model.bin": data})
    good = tmp_path / "old" / "good.bin"
    good.parent.mkdir()
    good.write_bytes(data)
    md.ensure(spec, root=tmp_path / "a", base_url=base(server), adopt=lambda f: good)
    assert server.ranges == []  # nothing downloaded
    bad = tmp_path / "old" / "bad.bin"
    bad.write_bytes(b"other" * 10)
    md.ensure(spec, root=tmp_path / "b", base_url=base(server), adopt=lambda f: bad)
    assert len(server.ranges) == 1
    assert (tmp_path / "b" / "demo" / REVISION / "model.bin").read_bytes() == data


def test_manifest_covers_the_pinned_models() -> None:
    from voicetutor.model_registry import ALL_MODELS

    m = md.manifest()
    assert set(m) == {x.key for x in ALL_MODELS}
    for model in ALL_MODELS:
        spec = m[model.key]
        assert (spec.repo_id, spec.revision) == (model.repo_id, model.revision)
        assert {f.path for f in spec.files} == set(model.allow_patterns)
        assert all(len(f.sha256) == 64 and f.size > 0 for f in spec.files)
    raw = json.loads(md.MANIFEST_PATH.read_text(encoding="utf-8"))
    sources = {f["verified_by"] for m in raw["models"].values() for f in m["files"].values()}
    assert sources <= {"lfs sha256", "git blob sha1"}
