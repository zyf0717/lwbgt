#!/usr/bin/env python3
"""Run byte-exact differential tests and interleaved throughput comparisons."""

from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def run(command: list[str]) -> bytes:
    return subprocess.run(command, check=True, stdout=subprocess.PIPE).stdout


def exact(reference: str, candidate: str, cases: str) -> None:
    expected = run([reference, cases])
    actual = run([candidate, cases])
    if actual != expected:
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        for ordinal, (left, right) in enumerate(
            zip(expected_lines, actual_lines, strict=False), start=1
        ):
            if left != right:
                raise SystemExit(
                    f"exact mismatch at output line {ordinal}:\n"
                    f"reference: {left.decode()}\ncandidate: {right.decode()}"
                )
        raise SystemExit("exact output lengths differ")
    print(json.dumps({
        "cases": max(0, len(expected.splitlines()) - 1),
        "sha256": hashlib.sha256(expected).hexdigest(),
        "status": "bit-identical",
    }, sort_keys=True))


def measured(executable: str, cases: str, iterations: int) -> dict[str, float]:
    payload = json.loads(run([executable, cases, str(iterations)]))
    return {key: float(value) for key, value in payload["rows_per_second"].items()}


def benchmark(reference: str, candidate: str, cases: str, output: str,
              repetitions: int, iterations: int) -> None:
    samples: dict[str, dict[str, list[float]]] = {
        "reference": defaultdict(list), "candidate": defaultdict(list)
    }
    for repetition in range(repetitions):
        order = (("reference", reference), ("candidate", candidate))
        if repetition % 2:
            order = tuple(reversed(order))
        for name, executable in order:
            for cohort, rate in measured(executable, cases, iterations).items():
                samples[name][cohort].append(rate)

    cohorts: dict[str, object] = {}
    passed = True
    for cohort in sorted(samples["reference"]):
        reference_values = samples["reference"][cohort]
        candidate_values = samples["candidate"][cohort]
        reference_median = statistics.median(reference_values)
        candidate_median = statistics.median(candidate_values)
        speedup = candidate_median / reference_median
        floor = 1.20 if cohort == "overall" else 0.98
        cohort_passed = speedup >= floor
        passed &= cohort_passed
        cohorts[cohort] = {
            "candidate_median_rows_s": candidate_median,
            "candidate_relative_mad": statistics.median(
                abs(value - candidate_median) for value in candidate_values
            ) / candidate_median,
            "gate": floor,
            "passed": cohort_passed,
            "reference_median_rows_s": reference_median,
            "reference_relative_mad": statistics.median(
                abs(value - reference_median) for value in reference_values
            ) / reference_median,
            "speedup": speedup,
        }
    report = {
        "cohorts": cohorts,
        "iterations_per_case": iterations,
        "method": "single-thread, pinned CPU, one warm-up, interleaved executions",
        "passed": passed,
        "repetitions": repetitions,
    }
    Path(output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    if not passed:
        raise SystemExit(1)


def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == "exact":
        exact(sys.argv[2], sys.argv[3], sys.argv[4])
        return
    if len(sys.argv) == 8 and sys.argv[1] == "benchmark":
        benchmark(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
                  int(sys.argv[6]), int(sys.argv[7]))
        return
    raise SystemExit(
        "usage: compare.py exact REF CANDIDATE CASES | "
        "compare.py benchmark REF CANDIDATE CASES OUT REPS ITERATIONS"
    )


if __name__ == "__main__":
    main()
