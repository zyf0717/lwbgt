# Benchmark method

The benchmark loads cases before timing, pins itself to the first CPU allowed by
the process affinity mask on Linux, performs one warm-up, and consumes every
output through a volatile checksum. `tests/compare.py benchmark` interleaves
reference and candidate executions and reports median rows/s and relative median
absolute deviation over seven repetitions. The timing harness excludes the
`invalid` and `solver-boundary` cohorts; oracle comparisons still include them.

## Current run

The current oracle input has 852 deterministic cases, including 400 successful
cases that span every supported year and the changed numerical paths. The
benchmark times 840 rows after excluding six `invalid` and six
`solver-boundary` cases. The workload contains no downloaded weather dataset;
the two `era5` rows are fixed London examples in
[`tests/generate_cases.py`](../tests/generate_cases.py), with no recorded source
provenance. Results for that cohort describe only those two rows.

On 2026-09-23, the workload was measured on the 13th Gen Intel Core
i9-13900HK, Linux 7.0.0-31-generic x86-64, GCC 13.3.0, and CMake 3.28.3.
The core used GNU89 and the harness used C11. Both used `-O2`,
`-fno-fast-math`, `-ffp-contract=off`, and `-fno-strict-aliasing`.
Each execution used 200 iterations per case, with seven interleaved repetitions.

| Cohort | Reference median rows/s | Derivative median rows/s | Speedup | Gate |
|---|---:|---:|---:|---|
| Overall, 840 rows | 144,271 | 192,546 | 1.335× | passed, ≥1.20× |

Every per-cohort gate passed. The complete medians and variability are in
[`expanded-gcc-13.3.0.json`](expanded-gcc-13.3.0.json).

Reproduce the measurement from the repository root:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
python3 tests/generate_cases.py build/cases.csv
python3 tests/compare.py benchmark \
  build/lwbgt_reference_benchmark build/lwbgt_benchmark build/cases.csv \
  build/benchmark.json 7 200
```
