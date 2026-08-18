# lwbgt

`lwbgt` is a drop-in-compatible, source-derived optimization of the Liljegren
WBGT v1.1 C implementation. It preserves the original scalar ABI and numerical
behaviour while eliminating demonstrably repeated or dead work.

**Release status: v0.2.0.** v0.1.0 is the frozen scalar-compatibility release.
Its complete permitted optimization set measures
1.316× on the primary GCC 13 benchmark and 1.289× in the GCC 16.2 container.
The v0.2.0 position-independent static build measures 1.249× on the GCC 13
host. All three results exceed the mandatory 1.20× gate with exact
compatibility. These are narrowly supported throughput measurements on the
documented environments and workloads, not broader portability claims.

It is not affiliated with or endorsed by the original authors, UChicago
Argonne, or the U.S. Department of Energy.

## Build and install

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
cmake --install build --prefix /desired/prefix
```

The build produces `liblwbgt.a` and a versioned shared library and installs
`lwbgt.h`, CMake package metadata, and `pkg-config` metadata. Core compilation is
GNU89 with `-fno-fast-math -ffp-contract=off -fno-strict-aliasing`; LTO and
architecture-specific flags are not enabled. GCC, Clang/AppleClang, and MinGW
GCC are supported; MSVC cannot compile the preserved K&R source.

Installed CMake consumers can select `lwbgt::static` or `lwbgt::shared` after
`find_package(lwbgt CONFIG REQUIRED)`.

## Supported API and compatibility contract

The legacy `calc_wbgt` and `esat` declarations in `include/lwbgt.h` remain the
permanent scalar compatibility ABI. Scalar floating-point arguments use
`double` at the ABI boundary because the original K&R `float` parameters undergo
default argument promotion; output pointers remain `float *`.

The v1 FFI ABI adds fixed-layout `lwbgt_input_v1` and `lwbgt_output_v1`
structures and `lwbgt_calc_batch_v1`. The batch call executes scalar calls in
input order. It returns the supplied wind as the effective 2-m wind when no
height conversion is needed, avoiding the legacy scalar routine's untouched
output-pointer behavior. Independent calls using separate buffers are
thread-safe; the batch function itself is serial.

The shared library exports only `calc_wbgt`, `esat`, and
`lwbgt_calc_batch_v1`. The static archive retains global helper symbols inherited
from the source implementation; they remain unsupported implementation details.
The exported-symbol review is recorded in `tests/API.md`.

Minimal Python, R, and Julia examples are under `examples/`. They are tested
interoperability examples, not maintained PyPI, CRAN, or Julia registry
packages, and they make no compatibility claim for third-party wrappers.

The exact upstream source is retained unmodified at
`upstream/wbgt.c.original`. `src/wbgt.c` is the modified derivative maintained
by Yifei/HeatStressDev. HeatStressBench's frozen `liljegren-c` target remains
the oracle and is not replaced or relabelled.

For matched compilers and floating-point flags, the acceptance policy is exact
32-bit equality for return status, estimated wind speed, `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat`. The deterministic 454-case suite produces the same
`087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff`
probe hash with GCC 13.3.0 and GCC 16.2.0.

## Evidence

| Environment | Exact result | Median overall speedup | Release gate |
|---|---:|---:|---:|
| Linux x86-64, GCC 13.3.0 | bit-identical | 1.316× | passed |
| Linux x86-64 container, GCC 16.2.0 | bit-identical | 1.289× | passed |
| Linux x86-64, GCC 13.3.0, v0.2.0 PIC build | bit-identical | 1.249× | passed |

Every v0.1.0 benchmark cohort exceeds 1.25×. The v0.2.0 PIC build passes the
unchanged overall and per-cohort gates, with a 1.210× slowest measured cohort.
Detailed host results, hardware, flags, datasets, warm-up, CPU-affinity policy,
repetitions, medians, and dispersion are under `benchmarks/`. HeatStressBench
adapter evidence is under `tests/`.

## Licence and provenance

`UPSTREAM.md` records the repository, pinned commit, blob, import date, and
relationship to HeatStressBench. The complete upstream source licence is in
`LICENSES/LicenseRef-UChicago-Argonne-WBGT-1.1.txt`; the required
Argonne/Department of Energy acknowledgement is in `NOTICE`.

## Explicit non-goals

This release adds no namespaced high-level language API, official language
package, alternate solver, precision change, new physics, cache, parallelism,
OpenMP, SIMD, GPU path, fast-math mode, or language package-manager
distribution.
