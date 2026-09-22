# Compatibility and performance

The shared library exports only `calc_wbgt`, `esat`, and
`lwbgt_calc_batch_v1`. Independent calls with separate buffers are thread-safe;
a batch call is serial. The acceptance policy requires exact 32-bit output
equality for matched compilers and floating-point flags.

| Environment | Exact result | Median overall speedup |
|---|---:|---:|
| Linux x86-64, GCC 13.3.0 | bit-identical | 1.316× |
| Linux x86-64 container, GCC 16.2.0 | bit-identical | 1.289× |
| Linux x86-64, GCC 13.3.0, PIC build | bit-identical | 1.249× |

These measurements apply only to the documented environments and workloads.
Full methods, hardware and compiler details, workloads, and retained results
are in the
[benchmark documentation](https://github.com/zyf0717/lwbgt/tree/main/benchmarks).
The exact compatibility scope, layouts, and API guarantees are defined by the
[ABI contract](https://github.com/zyf0717/lwbgt/blob/main/docs/ABI.md).
