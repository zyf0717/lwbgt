# lwbgt wet bulb globe temperature FAQ

## What does lwbgt calculate?

`lwbgt` calculates outdoor wet bulb globe temperature (WBGT) with the
Liljegren model. It also exposes the model's globe temperature, natural
wet-bulb temperature, psychrometric wet-bulb temperature, and estimated 2 m
wind speed outputs.

## How do I calculate outdoor WBGT in Python?

Install the binary wheel with `python -m pip install lwbgt`, populate an
[`lwbgt.Input`](https://github.com/zyf0717/lwbgt#python),
and pass it to `lwbgt.calculate`. Use `lwbgt.calculate_batch` for multiple
records; it calls the native serial batch entry point rather than looping in
Python.

## Which weather inputs does lwbgt require?

The input record includes date and time, UTC offset, averaging interval,
urban/rural flag, latitude, longitude, solar irradiance, pressure, air
temperature, relative humidity, wind speed and measurement height, and
vertical temperature difference. The authoritative field definitions and
units are in the [ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md).

## What should I use when an input is unavailable?

The library does not apply defaults. See the
[input assumptions](https://github.com/zyf0717/lwbgt/blob/main/docs/INPUTS.md)
for acceptable derivations and conditional fallbacks; core weather
observations have no general fallback.

## Does lwbgt convert units?

No. Units are explicit in Python field names and in the C ABI documentation.
The caller must convert source data to those units before calling `lwbgt`.

## Does lwbgt accept NumPy, pandas, or xarray objects directly?

No. The Python API accepts immutable `Input` records or iterables of them and
returns `Result` records. Dataframe, xarray, ingestion, and missing-data policy
belong in the calling application.

## Is lwbgt the same package as pywbgt?

No. Both expose Liljegren WBGT calculations, but their scope, APIs, unit
handling, supported methods, and compatibility contracts differ. See
[lwbgt vs pywbgt vs thermofeel](https://github.com/zyf0717/lwbgt/blob/main/docs/COMPARISON.md)
before choosing or substituting a package.

## How does lwbgt differ from thermofeel?

`lwbgt` is a narrow native Liljegren kernel with a stable C ABI, Python and R
APIs, and a SwiftPM C-library product.
`thermofeel` is a NumPy-based Python library covering multiple thermal comfort
indices and multiple WBGT calculation functions. The
[comparison page](https://github.com/zyf0717/lwbgt/blob/main/docs/COMPARISON.md)
lists the documented differences.

## Does lwbgt provide WBGT risk categories or exposure limits?

No. It returns physical calculation results, not health guidance,
classification thresholds, work/rest schedules, or advisory policy. Apply the
authoritative policy for the relevant jurisdiction and population outside the
kernel.

## Is lwbgt numerically identical to every Liljegren implementation?

No cross-package equivalence is claimed. Within lwbgt's documented scope,
matched compilers and floating-point flags reproduce the retained oracle
exactly for previously valid outputs except the corrected direct scalar 2 m
wind output. See the [ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md)
and the [test evidence](https://github.com/zyf0717/lwbgt/tree/main/tests).

## Can I call lwbgt from C, C++, Swift, R, or Julia?

Yes. The installed native package provides CMake and `pkg-config` metadata and
a stable C ABI. SwiftPM exposes that header through `CLWBGT`; the official R
package is under [`r/`](https://github.com/zyf0717/lwbgt/tree/main/r). The
repository also includes tested
[C/C++](https://github.com/zyf0717/lwbgt/tree/main/tests/consumer) and
[Julia](https://github.com/zyf0717/lwbgt/tree/main/examples/julia) consumers.
