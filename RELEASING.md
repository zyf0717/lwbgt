# Release process

The v0.4 release consists of the CRAN source package, five
Python-ABI-independent platform wheels, and one Python source distribution.
The R package must be accepted from the release commit before that commit is
tagged or any Python/GitHub artifacts are published.

## One-time service configuration

1. Configure the PyPI and TestPyPI Trusted Publishers for repository
   `zyf0717/lwbgt`, workflow `release.yml`, and their matching protected GitHub
   environments. Do not add API tokens.
2. Ensure the CRAN maintainer email in `r/DESCRIPTION` is current and verified.

## Release sequence

1. Set the same version in CMake, the C header, Python metadata, R
   `DESCRIPTION`, `CITATION.cff`, and the README. Add the changelog entry.
2. Require green native, wheel, and R-package CI on the exact release commit.
   The R workflow checks Linux/GCC, Linux/Clang with R-devel, Windows/Rtools,
   and macOS/AppleClang. Its `cran-source` artifact has passed
   `R CMD check --as-cran`, including the PDF manual.
3. Download the CI artifacts and independently verify them:

   ```sh
   python tests/check_versions.py
   python tests/check_r_sources.py
   python tests/check_distribution.py dist/*
   python -m twine check dist/*
   R CMD check --as-cran lwbgt_0.4.0.tar.gz
   ```

4. Rehearse the unchanged CRAN tarball on win-builder and macbuilder. Inspect
   package size, manual, DLL dependencies, examples, and installed legal files.
5. Submit that checked tarball to CRAN from the untagged release commit. Address
   reviewer feedback. If any source changes are required, bump the unified
   project version, rebuild all artifacts, and restart this sequence. If CRAN
   rejects the unlisted UChicago Argonne licence, stop and obtain a
   standard-licence grant; do not remove or rewrite the upstream terms.
6. After CRAN accepts the unchanged commit, create and push its annotated or
   signed tag:

   ```sh
   git tag -s v0.4.0 -m "lwbgt v0.4.0"
   git push origin v0.4.0
   ```

7. The tag workflow reruns the complete R and Python artifact gates, publishes
   to TestPyPI, verifies byte identity and installation, publishes to PyPI, and
   creates a GitHub release containing the Python and CRAN source artifacts.
8. Verify CRAN, PyPI, and GitHub metadata and clean installations. Never delete
   and re-upload a defective immutable artifact; issue a patch release.
