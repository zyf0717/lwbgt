# Numerical baseline

- Upstream oracle blob: `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`
- Deterministic cases: 454
- Oracle non-convergence statuses: 11
- Probe output SHA-256: `087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff`
- Compiler: GCC 13.3.0
- Floating-point flags: `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`

The hash covers the return status, estimated wind speed, `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat` result for every case, with every float serialized as its exact
32-bit hexadecimal representation.
