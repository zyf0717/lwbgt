# Compatibility and performance

The shared library exports only `calc_wbgt`, `esat`, and
`lwbgt_calc_batch_v1`. Independent calls with separate buffers are thread-safe;
a batch call is serial. With matched compiler and floating-point settings, the
854-case retained-oracle comparison found identical 32-bit values for `Tg`,
`Tnwb`, `Tpsy`, WBGT, and `esat`. Estimated wind also matched except in direct
scalar calls with wind measured at 2 m: the original left that output unwritten,
while the derivative writes the supplied speed converted to `float`. The batch
and R callers already initialized their 2 m estimated-wind output.

The comparison covers every supported year and targeted numerical branches,
including 400 new successful cases. It does not cover every valid input or
every compiler and platform. The original solar-position year guard and date
arithmetic remain in place, including their historical behavior.

The current [expanded benchmark](https://github.com/zyf0717/lwbgt/blob/main/benchmarks/README.md)
uses the 854-case oracle input but times 842 rows, excluding the six `invalid`
and six `solver-boundary` cases. On GCC 13.3.0, the derivative measured 1.336×
overall median speedup; the slowest cohort, NASA POWER, measured 1.259×. All
gates passed. The [complete report](https://github.com/zyf0717/lwbgt/blob/main/benchmarks/expanded-gcc-13.3.0.json)
contains the per-cohort results.

The measurements below describe earlier releases, before the scalar output
correction, using the historical 454-case input (442 timed rows).

| Environment | Exact result | Median overall speedup |
|---|---:|---:|
| Linux x86-64, GCC 13.3.0 | bit-identical | 1.316× |
| Linux x86-64 container, GCC 16.2.0 | bit-identical | 1.289× |
| Linux x86-64, GCC 13.3.0, PIC build | bit-identical | 1.249× |

These measurements apply only to the documented environments and workloads.
Dates outside the original 1950–2049 solar-position range are rejected.

Full methods, hardware and compiler details, workloads, and retained results
are in the
[benchmark documentation](https://github.com/zyf0717/lwbgt/tree/main/benchmarks).
The public compatibility scope, layouts, and API guarantees are defined by the
[ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md).
