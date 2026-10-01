# v1.0.2 release verification

v1.0.2 expands numerical regression coverage and adds contribution guidance.
The numerical kernel, floating-point flags, v1 ABI, historical 852-case corpus,
and 840-row benchmark workload are unchanged.

The default comparison adds 35,124 WBGT rows, 1,682 water/ice `esat` cases,
and 996 internal stability/solar diagnostics. The WBGT rows run through both
the static library and Python runtime; batch and installed-wheel tests also
exercise the expanded corpus. Rejected solar inputs are checked separately
against the current scalar and batch contracts; 64 invalid/non-finite weather
rows separately check current-API consistency.

Local verification on 2026-10-01 passed:

- all 20 CTest checks under GCC 13.3.0 and Clang 18.1.3 on Linux x86_64,
  including both expanded library comparisons and installed C/C++ consumers;
- all 19 Python tests against a wheel rebuilt from the source distribution;
- distribution-content checks, version coherence, and R-source synchronization;
- all three release-mode SwiftPM consumer tests under Swift 6.2.4 on Linux;
- `R CMD build r` and `R CMD check` on R 4.6.1, including tests and the PDF
  manual: `Status: OK`.

The extracted local Clang toolchain requires its `libomp` directory in
`LD_LIBRARY_PATH` for the R binding example. No kernel or linker-policy change
was needed. Reproduction details and numerical evidence are recorded in
[BASELINE.md](BASELINE.md). Release acceptance requires green native, SwiftPM,
wheel, and R CI on the exact candidate commit. Tagging and publication remain
separate release steps after those gates pass.

# v1.0.1 release verification

v1.0.1 changes only the R test-suite tolerance for five floating-point golden
values, plus synchronized release metadata. Native calculations, compiler
flags, and the exact native oracle tests are unchanged.

Local verification on 2026-10-01 passed:

- version coherence and R-source synchronization;
- all 12 existing CTest tests on GCC 13.3 and Clang 18.1, including the
  unchanged 852-case retained-original comparisons;
- all 17 Python tests against a rebuilt Linux wheel;
- all 3 release-mode SwiftPM downstream consumer tests using Swift 6.2.4
  on Linux;
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
