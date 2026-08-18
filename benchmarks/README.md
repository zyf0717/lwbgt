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

`baseline-gcc-13.3.0.json` compares two byte-identical source builds. Its 1.20×
overall gate is expected to fail before optimization; the baseline establishes
measurement parity and per-cohort noise.
