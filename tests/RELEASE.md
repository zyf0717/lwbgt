# v1.1.0 release verification

Release preparation started on 2026-10-02. v1.1.0 adds the Julia interface under
`julia/` and native artifact distribution through this repository's release
workflow. All interfaces share version 1.1.0. The reference-compatible numerical
kernel, v1 FFI ABI, and `liblwbgt.so.0` SONAME are unchanged.

The CMake package now accepts compatible releases within major version 1. Its
existing consumer test requests 1.0.0 and must continue to accept 1.1.0.

## Validation status

This is version and release-note preparation, not a published release. PR CI,
manual native-artifact preparation, the metadata release PR, tagged publication,
and published-installation checks remain release gates. Julia General
registration follows successful publication.

Local Linux checks passed for the 1.1.0 preparation:

- Version coherence and byte-identical R source copies.
- All 15 native CTest checks, including the installed CMake consumer requesting
  1.0.0, using GCC 13.3 in release mode.
- All four SwiftPM consumer tests using the CI image `swift:6.2.4-noble` in
  release mode with `-march=native`, including bit-for-bit comparison with CMake
  over all 35,976 WBGT cases. macOS validation remains in CI.
- Python wheel and source-distribution contents, plus all 18 installed-wheel
  tests with Python 3.14.7.
- `R CMD build` and `R CMD check`, including the PDF manual: `Status: OK`.
- Julia API tests (23 assertions), packaging/source-identity tests (16
  assertions), and four metadata-preparation guard tests. API tests loaded the
  locally built library; platform archive validation remains in release preparation.

The numerical corpus and recorded baseline are unchanged; retain their original
version and provenance in [baseline.json](baseline.json). See
[BASELINE.md](BASELINE.md) for coverage and
[benchmarks/README.md](../benchmarks/README.md) for the existing throughput record.
No new numerical or performance claim is introduced by this version bump.

Follow [RELEASING.md](../docs/RELEASING.md) for preparation and publication.
Earlier verification is preserved in [RELEASE-1.0.1.md](RELEASE-1.0.1.md) and the
other `RELEASE-*.md` files.
