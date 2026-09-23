# lwbgt 0.4.3

- Synchronized the R package with project release 0.4.3. The direct C scalar
  API now writes estimated wind for 2 m input; the R output and WBGT results
  for valid inputs are unchanged.
- Expanded the retained-original comparison and removed an unverified weather
  cohort from the timing workload.

# lwbgt 0.4.2

- Synchronized the R package version with project release 0.4.2; the R API and
  native numerical behavior are unchanged from 0.4.1.

# lwbgt 0.4.1

- Declared the CRAN-facing package license as Apache License 2.0 while
  preserving the original UChicago Argonne terms and attribution for the
  bundled Liljegren-derived `src/wbgt.c`.

# lwbgt 0.4.0

- Added the first R interface with dependency-free vectorized
  `lwbgt_input()`, `calculate()`, and `esat()` functions.
- Added per-row validation, stable statuses, and R-native missing output
  handling.
- Bundled the reference-compatible native kernel directly into the package.
- Added direct GitHub installation and R-universe distribution.
