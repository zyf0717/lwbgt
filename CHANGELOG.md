# Changelog

## v0.2.0 — 2026-08-18

- Added the fixed-layout `lwbgt_input_v1` and `lwbgt_output_v1` structures and
  serial `lwbgt_calc_batch_v1` FFI entry point without changing the scalar ABI.
- Added versioned shared-library builds with a three-symbol dynamic export
  surface while retaining the existing static archive.
- Added dependency-light Python, R, and Julia examples and made them release
  gates on Linux/GCC, macOS/Clang, and Windows/MinGW CI.
- Added relocatable CMake and `pkg-config` installation metadata.
- Verified the final static and shared artifacts on Linux/GCC,
  macOS/AppleClang, and Windows/MinGW, including installed consumers and all
  three language examples.
- Revalidated the position-independent static build at 1.249× overall median
  throughput with exact compatibility and all release gates passing.

## v0.1.0 — 2026-08-18

The release gate passes with 1.316× median single-thread throughput on GCC
13.3.0 and 1.289× on GCC 16.2.0. All 454 compatibility cases remain
bit-identical and every benchmark cohort exceeds 1.25×.

- Pinned Liljegren WBGT v1.1 commit
  `cd672a886880b67f3f27bdbf75038d8f7ff0bac2` and source blob
  `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`.
- Added static `liblwbgt.a` and the permanent `calc_wbgt`/`esat` compatibility
  declarations in `lwbgt.h`.
- Skipped radiative work that was multiplied by zero in the psychrometric
  wet-bulb solve.
- Reused rounded air viscosity in cylinder and sphere convective coefficients.
- Hoisted invariant atmospheric, surface, and solar radiation terms from the
  iterative globe and natural wet-bulb solves after profiling identified both
  solves as the remaining hot paths.
- Proved exact output equality with GCC 13.3.0 and GCC 16.2.0.
- Proved that all three existing HeatStressBench C adapters compile unchanged
  and produce byte-identical generated, decomposition, NASA POWER sample, and
  ERA5 sample results when only the link input changes.
- Audited the static archive export surface and fixed the permanent supported
  API at `calc_wbgt` and `esat`; inherited helper exports remain implementation
  details.
