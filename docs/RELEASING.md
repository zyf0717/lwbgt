# Releasing

C, Python, R, Julia, and SwiftPM share one version and Git tag. Test and
documentation changes can stay under `Unreleased`; publishing packages requires
a new version. SwiftPM uses the tag directly and builds the C sources.

| Workflow | Trigger | Purpose |
|---|---|---|
| Validate | Manual, selected branch | All language checks, or verification of prepared Julia artifacts |
| Prepare Julia release | Manual, `main` | Build/test Julia archives and open the metadata PR |
| Release | Annotated `v*` tag push | Verify artifacts, publish packages, and test published Julia installation |

PRs and branch pushes do not start project CI. See
[Contributing](../CONTRIBUTING.md#validation) for validation and branch selection.

## Prepare

1. Update shared version metadata, `CHANGELOG.md`, `r/NEWS.md`, and
   `tests/RELEASE.md`. For numerical changes, refresh the
   [baseline](../tests/BASELINE.md) and [benchmarks](../benchmarks/README.md).
2. Run **Validate → All checks** on the development branch. Review the tested
   commit and results, then merge the version bump and release notes into `main`.
3. Start **Prepare Julia release** on `main`:

   ```sh
   gh workflow run julia.yml --ref main
   ```

Preparation requires an untagged version. It builds and tests five native targets
using pinned BinaryBuilder tooling, then opens `codex/julia-release-vX.Y.Z` with:

- `julia/Artifacts.toml`: release URLs and archive/content hashes.
- `julia/native-build.toml`: source commit, source-tree digest, and preparation run.

Preparation runs only Julia checks, including native-oracle comparisons. It
neither tags nor publishes; download URLs work after publication.

## Verify the metadata PR

Wait for preparation to succeed, then select the metadata PR's branch in
**Validate** and choose **Prepared Julia artifacts**:

```sh
release_version=$(awk -F '"' '/^version = / {print $2; exit}' pyproject.toml)
gh workflow run validate.yml --ref "codex/julia-release-v${release_version}" \
  -f checks='Prepared Julia artifacts'
```

This authenticates the preparation run, compares committed metadata with its
output, verifies the source and archive hashes, and tests installation from the
prepared Linux archive. It reuses the archives without running build matrices.

Review and merge the metadata PR manually. Source identity excludes only the two
generated files, so squash/rebase merges are supported. If `main` advances during
preparation, PR creation fails. Any later source change makes the archives stale;
prepare again before tagging. CI archives expire after 90 days.

## Publish

Check out the merged metadata commit, confirm its version, then create and push
an annotated or signed tag:

```sh
release_version=$(awk -F '"' '/^version = / {print $2; exit}' pyproject.toml)
git tag -a "v${release_version}" -m "lwbgt v${release_version}"
git push origin "v${release_version}"
```

The release workflow verifies the prepared Julia archives, builds/tests Python
and R packages, and publishes Python to TestPyPI. After hash and installation
checks, it publishes the same Python files to PyPI and attaches Python, R, and
prepared Julia archives to the GitHub release. It then tests Julia installation
from the tagged subdirectory on all five platforms.

Wait for the entire run to succeed. Check Python/R installation using the
[README](../README.md), and require a successful R-universe build of the tagged
commit before announcing its R release. CRAN submission is separate.

After Julia's published-installation checks pass, comment on the **tagged commit**:

```text
@JuliaRegistrator register subdir=julia
```

Keep the existing Julia UUID. The shared `vX.Y.Z` tag is sufficient; a separate
Julia tag or TagBot workflow is unnecessary. Correct defective releases with a
new version; never replace published artifacts.

## Service setup

- Configure PyPI and TestPyPI Trusted Publishing for `release.yml` and its environments.
- Point R-universe to this repository with `subdir: "r"` and `branch: "*release"`.
- Install JuliaRegistrator on this repository for General registration.
- Allow GitHub Actions to create PRs under **Settings → Actions → General**.
  Keep the default token read-only; preparation/publication request write access
  only for the jobs that need it. No additional token or CI approval environment
  is required. Merge decisions remain manual.
