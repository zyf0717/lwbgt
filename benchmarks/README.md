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
  --compiler-flags='current: -std=c11; original: -std=gnu89; common: -O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing'
```

Current CMake builds use C11 for the production kernel and GNU89 for the oracle.
The recorded results above predate that build change; retain their original
compiler metadata when comparing new measurements.

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

## Optional psychrometric wet-bulb and private helpers

The unreleased C changes retain every default output and permit explicitly
skipping the independent psychrometric solve. `batch.py` compares the public
batch ABI against `main` at `027d41b`, using matching compiler settings. It
checks every default output bit and every retained opt-out output bit before
timing. Zero flags also match the existing entrypoint exactly.

On 2026-10-09, Linux x86_64, Intel Core i9-13900HK, CPU 0, with seven rotating
repetitions per mode and scale:

| Compiler | Main rows/s | Default rows/s | Opt-out rows/s | Default/main | Opt-out/main |
|---|---:|---:|---:|---:|---:|
| GCC 13.3.0 | 134,953 | 140,279 | 240,503 | 1.039× | 1.782× |
| Clang 18.1.3 | 140,598 | 140,491 | 240,332 | 0.999× | 1.709× |

These figures use 1,590,715 accepted ERA5 records, repeated four times per
timed run (6,362,860 evaluations). The sample selects every fourth latitude
and longitude from the acquired 0.25° global grid, retaining land fractions
above 0.5 and all 24 hours on January 1, July 1, and October 1, 2025. Rows are
cell-major. Solar energy is divided by 3600 to obtain W/m², pressure by 100
to obtain hPa, and temperatures are converted from kelvin to Celsius.
Timestamps are interval midpoints, with zero further averaging offset; wind
is measured at 10 m, terrain follows the saved urban mask, and the supplied
upper-minus-lower temperature difference is +1 °C, matching HeatStressBench's
missing-profile assumption. Relative humidity uses native water-phase `esat`.

All accepted records are timed, including 121,535 model failures per sample
pass. Loading, conversion, output hashing, validation, and warm-ups are
excluded. This measures kernel throughput rather than wrapper or end-to-end
data processing, and does not establish model accuracy on these records.

The matrix also covers the 35,976-row numerical corpus, 64 invalid-weather
cases, and 301,705 regional ERA5 records, at 1× and 4×. Both compilers together
process 404,976,600 timed records. Default and retained opt-out outputs match
`main` bit-for-bit in every dataset under each compiler. Relative median
absolute deviations were below 0.12% on the ERA5 datasets; the 64-row
fixture is too short for useful performance claims. Clang's default speed
remains essentially unchanged, so private helpers do not promise a gain on
every compiler.

[GCC raw results](optional-psychrometric-gcc.json) and
[Clang raw results](optional-psychrometric-clang.json) retain input and library
hashes, source hashes, controls, counts, and all timings. The native-endian
104-byte ERA5 input records are local study artifacts, excluded from Git.

To reproduce the runner after building a baseline and candidate library:

```sh
python3 benchmarks/batch.py \
  build/optional-psychrometric/baseline-gcc/liblwbgt.so \
  build/optional-psychrometric/gcc/liblwbgt.so \
  build/optional-psychrometric/gcc-performance.json \
  --input corpus=build/optional-psychrometric/gcc/cases.csv \
  --input weather=build/optional-psychrometric/gcc/weather-cases.csv \
  --input era5-global=build/optional-psychrometric/era5-global-3days.bin \
  --scales 1 4 --repetitions 7 \
  --compiler='GCC 13.3.0' \
  --compiler-flags='-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing'
```

The runner uses only the Python standard library. CSV input follows the shared
test-corpus schema; binary input uses the host's `lwbgt_input_v1` layout and
byte order. Use the saved ERA5 generator and metadata in
`build/optional-psychrometric` for the local acquisition.
