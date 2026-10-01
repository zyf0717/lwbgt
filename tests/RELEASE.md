# v1.0.2 release verification

This release expands comparison coverage and contribution guidance without
changing the kernel, floating-point flags, v1 ABI, or timing workload.
[BASELINE.md](BASELINE.md) records the corpus, seeds, hashes, and limitations.

Local checks on 2026-10-01 passed:

- 20 CTest checks on Linux x86_64 with GCC 13.3.0 and Clang 18.1.3;
- 19 installed-wheel Python tests, including a wheel built from the sdist;
- distribution, version, and R-source checks;
- three release-mode SwiftPM tests with Swift 6.2.4;
- R 4.6.1 build/check, tests, and PDF manual: `Status: OK`.

The extracted Clang toolchain needed its `libomp` directory in
`LD_LIBRARY_PATH` for the R example. Publication still requires passing CI
on the exact candidate commit; follow [RELEASING.md](../docs/RELEASING.md).

## Earlier verification

v1.0.1, checked on 2026-10-01, passed the then-current 12 CTest, 17 Python,
and three SwiftPM tests. R 4.6.1 checks passed with GCC, Clang, and disabled
long-double support, including the PDF manual. R golden tests use binary32
epsilon (`2^-23`); the original exact assertion failed on the noLD build.
There were no R errors or warnings; regular checks reported two environment
NOTEs and noLD reported one recent-update NOTE.

v1.0.0, checked on 2026-09-25, passed native, distribution, installed-wheel,
R, and Linux SwiftPM checks. The 852 cases matched the pre-refactor kernel
exactly, the Linux SONAME remained `liblwbgt.so.0`, and R reported `Status: OK`.
Older records are retained in the `RELEASE-*.md` files.
