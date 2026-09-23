# Numerical baseline

## Current expanded oracle

- Upstream oracle blob: `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`
- Deterministic cases: 854, including 400 added successful cases
- Supported years covered: every year from 1950 through 2049
- Oracle non-convergence statuses: 11, all in the historical prefix
- Probe output SHA-256: `e831990f627767d223ba87548e35040b4cc60ff6d0d4b2df9e40e3b4faeae99c`
- Compiler: GCC 13.3.0
- Floating-point flags: `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`

The 854-case compatibility comparison matches every output bit except the
corrected direct scalar 2 m estimated wind. The 400 new cases must all succeed
in the upstream oracle. This is sampled evidence, not a proof for all inputs.

## Historical 454-case prefix

- Upstream oracle blob: `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`
- Deterministic cases: 454
- Oracle non-convergence statuses: 11
- Probe output SHA-256: `087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff`
- Compiler: GCC 13.3.0
- Floating-point flags: `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`

Both hashes cover the return status, estimated wind speed, `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat` result for every case, with every float serialized as its exact
32-bit hexadecimal representation.
