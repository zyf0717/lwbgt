# Deviations from the original Liljegren C source

The reference is Liljegren WBGT v1.1 at upstream commit
[`cd672a8`](https://github.com/mdljts/wbgt/blob/cd672a886880b67f3f27bdbf75038d8f7ff0bac2/src/wbgt.c.original),
retained verbatim as [`upstream/wbgt.c.original`](https://github.com/zyf0717/lwbgt/blob/main/upstream/wbgt.c.original).
The derivative is [`src/wbgt.c`](https://github.com/zyf0717/lwbgt/blob/main/src/wbgt.c);
`r/src/wbgt.c` is required to be byte-identical to it. Upstream locations below
refer to the retained original. This register groups repeated declaration-only
changes, but accounts for every substantive diff hunk. To inspect the complete
line diff from the repository root, run:

```sh
git diff --no-index -- upstream/wbgt.c.original src/wbgt.c
```

## Changes within the derivative

| Upstream location | Deviation and reason | Output or API effect |
|---|---|---|
| File header, after line 46 | Added a derivative-work notice identifying the modifier and retaining the upstream terms. | Attribution only. |
| Demonstration `main`, lines 60–122 | Scoped `stdio.h`, `stdlib.h`, and the entire demonstration behind `LWBGT_BUILD_DEMO`; changed `main()` to `main(void)`, removed its implicit function/`exit` declarations, and removed the redundant early `TRUE`/`FALSE` definitions. Library builds therefore contain no demo entry point or stdio dependency. | No library calculation change. The demo remains opt-in. |
| Demonstration `main`, lines 99–109 | Initialized `dT` to zero before the first call, which uses wind measured at the 2 m reference height. The later 10 m call still uses `dT10_2`. | Removes an uninitialized C read. The first call never uses `dT` for wind scaling, so its intended WBGT is unchanged. |
| `calc_wbgt`, lines 201–246; `esat`, line 522; all other K&R function definitions through `stab_srdt`, line 1089 | Replaced K&R definitions and implicit function declarations with typed prototypes; retained `math.h` and removed obsolete handwritten math prototypes. At the scalar ABI boundary, `double` parameters are explicitly converted to local `float`, preserving the original default-promotion behavior. Removed obsolete local function declarations throughout. | Binary scalar signatures remain compatible. No intended valid-domain numerical change from declaration syntax. |
| `calc_wbgt`, line 251; `calc_solar_parameters`, line 313 | Check and propagate `solarposition()` failure through both callers. Set all five scalar outputs to `-9999` and return `-1` before consuming unwritten solar outputs. | Rejected solar inputs now fail deterministically. Successful solar calculations retain their numerical path. |
| `calc_wbgt`, lines 255–263 | Write the supplied, float-converted wind to `*est_speed` after successful solar calculation, before any height adjustment. | **Intentional compatibility exception:** direct scalar calls at 2 m now write that output instead of leaving the caller's previous value. WBGT and temperature outputs are unchanged; the batch and R callers already supplied that value. |
| `Twb`, lines 353–415 | Skip the radiative terms when `rad == 0`, where the original later multiplied them by zero. Compute atmospheric and solar terms once before the iteration when `rad != 0`. | Removes dead and repeated work; retained-oracle tests check the other output bits. |
| `h_cylinder_in_air`, lines 415–448; `h_sphere_in_air`, lines 494–522 | Reuse the `float` viscosity value already calculated for Reynolds number when calculating conductivity; mark the unused cylinder `length` argument explicitly unused. | Removes a repeated viscosity call. The conductivity expression uses the same rounded viscosity; retained-oracle tests check output bits. |
| `Tglobe`, lines 448–494 | Compute loop-invariant atmospheric and solar radiation terms before the iteration, then reuse them. | Removes repeated work; retained-oracle tests check output bits. |
| `esat`, lines 533–542 | Repaired malformed nested-comment text in three commented-out alternative moist-air corrections. | Comment-only; the executable saturation formula is unchanged. |
| `solarposition`, lines 736–845 | Removed obsolete local math/function declarations along with the K&R signature. Added `days_before_year()` and support for Gregorian years 1900–2100. Years 1950–2049 still execute the original date arithmetic; newly admitted years use Gregorian leap-century day counts. The internal `year == 0`/`days_1900` route is unchanged. | Previously rejected years 1900–1949 and 2050–2100 now produce results. Existing successful years retain their solar arithmetic. The original low-precision formulas state precision only for 1950–2050; accuracy outside that period is unverified. |

No model constants, convergence threshold, minimum wind speed, WBGT weighting,
or wind-stability lookup table were changed. The compatibility gate compares
all existing output bits with the retained oracle except the corrected direct
scalar 2 m wind output. The historical exact-comparison mode remains available.

## Project additions outside the original file

| Addition | Purpose and relationship to the original |
|---|---|
| `include/lwbgt.h` | Declares the preserved scalar binary signatures and the versioned input/output structures and batch entry point. The original file had no installed public header. |
| `src/lwbgt_ffi.c` | Calls the same scalar calculation for each batch record; it already initialized 2 m estimated wind before the scalar correction. It adds no alternate numerical model. |
| CMake, SwiftPM, Python, and R packages | Build and expose the native source. Python uses the batch ABI; R compiles a synchronized copy of the derivative and validates input rows before calling the scalar function. These interfaces, validation policies, and packaging were absent from the original single-file C program. |

The source lineage and licensing boundary are recorded in
[Upstream provenance](https://github.com/zyf0717/lwbgt/blob/main/docs/UPSTREAM.md)
and [Licensing](https://github.com/zyf0717/lwbgt/blob/main/LICENSING.md).
