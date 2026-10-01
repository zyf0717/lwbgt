# v1.0.1 release verification

v1.0.1 changes only the R test-suite tolerance for five floating-point golden
values, plus synchronized release metadata. Native calculations, compiler
flags, and the exact native oracle tests are unchanged.

Local verification on 2026-10-01 passed:

- version coherence and R-source synchronization;
- all 12 existing CTest tests on GCC 13.3 and Clang 18.1, including the
  unchanged 852-case retained-original comparisons;
- all 17 Python tests against a rebuilt Linux wheel;
- `R CMD build r` and `R CMD check --as-cran` on R 4.6.1 with GCC and Clang,
  and on R 4.6.1 built with `--disable-long-double` (capability confirmed
  false), including the PDF manual. No errors or warnings; regular R checks
  report two NOTEs (recent CRAN update and an installed-R compiler flag),
  while the noLD check reports only the recent-update NOTE.

The original R test suite reproduces the exact `esat(273.15, 1L)` assertion
failure under noLD; the updated suite passes. The tolerance is IEEE binary32
epsilon, `2^-23`, because R does not expose `.Machine$single.eps`.

Release acceptance requires green native, SwiftPM, wheel, and R CI on the
exact candidate commit, plus a successful CRAN-hosted noLD rerun. Create the
annotated release tag and publish only after the candidate gates pass.

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
