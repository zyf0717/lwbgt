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
[tests/BASELINE.md](tests/BASELINE.md). Extend `tests/generate_extended_cases.py`
without changing the historical corpus or timing workload. Keep the R copies
of `wbgt.c` and `lwbgt.h` byte-identical to their canonical sources.

## Validation

```sh
python3 tests/check_versions.py
python3 tests/check_r_sources.py
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

Use `-DLWBGT_REQUIRE_ALL_BINDING_TESTS=ON` to require R and Julia runtimes.
For Python changes, build and install a wheel in a clean environment, then run
`python -m unittest discover -s tests/python -v`. For R changes, run
`R CMD build r` and `R CMD check` on the archive. Run downstream SwiftPM tests
for C interface or packaging changes.

Performance claims require the [benchmark method](benchmarks/README.md).
Report the compiler/platform and any checks you could not run in the PR.
Follow [RELEASING.md](docs/RELEASING.md) for publication.
