# Language binding examples

These dependency-light examples call the versioned `lwbgt_calc_batch_v1` C ABI.
They demonstrate the intended integration pattern: higher-level language
packages can bind the stable ABI while owning their user-facing policies. They
are tested interoperability checks and starting points, not maintained PyPI,
CRAN, or Julia registry packages, and they make no compatibility commitment for
third-party wrappers.

Build the shared library and run every installed-language example through CTest:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

Python uses `ctypes`, Julia uses `ccall`, and R uses a small registered `.Call`
bridge because R cannot directly marshal arrays of C structures. Missing R or
Julia runtimes are skipped locally; use `-DLWBGT_REQUIRE_ALL_BINDING_TESTS=ON`
to make all three mandatory.
