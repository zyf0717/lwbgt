# Language binding examples

These examples call `lwbgt_calc_batch_v1` through Python `ctypes`, Julia
`ccall`, and a registered R `.Call` bridge. Use the official
[Python](../README.md#python) or [R](../r/README.md) package for normal use;
these examples demonstrate lower-level interoperability.

Build and run the available-language examples with CTest:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

Missing R or Julia runtimes are skipped. Set
`-DLWBGT_REQUIRE_ALL_BINDING_TESTS=ON` to require all three.
