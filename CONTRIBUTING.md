# Contributing

Keep changes small, readable, and scientifically justified. Explain the problem,
resulting behavior, and validation. Record units, timestamp conventions,
numerical assumptions, and data provenance where relevant.

## Commits

Use Conventional Commits: `<type>[optional scope]: <description>`.
Common types are `fix`, `feat`, `test`, `perf`, `docs`, `refactor`, `ci`, and
`chore`. Keep each commit focused and use a short imperative description:

```text
test(numerics): cover adjacent float wind thresholds
docs: explain oracle comparison limits
```

Describe rationale and validation in the body when needed. Mark breaking
changes with `!` or a `BREAKING CHANGE:` footer and follow the
[ABI contract](docs/ABI.md).

## Numerical changes

Preserve the v1 calculation, native floating-point flags, intermediate rounding,
and [compatibility policy](docs/COMPATIBILITY.md). Do not edit the retained
oracle, `upstream/wbgt.c.original`.

Add regression cases and compare statuses and output bits in matched builds.
Rejected solar and non-finite weather inputs need separate API checks; see
[tests/BASELINE.md](tests/BASELINE.md). Extend the shared corpus in
`tests/generate_cases.py` and refresh `tests/baseline.json`. Rerun throughput
measurements when the corpus changes. Keep the R copies of `wbgt.c` and
`lwbgt.h` byte-identical to their canonical sources.

## Validation

PRs and branch pushes do not start CI. In **Actions → Validate → Run workflow**,
select the branch and **All checks** to run native/Swift, Python, R, and Julia
validation. The run tests the selected commit, not a simulated merge; update the
branch from `main` first when needed. Review its commit and results in Actions
before merging. Later pushes require another manual run; starting one cancels
older validation on the same branch.

For prepared release metadata, select **Prepared Julia artifacts** instead; it
verifies the source and archive hashes and tests installation without rebuilding.
Neither option writes commits or publishes. See [RELEASING.md](docs/RELEASING.md)
for manual Julia preparation and tag-triggered publication.

```sh
python3 tests/check_versions.py
python3 tests/check_r_sources.py
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

For Python changes, build and install a wheel in a clean environment, then run
`python -m unittest discover -s tests/python -v`. For R changes, run
`R CMD build r` and `R CMD check` on the archive. Run downstream SwiftPM tests
for C interface or packaging changes, including the native numerical comparison:

```sh
build/lwbgt_probe build/cases.csv > build/swift-expected.csv
LWBGT_CASES="$PWD/build/cases.csv" \
LWBGT_EXPECTED="$PWD/build/swift-expected.csv" \
swift test --package-path tests/swiftpm -c release -Xcc -march=native
```

For Julia changes, run `julia --project=julia julia/test/runtests.jl` with
`LWBGT_LIBRARY` pointing to the built shared library, and run
`julia julia/test/packaging.jl`. The Julia checks also test the actual archives
on five platforms with Julia 1.10 and current stable, comparing them with probes
built using the same toolchain and the retained original. No native integration
tests are silently skipped when a library is unavailable.

Performance claims require the [benchmark method](benchmarks/README.md).
Windows CI also tests an opt-in MSVC build (`LWBGT_EXPERIMENTAL_MSVC=ON`) and
uploads cross-compiler numerical reports. Finite values must match exactly;
NaN payload differences are allowed. Inspect those reports before claiming
compatibility beyond the tested corpus and platform.
Report the compiler/platform and any checks you could not run in the PR.
Follow [RELEASING.md](docs/RELEASING.md) for publication.
