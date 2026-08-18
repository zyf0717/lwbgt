#!/usr/bin/env python3
"""Generate deterministic equivalence and benchmark cohorts."""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

HEADER = (
    "case_id", "cohort", "year", "month", "day", "hour", "minute", "gmt",
    "avg", "lat", "lon", "solar", "pressure", "air", "rh", "wind",
    "wind_height", "vertical_delta", "urban",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_cases.py OUTPUT.csv")
    rows: list[tuple[object, ...]] = []

    def add(cohort: str, *values: object) -> None:
        rows.append((f"case-{len(rows) + 1:05d}", cohort, *values))

    # HeatStressBench generator-n known-answer endpoints.
    add("hsb-generated", 2024, 3, 21, 7, 0, 0, 0, 14.515380, -91.977540,
        0.0, 1010.0, 42.543334, 31.5, 0.821752, 2.0, 0.0, 0)
    add("hsb-generated", 2024, 9, 22, 13, 0, 0, 0, 11.359619, 11.997070,
        933.496093, 1010.0, 20.215454, 52.0, 3.763891, 2.0, 0.0, 0)

    # Representative normalized NASA POWER and ERA5 rows.
    add("nasa-power", 2024, 4, 15, 14, 30, 8, 60, 1.3521, 103.8198,
        742.0, 1008.4, 32.1, 68.0, 2.8, 10.0, -0.4, 1)
    add("nasa-power", 2024, 4, 15, 2, 30, 8, 60, 1.3521, 103.8198,
        0.0, 1009.7, 27.0, 88.0, 1.1, 10.0, 0.2, 1)
    add("era5", 2023, 7, 18, 15, 30, 0, 60, 51.5074, -0.1278,
        612.5, 1004.2, 28.4, 55.0, 4.7, 10.0, -0.8, 0)
    add("era5", 2023, 1, 18, 3, 30, 0, 60, 51.5074, -0.1278,
        0.0, 1018.6, 2.3, 91.0, 3.2, 10.0, 0.5, 0)

    # Cartesian coverage of day/night, radiation, humidity, wind, height,
    # wind conversion, and averaging policy.
    for hour, solar, rh, wind, height, urban, avg in itertools.product(
        (0, 12), (0.0, 80.0, 950.0), (5.0, 50.0, 99.0),
        (0.0, 0.13, 8.0), (2.0, 10.0), (0, 1), (0, 60),
    ):
        if len(rows) >= 438:
            break
        add("matrix", 2024, 6, 21, hour, 30, 0, avg, 35.0, -80.0,
            solar, 1010.0, 35.0, rh, wind, height, 1.5, urban)

    # Solver/domain boundary coverage, including known pressure-pole cases.
    for pressure, wind in ((225.0, 0.099), (225.0, 0.101), (300.0, 0.129),
                           (300.0, 0.131), (500.0, 0.099), (700.0, 0.131)):
        add("solver-boundary", 2024, 3, 20, 12, 0, 0, 0, 0.0, 0.0,
            1000.0, pressure, 60.0, 100.0, wind, 2.0, 0.0, 0)
    for air, rh, solar, wind in (
        (-50.0, 0.01, 0.0, 0.0), (60.0, 99.99, 1100.0, 0.129),
        (0.0, 100.0, 0.0, 0.131), (45.0, 1.0, 1.0, 40.0),
    ):
        add("domain-edge", 1950, 1, 1, 0, 0, -12, 180, 89.9, -179.9,
            solar, 200.0, air, rh, wind, 10.0, -20.0, 1)

    # Finite but physically invalid inputs remain oracle-defined regression cases.
    for pressure, rh, solar, wind, height in (
        (1010.0, -1.0, 500.0, 2.0, 2.0),
        (1010.0, 101.0, 500.0, 2.0, 2.0),
        (1010.0, 50.0, -10.0, 2.0, 2.0),
        (1010.0, 50.0, 500.0, -1.0, 2.0),
        (0.0, 50.0, 500.0, 2.0, 2.0),
        (1010.0, 50.0, 500.0, 2.0, 0.0),
    ):
        add("invalid", 2049, 12, 31, 23, 59, 12, 30, -89.9, 179.9,
            solar, pressure, 25.0, rh, wind, height, 20.0, 0)

    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="ascii", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(rows)


if __name__ == "__main__":
    main()
