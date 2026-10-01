# Exported-symbol and API review

`docs/ABI.md` is the authoritative compatibility contract for public symbols,
layouts, units, ownership, and concurrency semantics.

The v0.1.0 static archive was reviewed with:

```sh
nm -g --defined-only build/liblwbgt.a
```

The v0.1.0 static compatibility symbols are:

```text
calc_wbgt
esat
```

Their declarations in `include/lwbgt.h` are the permanent compatibility ABI.
The scalar `float` parameters in the original K&R definitions are correctly
declared as `double` at the ABI boundary because of default argument promotion;
output pointers remain `float *`.

v0.2.0 adds the supported FFI symbol:

```text
lwbgt_calc_batch_v1
```

Its `lwbgt_input_v1` and `lwbgt_output_v1` structures have permanent 104-byte
and 24-byte layouts. The shared library's platform-specific export lists expose
only `calc_wbgt`, `esat`, and `lwbgt_calc_batch_v1`; `shared_exports` audits that
surface in CTest.

v0.3.0 adds a wheel-only, unversioned shared runtime built from the same object
libraries. `python_runtime_exports` audits the same three-symbol surface. The
current `python_runtime_compatibility_equivalence` test reruns the 852-case
comparison through an executable linked to that target. For those sampled
inputs, the compatibility comparison checks the bits of `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat` against the retained original. It also checks estimated wind,
except at 2 m, where it requires the supplied wind converted to `float`. These
tests do not prove bit identity for every valid input or build environment. The
historical byte-exact comparison mode remains available in `tests/compare.py`.

All 400 added rows must succeed in the upstream oracle; they cover every supported year,
calendar and solar geometry boundaries, wind stability thresholds, varied
thermophysical inputs, and scalar float conversion.

`demo_smoke` compiles and runs the optional demonstration with a valid row.
The batch test checks deterministic failure outputs for unsupported years and
out-of-range solar coordinates, which the original caller did not handle.

As of v0.4.0, the upstream demonstration program is compiled only when
`LWBGT_BUILD_DEMO` is defined and contributes no `main`, `printf`, or `exit`
dependency to library builds.

The archive also exposes these inherited implementation symbols:

```text
Tglobe
Twb
calc_solar_parameters
daynum
dew_point
diffusivity
est_wind_speed
evap
h_sphere_in_air
solarposition
stab_srdt
thermal_cond
viscosity
```

They remain link-visible because the static archive preserves the source-derived
structure; they are not declared by the installed header and are not supported
API.

As of v1.0.2, `native_extended_compatibility` and
`python_runtime_extended_compatibility` add 35,124 oracle comparisons.
`extended_batch_equivalence` streams those rows in batches of up to 1,024,
checking every output bit against scalar calls; the installed-wheel suite also
checks all extended rows. Water/ice `esat` probes exercise both library targets.
The static-library branch diagnostic checks internal stability thresholds and
adjacent solar-horizon/clipping inputs; it does not expand the supported API.

A separate 64-row invalid/non-finite weather corpus checks current scalar,
batch, and installed Python outputs. It is excluded from upstream equivalence:
unused radiation work can affect the original psychrometric solver on NaN
solar inputs. Rejected solar-input contract tests now cover 18 year, calendar,
and coordinate cases through both scalar and batch calls.
