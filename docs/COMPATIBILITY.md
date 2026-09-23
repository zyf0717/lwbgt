# Compatibility and performance

The shared library exports only `calc_wbgt`, `esat`, and
`lwbgt_calc_batch_v1`. Independent calls with separate buffers are thread-safe;
a batch call is serial. For matched compilers and floating-point flags, the
current compatibility gate requires exact 32-bit equality with the retained
oracle for existing 1950–2049 results except the corrected direct scalar
`estimated_wind_speed_m_s` output when wind is measured at 2 m. The corrected
field must equal the supplied speed converted to `float`. Batch and R callers
already initialized that field and retain their previous output bits.

The measurements below describe the earlier releases, before that scalar
output correction and the 1900–2100 year extension.

| Environment | Exact result | Median overall speedup |
|---|---:|---:|
| Linux x86-64, GCC 13.3.0 | bit-identical | 1.316× |
| Linux x86-64 container, GCC 16.2.0 | bit-identical | 1.289× |
| Linux x86-64, GCC 13.3.0, PIC build | bit-identical | 1.249× |

These measurements apply only to the documented environments and workloads.
The legacy solar formulas are used outside 1950–2049 with Gregorian day
counting; their accuracy outside the stated 1950–2050 precision period has not
been established. Newly admitted dates have no legacy valid-output comparison.
Full methods, hardware and compiler details, workloads, and retained results
are in the
[benchmark documentation](https://github.com/zyf0717/lwbgt/tree/main/benchmarks).
The exact compatibility scope, layouts, and API guarantees are defined by the
[ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md).
