# v0.2.0 release verification

v0.2.0 leaves the frozen numerical source unchanged and adds a versioned batch
FFI, static/shared installation metadata, and tested Python, R, and Julia
interoperability examples.

On 2026-08-18, release-preparation commit
`cd7f986f16c8bcddea34e03a4d7580fa2acad7e5` was cloned locally with
`git clone --no-hardlinks` into a separate directory. The checkout reported no
tracked or untracked changes before configuration.
The subsequent evidence-only commit changes no library, binding, build, or test
code.

The clean-checkout verification command set is:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DLWBGT_REQUIRE_ALL_BINDING_TESTS=ON
cmake --build build --clean-first --parallel
ctest --test-dir build --output-on-failure
python3 tests/compare.py exact \
  build/lwbgt_reference_probe build/lwbgt_probe build/cases.csv
python3 tests/compare.py benchmark \
  build/lwbgt_reference_benchmark build/lwbgt_benchmark build/cases.csv \
  build/v0.2.0-benchmark.json 7 200
```

All eight CTest tests passed, including the three-symbol shared export audit,
both installed CMake consumers, and the Python, R, and Julia examples. The
explicit differential run reported 454 bit-identical cases with the frozen
probe SHA-256:

```text
087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff
```

The clean-checkout benchmark measured 1.2487× overall median throughput against
the reference, above the mandatory 1.20× gate. Every per-cohort no-regression
gate passed; the slowest measured cohort was NASA POWER at 1.2100×. The tracked
report and environment are `../benchmarks/v0.2.0-gcc-13.3.0.json` and
`../benchmarks/v0.2.0-environment.json`.

The same library and test tree passed GitHub Actions on Linux/GCC,
macOS/AppleClang, and Windows/MinGW in
[run 32108617717](https://github.com/zyf0717/lwbgt/actions/runs/32108617717).
The workflow covered configuration, static and shared builds, all eight CTest
tests, installed consumers, and all three language examples.

The historical v0.1.0 clean-checkout record is retained in
`RELEASE-0.1.0.md`. HeatStressBench adapter compatibility evidence remains in
`HEATSTRESSBENCH.md`.
