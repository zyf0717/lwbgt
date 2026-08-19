# lwbgt: Liljegren wet bulb globe temperature kernel

[![Native CI](https://github.com/zyf0717/lwbgt/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/zyf0717/lwbgt/actions/workflows/ci.yml)
[![Wheel CI](https://github.com/zyf0717/lwbgt/actions/workflows/wheels.yml/badge.svg?branch=main)](https://github.com/zyf0717/lwbgt/actions/workflows/wheels.yml)
[![PyPI version](https://img.shields.io/pypi/v/lwbgt.svg)](https://pypi.org/project/lwbgt/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/lwbgt.svg)](https://pypi.org/project/lwbgt/)
[![License](https://img.shields.io/pypi/l/lwbgt.svg)](https://github.com/zyf0717/lwbgt/blob/main/LICENSING.md)

`lwbgt` is a stable, low-level C/FFI computational kernel for Liljegren outdoor
wet bulb globe temperature (WBGT). Derived from the Liljegren WBGT v1.1 C
implementation, it preserves the original scalar ABI and documented numerical
behaviour while removing demonstrably repeated or dead work. It is intended to
be embedded as a numerical backend by higher-level scientific packages,
services, and high-throughput data pipelines.

Python is an official, dependency-free `ctypes` binding to that same native
kernel. Install a self-contained binary wheel with `pip install lwbgt`. Input
units are explicit in field names and are never converted implicitly. The
package intentionally does not add dataframe/xarray models, meteorological
preprocessing, classifications, advisory policy, or alternate WBGT methods.
For those higher-level workflows, consider
[`pywbgt`](https://pypi.org/project/pywbgt/) or
[`thermofeel`](https://pypi.org/project/thermofeel/).

**Release status: v0.3.0.** v0.1.0 is the frozen scalar-compatibility release.
Its complete permitted optimization set measures
1.316× on the primary GCC 13 benchmark and 1.289× in the GCC 16.2 container.
The v0.2.0 position-independent static build measures 1.249× on the GCC 13
host. All three results exceed the mandatory 1.20× gate with exact
compatibility. These are narrowly supported throughput measurements on the
documented environments and workloads, not broader portability claims.

It is not affiliated with or endorsed by the original authors, UChicago
Argonne, or the U.S. Department of Energy.

This distribution contains a modified Liljegren WBGT v1.1 derivative. Binary
and source redistributions must retain the UChicago Argonne/Department of
Energy acknowledgement in
[NOTICE](https://github.com/zyf0717/lwbgt/blob/main/NOTICE) and comply with
[LICENSING.md](https://github.com/zyf0717/lwbgt/blob/main/LICENSING.md).

## Find the right documentation

- **How do I calculate outdoor wet bulb globe temperature in Python?** Start
  with the [installation and quick-start example](#python-installation-and-quick-start).
- **Which Python WBGT package should I use?** See the factual
  [lwbgt vs pywbgt vs thermofeel comparison](https://github.com/zyf0717/lwbgt/blob/main/COMPARISON.md).
- **What inputs, units, status codes, and native interfaces does lwbgt use?**
  Read the [ABI and API contract](https://github.com/zyf0717/lwbgt/blob/main/ABI.md).
- **Does lwbgt convert units, accept xarray objects, or classify heat risk?**
  Read the [wet bulb globe temperature FAQ](https://github.com/zyf0717/lwbgt/blob/main/FAQ.md).

## Python installation and quick start

```sh
python -m pip install lwbgt
```

```python
from lwbgt import Input, calculate, esat

weather = Input(
    year=2024, month=4, day=15, hour=14, minute=30,
    gmt_offset_hours=8, averaging_minutes=60, urban=1,
    latitude_deg_north=1.3521, longitude_deg_east=103.8198,
    solar_w_m2=742.0, pressure_hpa=1008.4,
    air_temperature_c=32.1, relative_humidity_percent=68.0,
    wind_speed_m_s=2.8, wind_height_m=10.0,
    vertical_temperature_difference_c=-0.4,
)
result = calculate(weather)
assert result.status == 0
print(result.wbgt_c)
print(esat(273.15, phase=0))
```

Batch calculation uses the native serial batch entry point rather than a
Python loop:

```python
from lwbgt import calculate_batch

results = calculate_batch([weather, weather])
```

`Input` and `Result` are immutable typed records. Their complete field names,
units, solver status, and `-9999` failure convention map directly to ABI v1;
see [ABI.md](https://github.com/zyf0717/lwbgt/blob/main/ABI.md). No third-party
Python runtime dependency is required.

## Purpose

`lwbgt` owns the numerical Liljegren calculation, stable C/FFI contracts,
reproducible compatibility evidence, and low-level static/shared-library
distribution. Higher-level callers own table and dataframe APIs,
meteorological data ingestion, unit conversion beyond the documented ABI,
missing-data policy, additional domain validation, classification and advisory
systems, orchestration and parallelism, and application-specific defaults.
This narrow boundary is intentional.

```text
Applications / research pipelines
              |
      Python / R / Julia / services
              |
            lwbgt
              |
   Liljegren WBGT numerical model
```

## When to use lwbgt

Use `lwbgt` when you need a stable C or FFI Liljegren backend; behaviour
anchored to the original Liljegren C implementation; an embedded WBGT kernel
for another package or service; high-volume calculation with preprocessing
kept outside the kernel; or an auditable, reference-compatible numerical
backend within the documented compatibility scope.

## When not to use lwbgt directly

A higher-level package is more appropriate when the primary requirement is
dataframe-oriented ergonomics, automatic weather-data preprocessing, policy or
heat-risk classifications, a batteries-included Python/R/Julia API, or GPU/JAX
execution.

## Native build and install

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
cmake --install build --prefix /desired/prefix
```

The build produces `liblwbgt.a` and a versioned shared library and installs
`lwbgt.h`, CMake package metadata, and `pkg-config` metadata. Core compilation is
GNU89 with `-fno-fast-math -ffp-contract=off -fno-strict-aliasing`; LTO and
architecture-specific flags are not enabled. GCC, Clang/AppleClang, and MinGW
GCC are supported; MSVC cannot compile the preserved K&R source.

Installed CMake consumers can select `lwbgt::static` or `lwbgt::shared` after
`find_package(lwbgt CONFIG REQUIRED)`.

## Supported API and compatibility contract

[ABI.md](https://github.com/zyf0717/lwbgt/blob/main/ABI.md) defines the
authoritative layouts, units, error behavior,
concurrency rules, symbol surface, and compatibility policy.

The legacy `calc_wbgt` and `esat` declarations in `include/lwbgt.h` remain the
permanent scalar compatibility ABI. Scalar floating-point arguments use
`double` at the ABI boundary because the original K&R `float` parameters undergo
default argument promotion; output pointers remain `float *`.

The v1 FFI ABI adds fixed-layout `lwbgt_input_v1` and `lwbgt_output_v1`
structures and `lwbgt_calc_batch_v1`. The batch call executes scalar calls in
input order. It returns the supplied wind as the effective 2-m wind when no
height conversion is needed, avoiding the legacy scalar routine's untouched
output-pointer behavior. It performs no allocation, retains no caller pointers,
and introduces no domain validation, clamping, unit conversion, or
missing-value policy beyond inherited scalar behaviour. Input and output arrays
must not overlap. Independent calls using separate buffers are thread-safe; a
single batch call is serial.

The shared library exports only `calc_wbgt`, `esat`, and
`lwbgt_calc_batch_v1`. The static archive retains global helper symbols inherited
from the source implementation; they remain unsupported implementation details.
The exported-symbol review is recorded in `tests/API.md`.

The maintained Python package and minimal R and Julia examples demonstrate the
intended integration pattern: higher-level packages can bind the stable ABI
while owning their user-facing policies. The R and Julia examples are tested
interoperability examples, not registry packages, and no compatibility claim is
made for third-party wrappers.

The exact upstream source is retained unmodified at
`upstream/wbgt.c.original`. `src/wbgt.c` is the modified derivative maintained
by Yifei/HeatStressDev. HeatStressBench's frozen `liljegren-c` target remains
the oracle and is not replaced or relabelled.

Numerical provenance and the exact-compatibility scope are documented in
[ABI.md](https://github.com/zyf0717/lwbgt/blob/main/ABI.md),
[UPSTREAM.md](https://github.com/zyf0717/lwbgt/blob/main/UPSTREAM.md), and the
[retained test evidence](https://github.com/zyf0717/lwbgt/tree/main/tests).

For matched compilers and floating-point flags, the acceptance policy is exact
32-bit equality for return status, estimated wind speed, `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat`. The deterministic 454-case suite produces the same
`087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff`
probe hash with GCC 13.3.0 and GCC 16.2.0.

## Evidence

| Environment | Exact result | Median overall speedup | Release gate |
|---|---:|---:|---:|
| Linux x86-64, GCC 13.3.0 | bit-identical | 1.316× | passed |
| Linux x86-64 container, GCC 16.2.0 | bit-identical | 1.289× | passed |
| Linux x86-64, GCC 13.3.0, v0.2.0 PIC build | bit-identical | 1.249× | passed |

Every v0.1.0 benchmark cohort exceeds 1.25×. The v0.2.0 PIC build passes the
unchanged overall and per-cohort gates, with a 1.210× slowest measured cohort.
Detailed host results, hardware, flags, datasets, warm-up, CPU-affinity policy,
repetitions, medians, and dispersion are under `benchmarks/`. HeatStressBench
adapter evidence is under `tests/`.

## Licence and provenance

Project-authored files are licensed under
[Apache-2.0](https://github.com/zyf0717/lwbgt/blob/main/LICENSE). The retained
upstream source and modified derivative remain under the UChicago Argonne
Liljegren WBGT v1.1 terms.
[LICENSING.md](https://github.com/zyf0717/lwbgt/blob/main/LICENSING.md) defines
the file-level boundary and redistribution requirements.

`UPSTREAM.md` records the repository, pinned commit, blob, import date, and
relationship to HeatStressBench. The complete upstream source licence is in
`LICENSES/LicenseRef-UChicago-Argonne-WBGT-1.1.txt`; the required
Argonne/Department of Energy acknowledgement is in `NOTICE`.

## Explicit non-goals

This release adds no high-level dataframe/xarray API, unit conversion,
meteorological ingestion, dew-point policy, classification thresholds,
alternate solver, precision change, new physics, cache, parallelism, OpenMP,
SIMD, GPU path, or fast-math mode.
