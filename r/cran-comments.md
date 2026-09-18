## Test environments

- Local Ubuntu 24.04, R 4.6.1
- GitHub Actions: Linux GCC, Linux Clang/R-devel, Windows Rtools, macOS AppleClang
- win-builder and macbuilder results will be added before submission

## R CMD check results

Local `R CMD check --as-cran` reports 0 errors, 0 warnings, and 2 notes:

- New submission using a file licence; the complete upstream and project
  licence texts are included and installed.
- The local R installation supplies `-mno-omit-leaf-frame-pointer` in its own
  `C90FLAGS`. The package does not add that flag.

Final win-builder and macbuilder results will be recorded before submission.

## Licensing

The package contains a modified Liljegren WBGT v1.1 derivative under the
permissive UChicago Argonne terms included in full in the source and installed
package. Project-authored files use Apache-2.0. DESCRIPTION therefore uses
`License: file LICENSE`; file-level copyright ownership, complete licence
texts, and the required acknowledgement are included in LICENSE, inst/LICENSES,
inst/COPYRIGHTS, and inst/NOTICE.
