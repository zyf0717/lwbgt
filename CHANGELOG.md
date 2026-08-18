# Changelog

## Unreleased — experimental v0.1.0 work

Release is blocked: the two permitted optimizations reach 1.162× median
single-thread throughput on the primary benchmark, below the required 1.20×.

- Pinned Liljegren WBGT v1.1 commit
  `cd672a886880b67f3f27bdbf75038d8f7ff0bac2` and source blob
  `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`.
- Added static `liblwbgt.a` and the permanent `calc_wbgt`/`esat` compatibility
  declarations in `lwbgt.h`.
- Skipped radiative work that was multiplied by zero in the psychrometric
  wet-bulb solve.
- Reused rounded air viscosity in cylinder and sphere convective coefficients.
- Proved exact output equality with GCC 13.3.0 and GCC 16.2.0.
- Proved that all three existing HeatStressBench C adapters compile unchanged
  and produce byte-identical generated, decomposition, NASA POWER sample, and
  ERA5 sample results when only the link input changes.
