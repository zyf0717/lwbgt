# Release process

The v1.0 release consists of one checked R source package, five
Python-ABI-independent platform wheels, and one Python source distribution.
The R package is distributed from GitHub and R-universe and uses a standard
Apache License 2.0 declaration for its CRAN-facing package metadata. The
bundled numerical source remains separately governed by the original UChicago
Argonne terms documented in the installed legal files.

## One-time service configuration

1. Configure the PyPI and TestPyPI Trusted Publishers for repository
   `zyf0717/lwbgt`, workflow `release.yml`, and their matching protected GitHub
   environments. Do not add API tokens.
2. Install the R-universe GitHub app for the `zyf0717` account and allow it to
   report commit statuses for this repository.

## Release sequence

1. Set the same version in CMake, the C header, Python metadata, R
   `DESCRIPTION`, `CITATION.cff`, and the README. Add the changelog entry.
2. Require green native, SwiftPM, wheel, and R-package CI on the exact release
   commit. SwiftPM is tested through a downstream package on Linux and macOS.
   The R workflow checks Linux/GCC, Linux/Clang with R-devel, Windows/Rtools,
   and macOS/AppleClang. Its `r-source` artifact has passed a complete `R CMD
   check`, including the PDF manual.
3. Download the CI artifacts and independently verify them:

   ```sh
   python tests/check_versions.py
   python tests/check_r_sources.py
   python tests/check_distribution.py dist/*
   python -m twine check dist/*
   R CMD check lwbgt_1.0.0.tar.gz
   ```

4. Create and push an annotated or signed tag only after every release gate
   passes:

   ```sh
   git tag -s v1.0.0 -m "lwbgt v1.0.0"
   git push origin v1.0.0
   ```

5. The tag workflow reruns the complete R and Python artifact gates, publishes
   to TestPyPI, verifies byte identity and installation, publishes to PyPI, and
   creates a GitHub release containing the Python and R source artifacts.
6. Verify that `packages.json` in `zyf0717/zyf0717.r-universe.dev` still
   contains this entry; add it if missing, preserving the existing entries:

   ```json
   {
       "package": "lwbgt",
       "url": "https://github.com/zyf0717/lwbgt",
       "subdir": "r",
       "branch": "*release"
   }
   ```

   The `subdir` is required because `DESCRIPTION` is under `r/`; `*release`
   keeps R-universe builds on the latest published GitHub release.
7. R-universe detects the new GitHub release through the `*release` registry
   entry and builds the package from `r/`. Require a successful build for the
   tagged commit at `https://zyf0717.r-universe.dev/lwbgt` before announcing
   the R release.
8. Verify PyPI and GitHub metadata, then test both supported R installation
   paths in clean R libraries:

   ```r
   install.packages("lwbgt", repos = "https://zyf0717.r-universe.dev")
   remotes::install_github("zyf0717/lwbgt/r@*release", upgrade = "never")
   ```

Never delete and re-upload a defective immutable artifact; issue a patch
release.
