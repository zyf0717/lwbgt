# v1.0.0 release verification

v1.0.0 stabilizes the existing reference-compatible v1 calculation and public
interfaces. The numerical source, v1 FFI ABI, and default calculation are
unchanged from v0.4.3. The Linux shared-library SONAME remains `liblwbgt.so.0`.
Future changes to defined valid-input numerical results require explicit
versioned APIs; v1 remains the default throughout the 1.x release series.

Local verification on 2026-09-23 passed:

- version coherence and R-source synchronization;
- the Release CMake build and all 12 CTest tests, including both 852-case
  retained-original comparisons and installed consumers;
- Linux SONAME inspection, confirming `liblwbgt.so.0`;
- wheel and source-distribution content checks, `twine check`, a wheel rebuilt
  from the source distribution, and all 17 tests against each wheel in a clean
  environment; and
- `R CMD build` and the complete `R CMD check`, including the PDF manual:
  `Status: OK`.

Release acceptance requires:

- downstream SwiftPM consumer tests in release mode; and
- green native, SwiftPM, wheel, and R CI on the exact candidate commit.

SwiftPM could not be run locally because Swift is unavailable in this
environment; CI supplies its Linux and macOS checks.

Create the annotated release tag and publish only after the candidate gates
pass. The previous release record is retained in `RELEASE-0.4.3.md`.
