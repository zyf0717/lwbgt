# Changelog

## Unreleased — v0.1.0 release candidate

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
