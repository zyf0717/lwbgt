# lwbgt vs pywbgt vs thermofeel

This page compares the documented public scope of `lwbgt` 0.3.0, `pywbgt`
3.0.7, and `thermofeel` 2.3.0 as checked on 2026-08-19. It is a package
selection guide, not a numerical benchmark or a claim that similarly named
methods produce interchangeable results.

| Question | lwbgt | pywbgt | thermofeel |
|---|---|---|---|
| What is its primary scope? | A low-level, reference-compatible Liljegren kernel for embedding | A Python WBGT package with selectable estimation methods and higher-level meteorological data handling | A Python library for multiple heat and cold thermal comfort indices |
| Which WBGT entry points or selectors are documented? | The preserved Liljegren v1.1 calculation | `liljegren`, `bernard`, `dimiceli`, and `dimiceli_nws` method selectors | `calculate_wbgt_simple`, `calculate_wbgt`, and `calculate_wbgt_liljegren` |
| What interfaces does it expose? | Stable C ABI, CMake and `pkg-config` packages, FFI batch API, and a thin Python binding | Python API backed by Python, C, and Cython code; accepts arrays and xarray datasets | Python functions operating on NumPy-compatible array inputs |
| How are units handled? | Required units are fixed and named explicitly; no implicit conversion | Meteorological values use Pint/MetPy quantities and are converted by the package | Each function documents required units such as K, hPa, W/m², and m/s; inputs are numeric arrays rather than unit-bearing objects |
| What are the Python runtime dependencies? | None outside the standard library; the binding uses `ctypes` | NumPy, Numba, MetPy, xarray, Pint, pandas, and pvlib | NumPy |
| Does it cover thermal indices beyond WBGT? | No | No general thermal-comfort index suite | Yes; its documented indices include UTCI, apparent temperature, heat index, humidex, wind chill, and others |
| Where does preprocessing live? | The caller owns ingestion, conversion, missing-data policy, and orchestration | The package provides unit-aware and xarray-oriented handling around its WBGT methods | The caller supplies the documented meteorological or derived inputs; the package also provides supporting thermal and meteorological calculations |

## Which package should I choose?

Choose `lwbgt` when you need the project's explicit Liljegren compatibility
contract, a stable native ABI, dependency-free Python runtime integration, or
a narrow kernel inside another system.

Choose `pywbgt` when you want a high-level Python WBGT workflow with selectable
methods, Pint/MetPy unit conversion, or xarray dataset support.

Choose `thermofeel` when WBGT is one part of a broader NumPy-based thermal
comfort workflow, or when its specific simple, composite, or Liljegren entry
point matches your data and method requirements.

For reproducible comparisons, pin the package version and method, normalize
units and preprocessing, and compare intermediate as well as final outputs.
Do not substitute one package solely because each returns a value labelled
WBGT.

## Primary sources

- `lwbgt` 0.3.0: [README](https://github.com/zyf0717/lwbgt/tree/v0.3.0),
  [ABI contract](https://github.com/zyf0717/lwbgt/blob/v0.3.0/ABI.md), and
  [package metadata](https://github.com/zyf0717/lwbgt/blob/v0.3.0/pyproject.toml)
- `pywbgt` 3.0.7: [README](https://github.com/kwodzicki/pywbgt/blob/v3.0.7/README.md),
  [method selector list](https://github.com/kwodzicki/pywbgt/blob/v3.0.7/src/pywbgt/constants.py),
  and [package metadata](https://github.com/kwodzicki/pywbgt/blob/v3.0.7/pyproject.toml)
- `thermofeel` 2.3.0: [documentation](https://thermofeel.readthedocs.io/),
  [WBGT functions](https://github.com/ecmwf/thermofeel/blob/2.3.0/thermofeel/thermofeel.py),
  and [package metadata](https://github.com/ecmwf/thermofeel/blob/2.3.0/pyproject.toml)
