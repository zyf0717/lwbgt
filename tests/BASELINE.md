# Numerical baseline

## Historical 852-case comparison

- Upstream oracle blob: `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`
- Deterministic cases: 852, including 400 added successful cases
- Supported years covered: every year from 1950 through 2049
- Oracle non-convergence statuses: 11
- Oracle probe SHA-256: `add31b1029c7bdb6b002c5ec3190a244cff26e22518a982af5e223e568f6785d`
- Candidate probe SHA-256: `ad85d97ef4f301fefc40522f4e92a1a0bd215c05afc49ae7cded3632d59fc129`
- Compiler: GCC 13.3.0
- Floating-point flags: `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`

The 852-case compatibility comparison matches every output bit except the
corrected direct scalar 2 m estimated wind. The 400 new cases must all succeed
in the upstream oracle. This is sampled evidence, not a proof for all inputs.

Both hashes cover the return status, estimated wind speed, `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat` result for every case, with every float serialized as its exact
32-bit hexadecimal representation.

## v1.0.2 expanded comparison

The default suite adds 35,124 WBGT cases to the historical 852, for **35,976
WBGT oracle comparisons**. The historical generator and 840-row timing workload
remain unchanged. All extended status and output bits match the retained
original on Linux x86_64 with GCC 13.3.0 and Clang 18.1.3, except for the
existing scalar 2 m wind correction. Wind height is compared after binary32
conversion, including double inputs that round to exactly 2 m.

[expanded-baseline.json](expanded-baseline.json) records the input hashes,
compiler settings, output hashes, and convergence counts. Its extended WBGT
candidate hash is
`0ff8d055116430322ec8291778a23c7ff2ccfe1f3ec3b9c4954cfed7cc39da05`.
Both documented compiler builds produced the same recorded hashes; this does
not imply equality across every compiler, architecture, or math library.

| Additional cohort | Cases | Oracle non-convergence | Coverage |
|---|---:|---:|---|
| Wind thresholds | 2,736 | 0 | Adjacent binary32 values around 0.13, 2, 2.5, 3, 5, 6 m/s; day/night, radiation, height, urban/rural, inversion sign |
| Radiation thresholds | 150 | 0 | Neighbors of 175, 675, 925 W/m² before solar adjustment; multiple wind classes and urban/rural |
| Height and inversion sign | 128 | 0 | Adjacent 2 m floats and doubles rounding to 2 m; signed zero and subnormal temperature differences |
| Geometry | 9,360 | 0 | Exact poles/date line, polar circles, tropics, four seasons, day/night, averaging |
| Horizon minutes | 2,178 | 0 | Every minute in two-hour morning/evening windows, three longitudes, zero/nonzero radiation |
| Solar clipping | 300 | 0 | Near-zero irradiance, cap neighborhoods, sensor overshoot, latitude and time variation |
| Calendar/time | 6,912 | 0 | Every month's first/last day in eight boundary/leap years; month/day and ordinal forms; GMT offsets -12, 0, +14 h; averaging 0, 60, 180 min |
| Thermophysical extremes | 3,360 | 1,025 | Air -60 to 60 °C, pressure 200–1,100 hPa, RH 0.001–100%, wind 0–40 m/s, radiation 0–1,100 W/m² |
| Seeded nominal | 5,000 | 5 | Air -10 to 45 °C, pressure 700–1,100 hPa, RH 10–100%, wind 0–15 m/s, height 1–30 m, radiation 0–1,200 W/m² |
| Seeded stress | 5,000 | 2,035 | Air -80 to 65 °C, pressure 200–1,100 hPa, RH 0.001–100%, wind 0–40 m/s, height 0.1–100 m, radiation 0–2,000 W/m² |

Seeded cohorts use seeds **20261001** and **20261002** and independent uniform
sampling over the listed ranges. They also vary all supported years, Gregorian
dates, global coordinates, GMT offsets -12 to +14 h, averaging intervals
0/15/30/60/180/1440 min, inversion difference -5 to 5 °C, and urban/rural.
Dates whose centered fractional day would be negative are advanced one day
before oracle evaluation. Solar-invalid inputs must not be compared to the
original, which consumes unwritten solar outputs on rejection. Historical date
arithmetic is preserved; paired calendar forms are not assumed equivalent.
These synthetic inputs are not observed weather, and radiation is sampled
independently of solar geometry.

The seven targeted boundary/geometry/calendar cohorts must all converge.
Extreme and seeded cohorts retain non-convergence as part of the comparison;
statuses and every output bit still have to match, and each cohort must contain
successful solves. The expanded corpus has 3,065 non-convergences. Five occur
within the nominal weather ranges, illustrating that those ranges alone do
not guarantee solver convergence.

Additional checks:

- **996 internal diagnostics** compare stability-table classes at adjacent
  wind/radiation floats and locate adjacent longitude floats straddling cosine
  thresholds 0 and `CZA_MIN` using each linked kernel. They also compare
  adjusted radiation and direct-beam outputs around the irradiance cap.
  Internal helper calls respect the original K&R argument promotions.
- **1,682 saturation-pressure cases** cover both water and ice, 173.15–373.15 K
  in 0.25 K steps, adjacent binary32 values and rounding midpoints at seven
  temperature anchors, signed zero, NaN, and infinities. Inputs outside the
  physical range test inherited function behavior, not physical accuracy.
- **64 invalid/non-finite weather rows** check current scalar/batch and Python
  consistency. They are excluded from upstream equivalence: NaN solar can fail
  the original psychrometric solver while the derivative returns finite `Tpsy`
  after skipping unused radiation calculations.
- **18 rejected solar cases** require status -1 and all five outputs -9999
  through current scalar and batch calls. They cover year bounds including
  integer extremes, invalid calendar fields, and out-of-range coordinates.

Native and Python-runtime probes compare against independently compiled
retained-source probes. The installed Python wrapper checks the entire expanded
WBGT and invalid-weather corpora against direct native batch calls. The C batch
harness processes arbitrarily large input files in chunks of at most 1,024 rows
and compares every field with scalar calls.

Reproduce the default suites with:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

Run a larger seeded comparison without changing the benchmark:

```sh
python3 tests/generate_extended_cases.py build/extended-large.csv --samples 100000
python3 tests/compare.py compat build/lwbgt_reference_probe build/lwbgt_probe \
  build/extended-large.csv
```

The default CTest suite took approximately three seconds on the local Linux
machine, so the 10,000 seeded cases run in normal CI. Sample counts and seeds
are configurable for additional investigations; preserve any new failure as a
permanent regression. Compatibility sampling does not establish scientific
accuracy against independent observations or prove equivalence for all inputs.
