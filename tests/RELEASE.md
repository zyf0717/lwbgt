# v0.4.1 release verification

v0.4.1 declares the CRAN-facing R package license as standard Apache License
2.0 while preserving the separate UChicago Argonne terms for the synchronized
Liljegren-derived kernel. The C ABI remains version 1.

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

Local release verification on 2026-09-19 passed version and R-source coherence,
the Python runtime-version and distribution-license fixtures, `R CMD build`,
and the full R test file under `R CMD check --as-cran`. The CRAN check completed
with 0 errors and no license-related warnings or notes. Its environment emitted
one warning for the unavailable optional `checkbashisms` script and two notes
for a new submission and a compiler-injected flag. Full native, wheel,
cross-platform, direct GitHub-install, and R-universe results remain pending
until their respective local or CI release gates run.

Historical verification is retained in `RELEASE-0.1.0.md`,
`RELEASE-0.2.0.md`, and `RELEASE-0.2.1.md`.
