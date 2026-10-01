# Contributing

Keep changes small, readable, and scientifically justified. Explain the input
that exposes a problem, the resulting behavior, and how you verified it.
Record units, timestamp conventions, numerical assumptions, and data provenance
where relevant. Use synthetic examples when source provenance is unavailable.

## Commits

Use Conventional Commits:

```text
<type>[optional scope]: <description>
```

Use `fix` for bug fixes, `feat` for new functionality, `test` for coverage,
`perf` for performance changes, `docs` for documentation, `refactor` for code
restructuring, `ci` for automation, and `chore` for maintenance. Prefer a short
imperative description and a scope such as `numerics`, `python`, `r`, or
`release` when it helps. Examples:

```text
test(numerics): cover adjacent float wind thresholds
docs: describe oracle comparison limits
chore(release): prepare v1.0.2
```

Keep each commit focused. Describe the rationale and validation in the body
when the title is insufficient. Conventional Commits marks breaking changes
with `!` or a `BREAKING CHANGE:` footer; that notation does not authorize
breaking an existing interface. Follow the [ABI contract](docs/ABI.md).

## Numerical and API changes

The retained original in `upstream/wbgt.c.original` is the compatibility oracle;
do not edit it. The default v1 calculation must remain available throughout
1.x. Changes to defined valid-input results require explicit versioned APIs.
Preserve the native floating-point flags and intermediate rounding behavior.

Add permanent regression cases for a new numerical failure. Compare both
statuses and output bits against the retained original in the same build.
Rejected solar inputs require current-API contract tests because the original
consumes unwritten outputs there. Preserve the historical 852-case generator
and 840-row performance workload; extend coverage in
`tests/generate_extended_cases.py`. See [the baseline](tests/BASELINE.md) for
ranges, seeds, convergence counts, and reproduction commands.

Keep `r/src/wbgt.c` and `r/src/lwbgt.h` byte-identical to their canonical
sources. Do not change model constants, units, failure semantics, layouts, or
exported symbols without explaining their compatibility implications.

## Validation

From the repository root:

```sh
python3 tests/check_versions.py
python3 tests/check_r_sources.py
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

CTest runs the historical and expanded native comparisons, Python runtime
comparisons, water/ice saturation tests, internal branch diagnostics, batch
checks, and installed C/C++ consumers. R and Julia examples run when their
runtimes are available; use `-DLWBGT_REQUIRE_ALL_BINDING_TESTS=ON` to require them.

For Python changes, build and install a wheel in a clean environment, then run:

```sh
python -m unittest discover -s tests/python -v
```

For R changes, run `R CMD build r` and `R CMD check` on the resulting archive.
Run the SwiftPM downstream tests when changing the C interface or packaging.
Performance claims require the documented [benchmark method](benchmarks/README.md).
Report the compiler/platform and any checks you could not run in the PR.

Synchronize release metadata with `tests/check_versions.py`; follow
[the release process](docs/RELEASING.md) for release gates and publication.
