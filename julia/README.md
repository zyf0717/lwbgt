# LWBGT

Julia ≥1.10 binding to the reference-compatible Liljegren C kernel. The package
lives in the `julia` subdirectory of [lwbgt](https://github.com/zyf0717/lwbgt).

Install with `using Pkg; Pkg.add("LWBGT")`. A published tag can also
be installed with `Pkg.add(url="https://github.com/zyf0717/lwbgt.git",
subdir="julia", rev="vX.Y.Z")`, replacing the version with a published Julia release.

## API

`Input` and `Result` are immutable records matching the native v1 ABI.
`calculate(input)` returns one result; `calculate_batch(records)` returns results
in input order through one serial native call. `calculate(inputs::AbstractVector)`
also accepts a batch. `esat(temperature_k; phase=0)` returns saturation vapour
pressure in hPa; phase 0 is water and phase 1 is ice.

See the [Julia quick start](https://github.com/zyf0717/lwbgt#julia) for a complete
input record and scalar/batch examples.

Field names encode units. There is no extra validation, clamping, missing-value
policy, or implicit weather assumption. Status -1 reports solar-position rejection
or solver non-convergence; failed outputs retain the C kernel's `-9999.0f0`
convention. See the [ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md).

## Native library

Published packages fetch a content-addressed native archive on the first calculation.
Supported targets are Linux glibc x86_64/aarch64, macOS x86_64/aarch64, and Windows
x86_64. Users need no compiler. Independent calls use separate output buffers and
are thread-safe. Empty batches and record construction do not load the library.

For development, build the C library from the repository root and explicitly select it:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
LWBGT_LIBRARY="$PWD/build/liblwbgt.so" julia --project=julia julia/test/runtests.jl
```

Use `liblwbgt.dylib` on macOS or `lwbgt.dll` on Windows. `LWBGT_LIBRARY` takes
precedence over artifacts; it must name an existing compatible library. There is
no automatic search of system library paths. A process keeps the first loaded
library; restart Julia after changing the override.

The Julia wrapper is Apache-2.0 licensed. The native kernel also carries the
Argonne license reproduced in [THIRD_PARTY_NOTICE.md](THIRD_PARTY_NOTICE.md).
