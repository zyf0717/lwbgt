# Benchmark

The fixed workload contains 840 rows from the historical 852-case corpus,
excluding six `invalid` and six `solver-boundary` rows. The expanded numerical
suite stays separate so the timing workload remains comparable.

The harness loads input before timing, pins execution to one CPU, warms each
run, and consumes outputs through a volatile checksum. It alternates original
and current kernels for seven repetitions of 200 iterations per case and
reports medians.

On 2026-09-25, median throughput was **1.603×** the retained original:

| Overall, 840 rows | Original | Current |
|---|---:|---:|
| Median rows/s | 60,423 | 96,834 |
| Relative median absolute deviation | 0.50% | 0.57% |

All cohort gates passed. Environment: GCC 13.3.0, Linux 7.0.0-31-generic,
Intel Core i9-13900HK, CPU 12 without a sibling hardware thread. Both kernels
used GNU89 and `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`.

Reproduce on the same machine from the repository root:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
python3 tests/generate_cases.py build/cases.csv
taskset -c 12 python3 tests/compare.py benchmark \
  build/lwbgt_reference_benchmark build/lwbgt_benchmark build/cases.csv \
  build/benchmark.json 7 200
```

Results depend on hardware, compiler, and workload. The two `era5` rows are
fixed London examples without recorded dataset provenance, so they do not
establish ERA5-wide performance. See [the numerical baseline](../tests/BASELINE.md)
for expanded correctness checks.
