# Optimization 3 profile

## Conditions

- CPU affinity: CPU 4 for both executables
- Workload: `build/cases.csv`, 454 deterministic cases
- Iterations: 200 per case
- Execution: single-threaded
- Compiler: GCC 13.3.0
- Core flags: GNU89, `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`
- Harness flags: C11, `-O2 -fno-fast-math -ffp-contract=off`

The reference and Optimizations 1+2 candidate were built together from the
release CMake configuration. The measured commands were:

```sh
perf stat -r 7 taskset -c 4 build/lwbgt_reference_benchmark build/cases.csv 200
perf stat -r 7 taskset -c 4 build/lwbgt_benchmark build/cases.csv 200
perf record -g -- taskset -c 4 <benchmark> build/cases.csv 200
perf report
```

`perf stat` reported 1.123113246 ± 0.000281397 seconds for the reference and
0.969978353 ± 0.000337163 seconds for Optimizations 1+2. Hardware counters were
not available on this host. `perf record` could not open an event because
`kernel.perf_event_paranoid=4`, and noninteractive privileged access was not
available; consequently no `perf report` call graph could be produced.

To retain profile guidance without altering the release build, both sources
were rebuilt with identical `-pg` instrumentation and run under the same CPU,
workload, and iteration constraints. The supplemental flat profile was:

| Build | Function | Self time | Calls |
|---|---|---:|---:|
| Reference | `Twb` | 40.0% | 355,368 |
| Reference | `Tglobe` | 16.0% | 177,684 |
| Optimizations 1+2 | `Twb` | 26.3% | 355,368 |
| Optimizations 1+2 | `Tglobe` | 42.1% | 177,684 |

The call graph recorded 5,114,646 cylinder-convection evaluations inside
`Twb` and 4,023,618 sphere-convection evaluations inside `Tglobe`, demonstrating
that the iterative solves remained material hot paths. Source inspection showed
that atmospheric emissivity, fixed air/surface fourth-power radiation, solar
geometry, and `tan(sza)` were recomputed inside those loops despite being
invariant for a solve.

Optimization 3 hoists only those invariant radiative subexpressions. It retains
their original evaluation order in `double` intermediates and does not change
the equations, solver, precision, iteration state, or convergence logic.

## Validation

Both GCC 13.3.0 and GCC 16.2.0 produced the same 454-case probe SHA-256 as the
reference:

```text
087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff
```

The hash covers status, estimated wind, Tg, Tnwb, Tpsy, WBGT, and `esat`, each
serialized by exact bit pattern. Final interleaved results are in
`optimization-3-gcc-13.3.0.json` and `optimization-3-gcc-16.2.0.json`.
