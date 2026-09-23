# lwbgt

`lwbgt` provides dependency-free, vectorized R access to the
reference-compatible Liljegren outdoor wet bulb globe temperature kernel.
Input names and units match the native and Python APIs.

Install the latest release from R-universe:

```r
install.packages("lwbgt", repos = "https://zyf0717.r-universe.dev")
```

Or install the latest GitHub release directly from this repository's `r/`
subdirectory:

```r
install.packages("remotes", repos = "https://cloud.r-project.org")
remotes::install_github("zyf0717/lwbgt/r@*release")
```

```r
input <- lwbgt_input(
    year = 2024, month = 4, day = 15, hour = 14, minute = 30,
    gmt_offset_hours = 8, averaging_minutes = 60, urban = 1,
    latitude_deg_north = 1.3521, longitude_deg_east = 103.8198,
    solar_w_m2 = 742, pressure_hpa = 1008.4,
    air_temperature_c = 32.1, relative_humidity_percent = 68,
    wind_speed_m_s = 2.8, wind_height_m = 10,
    vertical_temperature_difference_c = 1
)
calculate(input)
esat(273.15)
```

Rows with missing, invalid, or non-convergent inputs return a nonzero status
and `NA` numerical outputs without preventing other rows from being calculated.

The package contains a modified Liljegren WBGT v1.1 derivative. See the
installed `LICENSE`, `LICENSES/`, and `NOTICE` files for redistribution terms
and required acknowledgements. It is not affiliated with or endorsed by the
original authors, UChicago Argonne, or the U.S. Department of Energy.
