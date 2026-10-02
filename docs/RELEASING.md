# Releasing

Test, benchmark, and documentation changes can merge without a package
release. Keep the current version and record them under `Unreleased`. Publishing
new package artifacts requires a new version.

Release from a commit with passing native, SwiftPM, Python wheel, R, and Julia CI.
Use the workflow definitions as the source of truth for supported platforms.

## Prepare

Update version metadata, `CHANGELOG.md`, `r/NEWS.md`, and `tests/RELEASE.md`.
Run the checks in [CONTRIBUTING.md](../CONTRIBUTING.md). For kernel or corpus
changes, refresh the [numerical baseline](../tests/BASELINE.md) and
[throughput results](../benchmarks/README.md) using matched builds. Verify the
CI artifacts:

```sh
python3 tests/check_versions.py
python3 tests/check_r_sources.py
python3 tests/check_distribution.py dist/*
python3 -m twine check dist/*
release_version=$(awk -F '"' '/^version = / {print $2; exit}' pyproject.toml)
R CMD check "lwbgt_${release_version}.tar.gz"
```

Check the R source artifact from the same commit, including its PDF manual.

### Julia native archives

Julia shares the C/Python/R version, including releases that only change a binding.
The first Julia publication must use a new version (currently the next is 1.0.2);
do not add it retroactively to the published 1.0.1 release.

Put the version bump and all release changes in a same-repository PR. The **Julia**
workflow builds and tests the PR's source commit. After its full matrix and the
native, Python-wheel, and R workflows pass, it verifies the archives and appends
one commit to that same PR containing only:

- `julia/Artifacts.toml`: platform-specific release URLs and hashes.
- `julia/native-build.toml`: the tested source commit, source-tree digest, and CI run.

The job refuses to push if the PR closes or its source changes. Review the
metadata commit, wait for the originating Julia workflow to finish successfully,
and merge the PR manually. Tag the merged commit manually after the release gates
pass. Squash or rebase merging is supported because source identity is checked by
tree content, excluding only these two generated files.

The metadata push uses `GITHUB_TOKEN`, so it does not automatically execute another
test matrix. GitHub may show approval-pending workflows on the bot commit; the
successful source checks belong to its parent commit. The bot does not copy check
results onto the new commit. If branch rules later require checks on the final
commit, approve those runs or revise this policy before merging. No skip-CI marker
is added, so ordinary main-branch and tag workflows remain enabled.

Each subsequent source push runs the checks again and replaces the metadata.
Do not combine other source changes after preparation and before tagging. The
release preflight rejects such changes. CI archives are retained for 90 days;
rerun preparation if they expire. Generated URLs become usable only when their
corresponding archives are published; preparing metadata does not publish a release.
Runtime archives contain the native installation and license notices; the
matching-toolchain test probes remain only in CI artifacts.

For a fork PR, the bot cannot write to its branch. The manual fallback is to run
preparation on a branch in this repository and copy the files from that successful
run (also useful for refreshing expired archives):

```sh
gh workflow run julia.yml --ref BRANCH
# Find the completed run's ID with: gh run list --workflow julia.yml
gh run download RUN_ID --name julia-native --dir build/julia-release
cp build/julia-release/Artifacts.toml julia/Artifacts.toml
cp build/julia-release/native-build.toml julia/native-build.toml
git add julia/Artifacts.toml julia/native-build.toml
git commit -m "build(julia): pin prepared native release artifacts"
julia julia/build/artifacts.jl verify build/julia-release
```

BinaryBuilder is a pinned build-only dependency. Our CI builds and audits the
five supported targets without generating a JLL or submitting to Yggdrasil.

## Publish

After all gates pass, create and push an annotated or signed tag:

```sh
git tag -a "v${release_version}" -m "lwbgt v${release_version}"
git push origin "v${release_version}"
```

The [release workflow](../.github/workflows/release.yml) verifies the prepared Julia
archives and their source before publishing anything. It builds the Python/R artifacts,
publishes to TestPyPI, verifies their hashes and installation, then publishes
to PyPI and creates the GitHub release with the exact prepared native archives.
It then tests Julia installation from the tagged subdirectory on all five platforms.
Verify the published version and test
Python and R installation in clean environments using the [README](../README.md).
Require a successful R-universe build for the tagged commit before announcing
its R release. Correct a defective release with a new version; never replace
published artifacts.

After the published Julia installation checks pass, register the **tagged commit**
by commenting `@JuliaRegistrator register subdir=julia` on that commit. Use the
existing annotated `vX.Y.Z` tag for all bindings; no Julia-specific tag or TagBot
workflow is needed. Registration is separate from building and publishing binaries.
Preserve the existing Julia UUID. The all-capitals `LWBGT` name may require a manual
naming exception at initial registration; subdirectory packages need no `.jl`
repository suffix.

## Service setup

Configure PyPI and TestPyPI Trusted Publishing for `release.yml` and its
protected environments. The R-universe registry must point to this repository
with `subdir: "r"` and `branch: "*release"` so it follows GitHub releases.
Install JuliaRegistrator on this repository before the first Julia registration.
Retire the standalone Julia repository and superseded Yggdrasil submission only
after the integrated package has been published and verified.
