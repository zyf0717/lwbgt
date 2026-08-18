# Benchmark method

The benchmark loads cases before timing, pins itself to the first CPU allowed by
the process affinity mask on Linux, performs one warm-up, and consumes every
output through a volatile checksum. `tests/compare.py benchmark` interleaves
reference and candidate executions and reports median rows/s and relative median
absolute deviation over seven repetitions.

The checked-in baseline used:

- CPU: 13th Gen Intel Core i9-13900HK
- OS/kernel: Linux 7.0.0-28-generic x86_64
- Compiler: GCC 13.3.0
- CMake: 3.28.3
- Core flags: GNU89, `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`
- Harness flags: C11, `-O2 -fno-fast-math -ffp-contract=off`
- Workload: deterministic HeatStressBench generator/decomposition patterns,
  representative NASA POWER and ERA5 rows, and a broad condition matrix
- Iterations: 200 per case per execution
- Repetitions: 7

Exact host, compiler, container image, affinity, source, and harness metadata
for the final runs is recorded in `optimization-3-environment.json`.

`baseline-gcc-13.3.0.json` compares two byte-identical source builds. Its 1.20×
overall gate is expected to fail before optimization; the baseline establishes
measurement parity and per-cohort noise.

## Results

| Candidate | Compiler/environment | Overall median speedup | Slowest cohort | Gate |
|---|---|---:|---:|---:|
| Optimization 1 | GCC 13.3.0 host | 1.134× | 1.130× | failed |
| Optimizations 1+2 | GCC 13.3.0 host | 1.162× | 1.123× | failed |
| Optimizations 1+2 | GCC 16.2.0 container | 1.159× | 1.141× | failed |
| Optimizations 1+2+3 | GCC 13.3.0 host | 1.316× | 1.279× | passed |
| Optimizations 1+2+3 | GCC 16.2.0 container | 1.289× | 1.253× | passed |
| v0.2.0 PIC static build | GCC 13.3.0 host | 1.248× | 1.211× | passed |

All measured cohorts exceed the no-regression floor. The v0.1.0 candidate
passes the unchanged 1.20× overall gate on both required compilers. The v0.2.0
rerun measures the position-independent object code now shared by the static
and shared libraries; it also passes the overall and per-cohort gates. Its full
result and environment are recorded in `v0.2.0-gcc-13.3.0.json` and
`v0.2.0-environment.json`.
