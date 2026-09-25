# Benchmark

The benchmark compares the retained original Liljegren C with the current
kernel on the same 840 deterministic rows. The full 852-case corpus is used for
numerical comparison; timing excludes six `invalid` and six `solver-boundary`
rows. The harness loads cases before timing, pins execution to one CPU, warms
up each run, and consumes all outputs through a volatile checksum. The two
variants run in alternating order for seven repetitions of 200 iterations per
case. Reported rates are medians.

On 2026-09-25, the current kernel measured **1.603×** the retained original on
GCC 13.3.0, Linux 7.0.0-31-generic, and an Intel Core i9-13900HK restricted
to CPU 12, which has no sibling hardware thread. Both kernels used GNU89,
`-O2`, `-fno-fast-math`, `-ffp-contract=off`, and `-fno-strict-aliasing`.

| Overall, 840 rows | Original | Current |
|---|---:|---:|
| Median rows/s | 60,423 | 96,834 |
| Relative median absolute deviation | 0.50% | 0.57% |

Every cohort met the existing performance gate. Reproduce this comparison from
the repository root on the same machine with:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
python3 tests/generate_cases.py build/cases.csv
taskset -c 12 python3 tests/compare.py benchmark \
  build/lwbgt_reference_benchmark build/lwbgt_benchmark build/cases.csv \
  build/benchmark.json 7 200
```

The workload contains no downloaded weather dataset. Its two `era5` rows are
fixed London examples with no recorded source provenance, so that cohort is
not evidence about ERA5-wide performance. Throughput depends on the CPU,
compiler, and workload.
