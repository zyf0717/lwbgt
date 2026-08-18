# Exported-symbol and API review

`ABI.md` is the authoritative compatibility contract for public symbols,
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

The archive also exposes these inherited implementation symbols:

```text
Tglobe
Twb
calc_solar_parameters
daynum
dew_point
diffusivity
emis_atm
est_wind_speed
evap
h_cylinder_in_air
h_sphere_in_air
lwbgt_original_demo_main
solarposition
stab_srdt
thermal_cond
viscosity
```

They remain link-visible because the static archive preserves the source-derived
structure; they are not declared by the installed header and are not supported
API.
