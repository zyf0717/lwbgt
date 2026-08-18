# lwbgt

`lwbgt` is a source-derived, performance-focused C library based on the
Liljegren WBGT v1.1 reference source. The intended v0.1.0 preserves the original
scalar ABI and numerical behaviour while eliminating demonstrably dead work.

**Release status: experimental.** The complete permitted optimization set
measures 1.162× on the primary GCC 13 benchmark and 1.159× in the GCC 16.2
HeatStressBench toolchain, below the mandatory 1.20× gate. No `v0.1.0` tag has
been created.

It is not affiliated with or endorsed by the original authors, UChicago
Argonne, or the U.S. Department of Energy.

## Build and install

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
cmake --install build --prefix /desired/prefix
```

The build produces the static library `liblwbgt.a` and installs `lwbgt.h`.
Core compilation is GNU89 with `-fno-fast-math -ffp-contract=off
-fno-strict-aliasing`; LTO and architecture-specific flags are not enabled.

## Compatibility contract

The callable `calc_wbgt` and `esat` symbols and their declarations in
`include/lwbgt.h` are permanent compatibility ABI. Scalar floating-point
arguments use `double` at the ABI boundary because the original K&R `float`
parameters undergo default argument promotion; output pointers remain
`float *`.

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
| Linux x86-64, GCC 13.3.0 | bit-identical | 1.162× | failed |
| Linux x86-64 container, GCC 16.2.0 | bit-identical | 1.159× | failed |

No benchmark cohort regressed. Detailed host results, hardware, flags,
datasets, warm-up, CPU-affinity policy, repetitions, medians, and dispersion are
under `benchmarks/`. HeatStressBench adapter evidence is under `tests/`.

## Licence and provenance

`UPSTREAM.md` records the repository, pinned commit, blob, import date, and
relationship to HeatStressBench. The complete upstream source licence is in
`LICENSES/LicenseRef-UChicago-Argonne-WBGT-1.1.txt`; the required
Argonne/Department of Energy acknowledgement is in `NOTICE`.

## Explicit non-goals

This experimental work adds no namespaced high-level API, batch API, shared
library or SONAME, alternate solver, precision change, new physics, cache,
parallelism, OpenMP, SIMD, GPU path, fast-math mode, language binding, or
package-manager distribution.
