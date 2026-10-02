"""Append verified native metadata to an unchanged, same-repository PR branch."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tomllib

WORKFLOWS = {".github/workflows/ci.yml", ".github/workflows/wheels.yml", ".github/workflows/r.yml"}
GENERATED = ("julia/Artifacts.toml", "julia/native-build.toml")


def api(endpoint: str):
    return json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))


def check_pr(pr: dict, repository: str, head: str) -> str:
    if (pr["state"] != "open" or pr["head"]["repo"]["full_name"] != repository
            or pr["head"]["sha"] != head):
        raise RuntimeError("PR closed, changed source, or belongs to another repository; refusing to push")
    return pr["head"]["ref"]


def pending_workflows(runs: list[dict], head: str) -> set[str]:
    latest = {}
    for run in runs:
        path = run["path"]
        if path in WORKFLOWS and run["head_sha"] == head and run["event"] == "pull_request":
            if path not in latest or run["id"] > latest[path]["id"]:
                latest[path] = run
    for path, run in latest.items():
        if run["status"] == "completed" and run["conclusion"] != "success":
            raise RuntimeError(f"{path} did not pass: {run['conclusion']}")
    return WORKFLOWS - {path for path, run in latest.items() if run["status"] == "completed"}


def main() -> None:
    archives = Path(sys.argv[1]).resolve()
    repository, head = os.environ["GITHUB_REPOSITORY"], os.environ["PR_HEAD"]
    endpoint = f"repos/{repository}/pulls/{os.environ['PR_NUMBER']}"
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != head:
        raise RuntimeError("checkout differs from tested PR head")
    metadata = tomllib.loads((archives / "native-build.toml").read_text())
    if metadata["source_commit"] != head or metadata["run_id"] != os.environ["GITHUB_RUN_ID"]:
        raise RuntimeError("metadata belongs to a different source or workflow run")

    # Julia's matrix is a job dependency. Wait for the other three workflows too.
    deadline = time.monotonic() + 1800
    while True:
        branch = check_pr(api(endpoint), repository, head)
        runs = api(f"repos/{repository}/actions/runs?head_sha={head}&event=pull_request&per_page=100")
        pending = pending_workflows(runs["workflow_runs"], head)
        if not pending:
            break
        if time.monotonic() >= deadline:
            raise RuntimeError(f"timed out waiting for {sorted(pending)}")
        print(f"Waiting for {sorted(pending)}", flush=True)
        time.sleep(15)

    subprocess.run(["julia", "-e", 'include("julia/build/artifacts.jl"); verify(ARGS...)',
                    str(archives), str(archives / "Artifacts.toml"),
                    str(archives / "native-build.toml")], check=True)
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        raise RuntimeError("expected a clean checkout before copying metadata")
    for path in GENERATED:
        shutil.copyfile(archives / Path(path).name, path)
    subprocess.run(["git", "add", "--", *GENERATED], check=True)
    changed = set(subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines())
    if not changed or not changed <= set(GENERATED):
        raise RuntimeError(f"unexpected staged changes: {sorted(changed)}")
    check_pr(api(endpoint), repository, head)
    subprocess.run(["git", "-c", "user.name=github-actions[bot]", "-c",
                    "user.email=41898282+github-actions[bot]@users.noreply.github.com", "commit",
                    "-m", "build(julia): pin tested native artifacts"], check=True)
    # An ordinary fast-forward push fails if another commit arrived in the meantime.
    subprocess.run(["git", "push", "origin", f"HEAD:refs/heads/{branch}"], check=True)
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
        summary.write(f"Appended native metadata to PR #{os.environ['PR_NUMBER']}. "
                      f"Source checks passed on `{head}`. Review and merge manually; tagging remains manual.\n")


if __name__ == "__main__":
    main()
