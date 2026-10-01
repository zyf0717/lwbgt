# Releasing

Release from a commit with passing native, SwiftPM, Python wheel, and R CI.
Use the workflow definitions as the source of truth for supported platforms.

## Prepare

Update version metadata, `CHANGELOG.md`, `r/NEWS.md`, and `tests/RELEASE.md`.
Run the checks in [CONTRIBUTING.md](../CONTRIBUTING.md), then verify the CI
artifacts:

```sh
python3 tests/check_versions.py
python3 tests/check_r_sources.py
python3 tests/check_distribution.py dist/*
python3 -m twine check dist/*
release_version=$(awk -F '"' '/^version = / {print $2; exit}' pyproject.toml)
R CMD check "lwbgt_${release_version}.tar.gz"
```

Check the R source artifact from the same commit, including its PDF manual.

## Publish

After all gates pass, create and push an annotated or signed tag:

```sh
git tag -a "v${release_version}" -m "lwbgt v${release_version}"
git push origin "v${release_version}"
```

The [release workflow](../.github/workflows/release.yml) builds the artifacts,
publishes to TestPyPI, verifies their hashes and installation, then publishes
to PyPI and creates the GitHub release. Verify the published version and test
Python and R installation in clean environments using the [README](../README.md).
Require a successful R-universe build for the tagged commit before announcing
its R release. Correct a defective release with a new version; never replace
published artifacts.

## Service setup

Configure PyPI and TestPyPI Trusted Publishing for `release.yml` and its
protected environments. The R-universe registry must point to this repository
with `subdir: "r"` and `branch: "*release"` so it follows GitHub releases.
