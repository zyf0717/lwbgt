# v1.0.0 release verification

v1.0.0 stabilizes the existing reference-compatible v1 calculation and public
interfaces. The C source now shares atmospheric and wet-bulb intermediates;
the 852-case probe remains bit-identical to the v0.4.3/v1.0.0 baseline. The
v1 FFI ABI and default calculation are unchanged. The Linux shared-library
SONAME remains `liblwbgt.so.0`.
Future changes to defined valid-input numerical results require explicit
versioned APIs; v1 remains the default throughout the 1.x release series.

Local verification on 2026-09-25 passed:

- version coherence and R-source synchronization;
- the Release CMake build and all 12 CTest tests, including both 852-case
  retained-original comparisons and installed consumers;
- Linux SONAME inspection, confirming `liblwbgt.so.0`;
- byte-exact comparison with the pre-refactor v1.0.0 kernel on all 852 cases;
- wheel and source-distribution content checks, a wheel rebuilt from the
  source distribution, and all 17 tests against each wheel in a clean
  environment;
- `R CMD build` and the complete `R CMD check`, including the PDF manual:
  `Status: OK`; and
- release-mode Linux SwiftPM downstream consumer tests using the cached
  Swift 6.2.4 container: 3 tests passed.

Release acceptance still requires green native, SwiftPM, wheel, and R CI on
the exact candidate commit. CI supplies the macOS SwiftPM check.

Create the annotated release tag and publish only after the candidate gates
pass. The previous release record is retained in `RELEASE-0.4.3.md`.
