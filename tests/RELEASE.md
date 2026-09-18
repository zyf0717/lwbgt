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
- complete `R CMD check` runs on Linux/GCC, Linux/Clang with R-devel,
  Windows/Rtools, and macOS/AppleClang, with the PDF manual checked on Linux;
- installed legal files and no errors or warnings;
- successful installation from the GitHub release and from R-universe; and
- an R-universe build whose source commit matches the GitHub release tag.

The signed or annotated Git tag is created only after the source commit passes
all local and CI gates. The tag workflow publishes the immutable GitHub
release; the `*release` entry in `zyf0717/zyf0717.r-universe.dev` then makes
that release available through R-universe. A required source change after
publication requires a unified version bump and a new release.

Local Linux/GCC 13 verification on 2026-09-18 passed all 11 CTest tests,
including the 454-case exact-equivalence suite, all 17 installed-wheel tests,
and the full R test file. The complete R package check completed with 0 errors
and 0 warnings. The installed R DLL exports only `R_init_lwbgt`, has no `exit`
or `printf` import, and includes all legal files. Cross-platform, direct
GitHub-install, and R-universe results remain pending until their respective
CI and release steps run.

Historical verification is retained in `RELEASE-0.1.0.md`,
`RELEASE-0.2.0.md`, and `RELEASE-0.2.1.md`.
