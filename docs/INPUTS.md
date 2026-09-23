# Input sourcing and fallback assumptions

`lwbgt` does not supply defaults. Callers must record any fallback as part of
their application policy.

| Input | Recommendation when unavailable |
|---|---|
| Date, time, GMT offset, latitude, longitude | No fallback; derive them from the observation and site metadata. |
| `averaging_minutes` | Use the source observation interval; use `0` only for instantaneous or already centered observations. |
| `solar_w_m2` | Use `0` only when the time and location confirm nighttime; there is no general daytime fallback. |
| `pressure_hpa` | Prefer an elevation-derived station-pressure estimate. Use `1013.25` only as an explicit sea-level screening assumption. |
| `air_temperature_c`, `relative_humidity_percent`, `wind_speed_m_s` | No general fallback; these directly control the result. Humidity may instead be derived from suitable source observations such as dew point. |
| `wind_height_m` | Use instrument metadata. Use `10` only when the source specifies a 10 m wind measurement. |
| `vertical_temperature_difference_c` | Use `1` to assume a nighttime inversion. Only `< 0` versus `>= 0` matters. It can affect results only for rural nighttime records when wind height differs from 2 m and wind speed is below 2.5 m/s. |
| `urban` | For wind measured above 2 m, `1` is the conservative daytime fallback. At night, no single value is always conservative; evaluate both and retain the higher WBGT. The input is ignored at 2 m. |

Examples demonstrate complete inputs; their values are not universal defaults.
