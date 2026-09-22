# ABI contract

This document defines the supported binary interface for lwbgt. Public symbols
and layouts described here are compatibility commitments; other link-visible
symbols in the static archive are implementation details.

## Versioning

The project release version and FFI ABI version are independent:

- `LWBGT_VERSION_MAJOR`, `LWBGT_VERSION_MINOR`, and `LWBGT_VERSION_PATCH`
  identify the project release.
- `LWBGT_FFI_ABI_VERSION` identifies the versioned structure and batch API.
- The `calc_wbgt` and `esat` scalar symbols retain the original compatibility
  ABI.
- The `lwbgt_input_v1`, `lwbgt_output_v1`, and `lwbgt_calc_batch_v1` names are
  permanent. Incompatible layouts or behavior require new `v2` names while the
  v1 entry point remains available.

New symbols and backward-compatible documentation clarifications may be added
without changing the v1 ABI. Fields must not be reordered, resized, removed, or
repurposed.

## Data model and layout

The v1 ABI requires 8-bit bytes, 32-bit `int32_t` and `float`, 64-bit `double`,
and the field offsets below. Supported release builds enforce the total sizes
and boundary offsets with compile-time assertions.

### `lwbgt_input_v1`

Total size: 104 bytes. Integer fields occupy the first 32 bytes; every floating
point input is an ABI-boundary `double`.

| Offset | Field | Type | Units and meaning |
|---:|---|---|---|
| 0 | `year` | `int32_t` | Four-digit Gregorian year |
| 4 | `month` | `int32_t` | Month 1–12; 0 means `day` is day-of-year |
| 8 | `day` | `int32_t` | Day of month, or day-of-year when `month == 0` |
| 12 | `hour` | `int32_t` | Local standard-time hour, 0–23 |
| 16 | `minute` | `int32_t` | Minutes past the hour |
| 20 | `gmt_offset_hours` | `int32_t` | Local standard time minus GMT, in hours |
| 24 | `averaging_minutes` | `int32_t` | Input averaging interval in minutes |
| 28 | `urban` | `int32_t` | 0 selects rural; 1 selects urban wind scaling |
| 32 | `latitude_deg_north` | `double` | Degrees north; south is negative |
| 40 | `longitude_deg_east` | `double` | Degrees east; west is negative |
| 48 | `solar_w_m2` | `double` | Solar irradiance, W/m² |
| 56 | `pressure_hpa` | `double` | Barometric pressure, hPa (equivalent to mb) |
| 64 | `air_temperature_c` | `double` | Dry-bulb air temperature, °C |
| 72 | `relative_humidity_percent` | `double` | Relative humidity, percent |
| 80 | `wind_speed_m_s` | `double` | Wind speed, m/s |
| 88 | `wind_height_m` | `double` | Wind measurement height, m |
| 96 | `vertical_temperature_difference_c` | `double` | Upper-minus-lower temperature difference, °C |

### `lwbgt_output_v1`

Total size: 24 bytes.

| Offset | Field | Type | Meaning |
|---:|---|---|---|
| 0 | `status` | `int32_t` | Per-record scalar solver status |
| 4 | `estimated_wind_speed_m_s` | `float` | Effective wind speed at 2 m, m/s |
| 8 | `globe_temperature_c` | `float` | Globe temperature, °C |
| 12 | `natural_wet_bulb_c` | `float` | Natural wet-bulb temperature, °C |
| 16 | `psychrometric_wet_bulb_c` | `float` | Psychrometric wet-bulb temperature, °C |
| 20 | `wbgt_c` | `float` | Outdoor wet-bulb globe temperature, °C |

## Batch call contract

```c
int lwbgt_calc_batch_v1(
    const lwbgt_input_v1 *inputs,
    lwbgt_output_v1 *outputs,
    size_t count
);
```

- `count == 0` returns `LWBGT_BATCH_OK`; either pointer may be null.
- For nonzero `count`, a null pointer returns
  `LWBGT_BATCH_INVALID_ARGUMENT` without modifying outputs.
- The caller owns both arrays and must provide at least `count` elements. The
  input and output storage must not overlap.
- Records execute serially, in ascending array order, by calling the scalar
  implementation once per record.
- The function return value reports call validity. Each output `status` reports
  that record's scalar solver result: 0 for success and -1 for failure to
  converge. A failed record uses the upstream `-9999` result convention.
- Inputs are forwarded without domain validation, clamping, unit conversion, or
  missing-value policy beyond behavior already present in the scalar model.
- When wind is already measured at 2 m, the batch API returns the supplied wind
  as `estimated_wind_speed_m_s`. This makes the batch result deterministic; the
  legacy scalar function instead leaves that output pointer untouched when no
  estimation is performed.

## Scalar ABI

The declarations in `lwbgt.h` are authoritative. Scalar floating-point inputs
to `calc_wbgt` use `double` at the ABI boundary because the original K&R
`float` parameters undergo default argument promotion. Output pointers remain
`float *`.

`esat` accepts temperature in kelvin. `phase == 0` computes saturation over
liquid water; `phase == 1` computes saturation over ice. Other phase values are
outside the supported contract.

## Concurrency and ownership

The implementation has no mutable shared calculation state. Independent scalar
or batch calls are thread-safe when callers use separate output buffers. A
single batch call is serial and does not create threads. The API retains no
input or output pointers after return and performs no allocation.

## Symbols and platforms

The shared library exports only:

```text
calc_wbgt
esat
lwbgt_calc_batch_v1
```

The release CI validates Linux with GCC, macOS with AppleClang, and Windows with
MinGW GCC. MSVC is unsupported because it cannot compile the preserved GNU89
numerical source. The public header is valid C and C++ and is tested through
installed C and C++ consumers.

## Official Python binding

The `lwbgt` Python distribution loads its bundled unversioned runtime through
`importlib.resources` and `ctypes`. Its public `Input` and `Result` records map
field-for-field to the v1 structures above. `calculate` and `calculate_batch`
both use `lwbgt_calc_batch_v1`; the latter submits the entire iterable in one
native call. `esat` directly exposes the scalar symbol. The binding performs no
unit conversion, domain validation, clamping, missing-data handling, or solver
failure substitution.
