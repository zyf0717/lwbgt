# Release process

The v0.3 release artifacts are five Python-ABI-independent platform wheels and
one source distribution. `.github/workflows/wheels.yml` builds, repairs,
inspects, and tests them. `.github/workflows/release.yml` invokes that same
artifact workflow for an annotated `v*` tag and publishes only its downloaded
outputs; the OIDC-enabled publish job does not rebuild.

## One-time PyPI configuration

1. Satisfy PyPI account recovery and 2FA prerequisites.
2. Create the `lwbgt` project or a pending Trusted Publisher.
3. Configure the publisher for repository `zyf0717/lwbgt`, workflow
   `release.yml`, and GitHub environment `pypi`.
4. Create the protected GitHub environment `pypi`; require reviewer approval if
   desired. Do not add a PyPI API token.
5. Create a distinct `testpypi` GitHub environment and configure a TestPyPI
   pending Trusted Publisher for repository `zyf0717/lwbgt`, workflow
   `release.yml`, and environment `testpypi`.

Each publish job grants only `contents: read` and `id-token: write`. PyPI
attestations remain enabled through the official PyPA publish action.

## Release sequence

1. Require green native CI and wheel CI on the exact release commit.
2. Download the wheel-workflow artifacts and independently run:

   ```sh
   python tests/check_versions.py
   python tests/check_distribution.py dist/*
   python -m twine check dist/*
   ```

3. Create an annotated or signed tag on the verified commit:

   ```sh
   git tag -s v0.3.0 -m "lwbgt v0.3.0"
   git push origin v0.3.0
   ```

4. The release workflow rebuilds from that immutable tag and reruns all
   artifact gates. It then uploads the exact six artifacts through the
   `testpypi` environment. A separate non-OIDC job downloads the compatible
   wheel from TestPyPI, verifies all six published filenames and SHA-256 values
   against the tested artifact set, verifies the downloaded wheel bytes, and
   runs the full installed-wheel suite.
5. Production publishing through the `pypi` environment cannot start until the
   TestPyPI identity and smoke gate passes. The workflow then creates a GitHub
   release with the same six artifacts.
6. Verify the PyPI metadata, license expression/files, wheel matrix,
   attestations, repository link, and a clean `pip install lwbgt` smoke test.
7. Never delete and re-upload a defective PyPI version; issue a patch release.
   If production publishing alone fails after the TestPyPI gate succeeds, use
   GitHub's **Re-run failed jobs** operation so the successful TestPyPI upload
   is not attempted a second time.
