"""Reject stale PR validation and unsuccessful or unexpectedly skipped checks."""

import json
import os
from pathlib import Path
import subprocess
import sys


def validate_current(expected: dict, current: dict) -> None:
    if current["state"] != "open" or any(
        current[side]["sha"] != expected[side]["sha"] for side in ("head", "base")
    ):
        raise RuntimeError("PR head or base changed, or PR closed; update the branch and approve a fresh run")


def validate_results(needs: dict) -> None:
    metadata = needs["approve"]["outputs"].get("metadata_only")
    if metadata not in ("true", "false"):
        raise RuntimeError("PR classification did not complete")
    expected = {"approve": "success", "julia": "success"}
    expected.update(dict.fromkeys(
        ("native", "python", "r"), "skipped" if metadata == "true" else "success"
    ))
    for job, result in expected.items():
        actual = needs[job]["result"]
        if actual != result:
            raise RuntimeError(f"{job}: expected {result}, got {actual}")


def main() -> None:
    if sys.argv[1:] == ["current"]:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        repository = os.environ["GITHUB_REPOSITORY"]
        current = json.loads(subprocess.check_output(
            ["gh", "api", f"repos/{repository}/pulls/{event['number']}"], text=True,
        ))
        validate_current(event["pull_request"], current)
        print(f"Current PR revision: head={current['head']['sha']} base={current['base']['sha']}")
    elif sys.argv[1:] == ["results"]:
        validate_results(json.loads(os.environ["VALIDATION_NEEDS"]))
        print("All selected PR checks passed")
    else:
        raise SystemExit("usage: pr_validation.py current | results")


if __name__ == "__main__":
    main()
