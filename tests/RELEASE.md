# v1.2.1 release verification

Prepared on 2026-10-11; publication is pending. This patch fixes binding failure
handling and packaging while preserving native v1 numerical results, ABI
layouts, and the `liblwbgt.so.0` SONAME.

## Compatibility

- R now reports status -1 and `NA` numerical outputs when a requested
  psychrometric solve fails. `psychrometric=FALSE` can still return valid WBGT.
- Non-finite R `esat()` results become `NA` with a warning.
- Source archives exclude generated R/Swift files. Native installation paths
  support nested library directories and relocation through `pkg-config`.
- The release workflow requires native and SwiftPM validation before publication.

## Validation status

Local Linux checks passed on 2026-10-11:

- Version coherence and byte-identical R source copies.
- All 15 native CTest checks with GCC 13.3.0, including the retained-original
  comparison and installed CMake/`pkg-config` consumers. The installation uses
  Debian-style `lib/x86_64-linux-gnu` and custom `lib/lwbgt-test` layouts,
  relocated to temporary prefixes. Custom layouts specify the package config
  directory explicitly for CMake discovery.
- Source distribution built from a checkout containing R/Swift build products;
  archive checks confirm they are excluded. A wheel rebuilt from that archive
  passes its content check; all 21 installed-package tests pass on Python 3.14.7.
- All four SwiftPM consumer tests with `swift:6.2.4-noble`, release mode and
  `-march=native`, including bitwise comparison over all 35,976 corpus rows.
- R 4.6.1 source-package build and full check, including requested psychrometric
  failure handling, non-finite `esat` results, and the PDF manual: `Status: OK`.
- Actionlint validation of the modified native and release workflows.

Cross-platform CI and post-merge validation are required before tagging.

The synthetic corpus and [baseline.json](baseline.json) are unchanged; retain
their original provenance. No new numerical or throughput claim is introduced.
[BASELINE.md](BASELINE.md) defines coverage and limits.

Follow [RELEASING.md](../docs/RELEASING.md) for validation and publication.
Previous verification is preserved in [RELEASE-1.2.0.md](RELEASE-1.2.0.md).
