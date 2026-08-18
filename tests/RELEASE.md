# v0.2.1 release verification

v0.2.1 is a distribution and ABI-documentation patch. It does not change the
frozen numerical implementation, scalar ABI, v1 batch runtime behavior, shared
symbol surface, or floating-point flags. It adds an explicit Apache-2.0 default
licence with upstream exceptions, installs the complete licence and ABI
document set, enforces every v1 field offset at compile time, and adds an
installed C++ consumer.

The clean-checkout verification command set is:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DLWBGT_REQUIRE_ALL_BINDING_TESTS=ON
cmake --build build --clean-first --parallel
ctest --test-dir build --output-on-failure
python3 tests/compare.py exact \
  build/lwbgt_reference_probe build/lwbgt_probe build/cases.csv
sha256sum LICENSE
```

Acceptance requires all eight CTest tests, including installed C, C++, Python,
R, and Julia consumers; the installed licence, notice, and ABI documents; the
three-symbol shared export audit; and the frozen 454-case exact probe hash. The
Apache-2.0 text must have SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.

No performance rerun is required because the numerical source and runtime code
paths are unchanged. The v0.2.0 performance and compatibility evidence remains
applicable and is retained in `RELEASE-0.2.0.md` and `../benchmarks/`.

Cross-platform CI must independently pass on Linux/GCC, macOS/AppleClang, and
Windows/MinGW before tagging. Historical v0.1.0 and v0.2.0 clean-checkout
records are retained in `RELEASE-0.1.0.md` and `RELEASE-0.2.0.md`.
