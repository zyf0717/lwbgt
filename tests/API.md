# Exported-symbol and API review

The v0.1.0 static archive was reviewed with:

```sh
nm -g --defined-only build/liblwbgt.a
```

The only supported public symbols are:

```text
calc_wbgt
esat
```

Their declarations in `include/lwbgt.h` are the permanent compatibility ABI.
The scalar `float` parameters in the original K&R definitions are correctly
declared as `double` at the ABI boundary because of default argument promotion;
output pointers remain `float *`.

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

They remain link-visible because v0.1.0 preserves the source-derived structure;
they are not declared by the installed header and are not supported API.
