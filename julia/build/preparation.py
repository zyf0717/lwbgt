"""Check release preparation prerequisites and authenticate prepared archives."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib


def validate_run(run: dict, repository: str, source: str) -> None:
    if not (
        run["status"] == "completed" and run["conclusion"] == "success"
        and run["event"] == "workflow_dispatch" and run["head_branch"] == "main"
        and run["path"] == ".github/workflows/julia.yml" and run["head_sha"] == source
        and (run.get("head_repository") or {}).get("full_name") == repository
    ):
        raise RuntimeError("expected a successful manual Julia preparation on this repository's main branch")


def output(**values) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
        for key, value in values.items():
            print(f"{key}={value}", file=stream)


def preflight() -> None:
    if os.environ["GITHUB_REF"] != "refs/heads/main":
        raise RuntimeError("start release preparation on main")
    version = tomllib.loads(Path("julia/Project.toml").read_text())["version"]
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise RuntimeError("expected a stable shared release version")
    tag = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/tags/v{version}"])
    if tag.returncode == 0:
        raise RuntimeError(f"v{version} already exists; merge a new version before preparing a release")
    if tag.returncode != 1:
        raise RuntimeError("could not check existing release tags")
    output(version=version)


def check_run() -> None:
    metadata = tomllib.loads(Path("julia/native-build.toml").read_text())
    run_id, source = metadata["run_id"], metadata["source_commit"]
    if not re.fullmatch(r"[0-9]+", run_id) or not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RuntimeError("invalid preparation run ID or source commit")
    repository = os.environ["GITHUB_REPOSITORY"]
    run = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repository}/actions/runs/{run_id}"], text=True,
    ))
    validate_run(run, repository, source)
    output(run_id=run_id)


if __name__ == "__main__":
    if sys.argv[1:] == ["preflight"]:
        preflight()
    elif sys.argv[1:] == ["check-run"]:
        check_run()
    else:
        raise SystemExit("usage: preparation.py preflight | check-run")
