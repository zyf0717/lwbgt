# v0.4.0 release verification

v0.4.0 adds the dependency-free base-R package under `r/`. It compiles a
synchronized copy of the existing kernel directly into the package DLL; the C
ABI remains version 1 and Python behavior is unchanged.

Release acceptance requires:

- the full native CTest matrix and exact 454-case equivalence suite;
- all installed-wheel, sdist, ABI, resource, and version-coherence tests;
- base-R scalar, vector, recycling, empty, validation, failure-status, schema,
  and water/ice `esat` tests;
- byte-identical canonical and `r/src` kernel/header sources;
- registered forced R symbols, hidden internal symbols, and no compiled
  demonstration `main`, `printf`, or `exit` dependency;
- `R CMD check --as-cran` on Linux/GCC, Linux/Clang with R-devel,
  Windows/Rtools, and macOS/AppleClang, with the PDF manual checked on Linux;
- installed legal files and no errors, warnings, or significant notes;
- win-builder and macbuilder rehearsal of the exact CRAN tarball.

CRAN submission occurs from the release commit before tagging. A required
source change after submission also requires a unified version bump. CRAN
acceptance of the unchanged commit precedes the matching Git tag and
Python/GitHub publication.

Local Linux/GCC 13 verification on 2026-09-18 passed all 11 CTest tests,
including the 454-case exact-equivalence suite, all 17 installed-wheel tests,
and the full R test file. `R CMD check --as-cran` completed with 0 errors,
0 warnings, and the two expected new-submission/licence and host-compiler
notes. The installed R DLL exports only `R_init_lwbgt`, has no `exit` or
`printf` import, and includes all legal files. Cross-platform and builder
results remain pending until CI and pre-submission rehearsal run.

Historical verification is retained in `RELEASE-0.1.0.md`,
`RELEASE-0.2.0.md`, and `RELEASE-0.2.1.md`.
