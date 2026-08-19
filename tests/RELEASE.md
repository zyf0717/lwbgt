# v0.3.0 release verification

v0.3.0 adds a dependency-free Python `ctypes` distribution around the unchanged
Liljegren numerical source and FFI ABI v1. The wheel-only runtime uses the same
object files, compiler flags, linker export controls, and three-symbol surface
as the native shared library. The normal native CMake installation remains
unchanged.

Release acceptance requires:

- the full native CTest matrix on Linux/GCC, macOS/AppleClang, and
  Windows/MinGW;
- exact 454-case equivalence through both the native and wheel-only targets;
- installed-wheel API, layout, scalar, batch, solver-failure, `esat`, and
  packaged-resource tests;
- `py3-none` wheels for manylinux x86_64/aarch64, macOS x86_64/arm64, and
  Windows amd64, repaired and dependency-inspected by platform tools;
- one loadable runtime library per wheel and no native development tree;
- clean installation of the same Linux wheel on Python 3.10 and the latest
  stable CPython;
- an isolated sdist rebuild and clean source-built-wheel test;
- PEP 639 metadata plus `LICENSE`, `LICENSING.md`, `NOTICE`, and the complete
  UChicago Argonne licence in every archive;
- version coherence and successful metadata validation.

Local Linux/GCC 13 verification on 2026-08-19 passed all 10 CTest tests: native
and wheel-target 454-case exact equivalence, batch equivalence, both export
audits, installed C/C++ consumers, and the Python/R/Julia examples. All 16
installed-wheel tests passed from both the wheel and an isolated sdist build.
The local `py3-none-linux_x86_64` wheel contains exactly one 22,728-byte runtime
library and all four required legal files; `twine check` and `auditwheel show`
passed. The same wheel produced Singapore WBGT `32.50229263305664` with status 0
on clean Python 3.10.20, 3.12.13, and 3.14.7 environments.

Cross-platform wheel results, TestPyPI rehearsal status, PyPI publication,
attestation verification, and the final release commit/tag are pending until
the changes are merged and the release workflows execute.

Production PyPI publication is structurally blocked on a successful TestPyPI
OIDC upload, byte-for-byte artifact identity check, and clean installed-wheel
test suite.

Historical verification is retained in `RELEASE-0.1.0.md`,
`RELEASE-0.2.0.md`, and `RELEASE-0.2.1.md`.
