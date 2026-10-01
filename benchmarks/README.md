# Throughput benchmark

Compare the retained original and current scalar kernels using the same
35,976-row corpus as the numerical tests, at 1× and 10×.

Each scale repeats the complete corpus in order. All rows are timed, including
3,076 failures per corpus pass. This measures kernel execution; CSV loading,
one full-corpus warm-up per execution, Python overhead, and result formatting
are excluded. It does not measure batch or language-wrapper throughput.

The C harness consumes every output bit through a volatile integer checksum,
uses a monotonic clock, and pins to the first available CPU on Linux. The
runner records CPU affinity (`-1` if unavailable), alternates kernel order for
seven repetitions at each scale, and reports median elapsed time, rows/s, and
relative median absolute deviation. Reports retain raw elapsed times, call and
failure counts, compiler/platform details, and corpus/executable hashes.

## Results

On 2026-10-01, GCC 13.3.0 on Linux x86_64 (7.0.0-34-generic, glibc 2.39),
Intel Core i9-13900HK, pinned to CPU 12:

| Scale | Calls/run | Original s | Current s | Original rows/s | Current rows/s | Speedup |
|---|---:|---:|---:|---:|---:|---:|
| 1× | 35,976 | 0.526 | 0.328 | 68,425 | 109,810 | 1.605× |
| 10× | 359,760 | 5.261 | 3.281 | 68,377 | 109,653 | 1.604× |

Values are medians of seven repetitions. Relative MAD was below 0.19% for
both kernels at both scales. Kernels used GNU89 and
`-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`.
[throughput-gcc-13.3.0.json](throughput-gcc-13.3.0.json) retains the measurements.

## Reproduce

From the repository root:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
python3 benchmarks/compare.py \
  build/lwbgt_reference_benchmark build/lwbgt_benchmark build/cases.csv \
  build/throughput.json \
  --compiler-flags='-std=gnu89 -O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing'
```

On Linux, prefix the runner with `taskset -c N` to select a CPU available on
your machine. Both kernels must use matched compiler and floating-point flags.
Use `--repetitions N` to change the repetition count (minimum three). The
measured scales remain 1× and 10×. Allow about 80 seconds on this machine
for seven paired repetitions at both scales, including warm-ups. CI checks
accounting on a small fixture.

Results depend on hardware, compiler, and workload. These regression fixtures
and synthetic samples do not establish performance on an observed-weather
dataset. See [the numerical baseline](../tests/BASELINE.md) for input coverage
and comparison limits.
