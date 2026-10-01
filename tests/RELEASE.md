# v1.0.2 release verification

This release uses one 35,976-row corpus for reference comparison and throughput
runs at 1× and 10×. The kernel, floating-point flags, and v1 ABI are
unchanged. [BASELINE.md](BASELINE.md) records coverage and hashes;
[benchmarks/README.md](../benchmarks/README.md) records the timing method and
results.

Local checks on 2026-10-01 passed:

- 17 CTest checks on Linux x86_64 with GCC 13.3.0 and Clang 18.1.3, including
  whole-corpus compatibility, scalar/batch equality, and benchmark accounting;
- 18 installed-wheel Python tests, including a wheel built from the sdist;
- distribution, version, and R-source checks;
- seven paired throughput measurements at each scale with GCC 13.3.0,
  measuring 1.605× and 1.604× median speedups at 1× and 10×.

The same kernel and interfaces also passed three release-mode SwiftPM tests
with Swift 6.2.4 and R 4.6.1 build/check with a PDF manual (`Status: OK`).
The extracted Clang toolchain needed its `libomp` directory in
`LD_LIBRARY_PATH` for the R example. Publication requires passing CI on the
exact candidate commit; follow [RELEASING.md](../docs/RELEASING.md).

## Earlier verification

v1.0.1, checked on 2026-10-01, passed native, Python, and SwiftPM tests.
R 4.6.1 checks passed with GCC, Clang, and disabled long-double support,
including the PDF manual. R golden tests use binary32 epsilon (`2^-23`);
there were no R errors or warnings.

v1.0.0, checked on 2026-09-25, passed native, distribution, installed-wheel,
R, and Linux SwiftPM checks. Numerical results matched the pre-refactor kernel,
the Linux SONAME remained `liblwbgt.so.0`, and R reported `Status: OK`.
Older records are retained in the `RELEASE-*.md` files.
