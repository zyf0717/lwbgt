# Releasing

Test, benchmark, and documentation changes can merge without a package
release. Keep the current version and record them under `Unreleased`. Publishing
new package artifacts requires a new version.

Release from a commit with passing native, SwiftPM, Python wheel, R, and Julia CI.
Use the workflow definitions as the source of truth for supported platforms.

SwiftPM takes its package version from the shared Git tag (for example, `v1.1.0`).
`Package.swift` has no release-version field; `swift-tools-version: 5.9` specifies
the minimum tools version. The README's `from: "1.0.0"` dependency permits
compatible 1.x releases, including 1.1.0. SwiftPM builds the C sources directly
and needs no separate binary publication.

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

PRs and branch pushes do not start project CI. Manually run **Validate** on the
development branch with **All checks** selected, and review the tested commit
before merging. It tests the selected branch commit, not a simulated merge;
update the branch from `main` first when needed. Later pushes require a fresh
manual run. GitHub-managed dependency indexing may still run independently.
Merge the shared version bump and release notes into `main`, then start the
**Prepare Julia release** workflow manually on `main`:

```sh
gh workflow run julia.yml --ref main
```

Manual preparation requires `main` and an untagged version. It runs the full Julia
platform tests, including comparison with the native oracle, then verifies the
archives and opens or updates `codex/julia-release-vX.Y.Z`, a separate release PR
containing only:

- `julia/Artifacts.toml`: platform-specific release URLs and hashes.
- `julia/native-build.toml`: the tested source commit, source-tree digest, and CI run.

Wait for preparation to finish successfully, then manually run **Validate** on
the metadata PR's branch with **Prepared Julia artifacts** selected:

```sh
gh workflow run validate.yml --ref "codex/julia-release-v${release_version}" \
  -f checks='Prepared Julia artifacts'
```

This authenticates the successful preparation run, compares the committed
metadata with its output, verifies source and archive hashes, and tests
installation from the prepared Linux archive. It runs no build matrices.
Use **All checks** for development changes; preparation and tag publication
remain separate. Tag publication rebuilds/tests Python and R; Julia preparation
does not repeat their checks or native/Swift CI.

Review and merge the release PR manually, then tag its merged commit. Squash or
rebase merging is supported because source identity is checked by tree content,
excluding only the two generated files. If `main` advances during preparation, the
workflow refuses to open the PR; start preparation again. If source changes after
the PR opens, its metadata verification or the tag preflight rejects the stale
archives. Reprepare after source changes or if the 90-day CI artifacts expire.

Generated URLs become usable only after the corresponding archives are published.
Preparation neither tags nor publishes a release. Runtime archives contain the
native installation and license notices; matching-toolchain probes remain only
in CI artifacts. To inspect a preparation locally:

```sh
gh run download RUN_ID --name julia-native --dir build/julia-release
julia -e 'include("julia/build/artifacts.jl"); verify("build/julia-release", "build/julia-release/Artifacts.toml", "build/julia-release/native-build.toml")'
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
Allow GitHub Actions to create pull requests under **Settings → Actions → General
→ Workflow permissions**. Keep the default token read-only; only the manual
release-PR job requests contents/PR write permissions. The built-in token is enough;
no additional app or personal token is required. Validation is manually dispatched
and needs no approval environment. Merge decisions remain manual.

Install JuliaRegistrator on this repository before the first Julia registration.
Retire the standalone Julia repository and superseded Yggdrasil submission only
after the integrated package has been published and verified.
