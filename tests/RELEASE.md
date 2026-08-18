# v0.2.0 release verification

v0.2.0 leaves the frozen numerical source unchanged and adds a versioned batch
FFI, static/shared installation metadata, and tested Python, R, and Julia
interoperability examples. The final release gate requires a clean checkout of
the release-preparation commit.

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

Acceptance requires all eight CTest tests, the frozen 454-case probe hash,
the 1.20× overall performance gate, every per-cohort no-regression gate, the
three-symbol shared export audit, both installed CMake consumers, and the
Python, R, and Julia examples to pass. Cross-platform CI must independently
pass on Linux/GCC, macOS/AppleClang, and Windows/MinGW before tagging.

The historical v0.1.0 clean-checkout record is retained in
`RELEASE-0.1.0.md`. HeatStressBench adapter compatibility evidence remains in
`HEATSTRESSBENCH.md`.
