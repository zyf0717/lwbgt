# Changelog

## v0.4.2 — 2026-09-22

- Added a dependency-safe SwiftPM `CLWBGT` C-library product backed directly
  by the canonical native sources and public header.
- Added release-mode downstream SwiftPM consumer tests on Linux and macOS.

## v0.4.1 — 2026-09-19

- Declared the CRAN-facing R package license as standard Apache License 2.0.
- Preserved the original UChicago Argonne license, attribution, and required
  acknowledgement for the bundled Liljegren-derived source.

## v0.4.0 — 2026-09-18

- Added a dependency-free R package under `r/` with the plain-data-frame
  `lwbgt_input()`, `calculate()`, and vectorized `esat()` API.
- Matched the Python wrapper's input names, units, ordering, and public `esat`
  default while adding per-row R validation and stable failure statuses.
- Compiled synchronized kernel sources directly into the R DLL with registered,
  forced native symbols and the native floating-point safety flags.
- Guarded the legacy demonstration program out of library builds and made
  invalid solar-position inputs return initialized failure outputs.
- Added base-R API tests, source/version coherence gates, multi-platform R
  package checks, direct GitHub installation, and R-universe distribution.

## v0.3.0 — 2026-08-19

- Added the official dependency-free Python API: immutable `Input` and `Result`
  records plus `calculate`, `calculate_batch`, and `esat`.
- Added an unversioned, wheel-only shared target built from the existing native
  objects with the same restricted three-symbol export surface.
- Added platform-specific, Python-ABI-independent wheel and rebuildable sdist
  packaging through scikit-build-core.
- Added installed-wheel ABI layout, resource loading, scalar, batch, failure,
  `esat`, deterministic fixture, archive licensing, and version-coherence tests.
- Added cibuildwheel coverage for manylinux x86_64/aarch64, macOS x86_64/arm64,
  and Windows amd64, plus OIDC Trusted Publishing release automation.

## v0.2.1 — 2026-08-18

- Licensed project-authored files under Apache-2.0 while preserving the
  Liljegren-derived numerical files under their UChicago Argonne terms.
- Added the authoritative v1 ABI contract covering layouts, units, status and
  ownership semantics, concurrency, symbols, and compatibility policy.
- Added an installed C++ consumer that validates public-header compatibility,
  structure sizes and offsets, and shared-library linkage.

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
