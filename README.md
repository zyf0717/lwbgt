# lwbgt

[![Native CI](https://github.com/zyf0717/lwbgt/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/zyf0717/lwbgt/actions/workflows/ci.yml)
[![Wheel CI](https://github.com/zyf0717/lwbgt/actions/workflows/wheels.yml/badge.svg?branch=main)](https://github.com/zyf0717/lwbgt/actions/workflows/wheels.yml)
[![R package CI](https://github.com/zyf0717/lwbgt/actions/workflows/r.yml/badge.svg?branch=main)](https://github.com/zyf0717/lwbgt/actions/workflows/r.yml)
[![PyPI](https://img.shields.io/pypi/v/lwbgt.svg)](https://pypi.org/project/lwbgt/)
[![R-universe](https://zyf0717.r-universe.dev/lwbgt/badges/version)](https://zyf0717.r-universe.dev/lwbgt)

`lwbgt` implements the Liljegren outdoor wet bulb globe temperature (WBGT)
model in C. It provides a stable numerical backend for weather and heat-stress
software.

Dependency-free Python and R bindings use the same C kernel. SwiftPM exposes
the C interface as `CLWBGT`, and the native C/FFI interface supports other
language bindings.

Callers supply weather data, convert units, choose missing-data policies, and
classify heat risk. For a higher-level Python workflow, consider
[`pywbgt`](https://pypi.org/project/pywbgt/) or
[`thermofeel`](https://pypi.org/project/thermofeel/).

## Compatibility policy

**Version: v1.0.1.** The v1 calculation remains the default throughout the 1.x
series. Changes to defined valid-input numerical results require explicit
versioned APIs, with v1 still available. The original solar-position year
range, 1950–2049, is retained.

Under matched build settings, the 35,976-row WBGT corpus matches the retained
original C bit for bit for `Tg`, `Tnwb`, `Tpsy`, WBGT, and `esat`. Another
1,682 cases check water/ice `esat`, and 996 diagnostics check internal branches.
These sampled comparisons do not guarantee equivalence for every input or
platform.

The original scalar binary ABI is preserved. The intentional output correction
is estimated wind at 2 m: the scalar function now writes the supplied speed,
rounded to `float`; the original left that output unwritten. See
[compatibility and performance](https://github.com/zyf0717/lwbgt/blob/main/docs/COMPATIBILITY.md)
for the comparison scope and limitations. The same corpus provides the
[1×/10× throughput benchmark](benchmarks/README.md).

## Python

```sh
python -m pip install lwbgt
```

```python
from lwbgt import Input, calculate, calculate_batch, esat

weather = Input(
    year=2024, month=4, day=15, hour=14, minute=30,
    gmt_offset_hours=8, averaging_minutes=60, urban=1,
    latitude_deg_north=1.3521, longitude_deg_east=103.8198,
    solar_w_m2=742.0, pressure_hpa=1008.4,
    air_temperature_c=32.1, relative_humidity_percent=68.0,
    wind_speed_m_s=2.8, wind_height_m=10.0,
    vertical_temperature_difference_c=1,
)

result = calculate(weather)
assert result.status == 0
print(result.wbgt_c)

results = calculate_batch([weather, weather])
print(esat(273.15, phase=0))
```

`Input` and `Result` are immutable typed records. Field names, units, status
codes, and failure behaviour are defined by the
[ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md). See the
[input assumptions](https://github.com/zyf0717/lwbgt/blob/main/docs/INPUTS.md)
before substituting unavailable observations.

## R

Install from R-universe:

```r
install.packages("lwbgt", repos = "https://zyf0717.r-universe.dev")
```

Or install the latest GitHub release from the `r/` subdirectory:

```r
install.packages("remotes", repos = "https://cloud.r-project.org")
remotes::install_github("zyf0717/lwbgt/r@*release", upgrade = "never")
```

The R API provides `lwbgt_input()`, `calculate()`, and `esat()`. It returns
ordinary data frames, recycles scalar constructor arguments, and isolates
invalid or non-convergent rows. See the
[R quick start](https://github.com/zyf0717/lwbgt/blob/main/r/README.md).

## SwiftPM

Add the package and its C-library product to a Swift target:

```swift
let package = Package(
    dependencies: [
        .package(url: "https://github.com/zyf0717/lwbgt.git", from: "1.0.0"),
    ],
    targets: [
        .target(
            name: "WeatherService",
            dependencies: [
                .product(name: "CLWBGT", package: "lwbgt"),
            ]
        ),
    ]
)
```

```swift
import CLWBGT
```

`CLWBGT` exposes `lwbgt.h` directly; it is not an idiomatic Swift wrapper.
SwiftPM builds the canonical C sources without vendoring or generated copies.
Linux and macOS downstream consumption are tested in release mode.

## Native C

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
cmake --install build --prefix /desired/prefix
```

The install provides static and shared libraries, `lwbgt.h`, CMake package
metadata, and `pkg-config` metadata. CMake consumers can select
`lwbgt::static` or `lwbgt::shared` after `find_package(lwbgt CONFIG REQUIRED)`.
GCC, Clang/AppleClang, and MinGW GCC are supported. MSVC is unsupported; the
numerical target is built in GNU89 mode.

## Documentation

| Topic | Document |
|---|---|
| Inputs, units, layouts, status codes, and concurrency | [ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md) |
| Numerical compatibility and measured performance | [Compatibility and performance](https://github.com/zyf0717/lwbgt/blob/main/docs/COMPATIBILITY.md) |
| Scope and common integration questions | [FAQ](https://github.com/zyf0717/lwbgt/blob/main/docs/FAQ.md) |
| Package selection | [lwbgt vs pywbgt vs thermofeel](https://github.com/zyf0717/lwbgt/blob/main/docs/COMPARISON.md) |
| Source lineage | [Upstream provenance](https://github.com/zyf0717/lwbgt/blob/main/docs/UPSTREAM.md) |
| Source changes | [Deviations from original Liljegren C](https://github.com/zyf0717/lwbgt/blob/main/docs/DEVIATIONS.md) |
| Release history | [Changelog](https://github.com/zyf0717/lwbgt/blob/main/CHANGELOG.md) |
| Release procedure | [Maintainer guide](https://github.com/zyf0717/lwbgt/blob/main/docs/RELEASING.md) |

## License

Project license: [Apache-2.0](https://github.com/zyf0717/lwbgt/blob/main/LICENSE).

See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and Conventional Commits.
