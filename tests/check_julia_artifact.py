"""Test a prepared Julia archive without a compiler or the repository on its load path."""

from __future__ import annotations

import functools
import http.server
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    archives = Path(sys.argv[1]).resolve()
    manifest = archives / "Artifacts.toml"
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(archives))
    with tempfile.TemporaryDirectory() as temporary:
        package = Path(temporary, "LWBGT")
        shutil.copytree(ROOT / "julia", package,
                        ignore=shutil.ignore_patterns("build", "Manifest.toml", "native-build.toml"))
        env = dict(os.environ, JULIA_DEPOT_PATH=str(Path(temporary, "depot")),
                   JULIA_NUM_THREADS="4", JULIA_PKG_SERVER="")
        env.pop("LWBGT_LIBRARY", None)
        with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                subprocess.run([
                    "julia", "--startup-file=no", str(ROOT / "julia/test/artifacts.jl"),
                    str(package), str(manifest), f"http://127.0.0.1:{server.server_port}",
                ], env=env, check=True)
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    main()
