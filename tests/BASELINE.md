# Numerical baseline

- Upstream oracle blob: `7bc6e6ddd76a538d6454b27e9b252667846e6c9b`
- Deterministic cases: 852, including 400 added successful cases
- Supported years covered: every year from 1950 through 2049
- Oracle non-convergence statuses: 11
- Probe output SHA-256: `add31b1029c7bdb6b002c5ec3190a244cff26e22518a982af5e223e568f6785d`
- Compiler: GCC 13.3.0
- Floating-point flags: `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`

The 852-case compatibility comparison matches every output bit except the
corrected direct scalar 2 m estimated wind. The 400 new cases must all succeed
in the upstream oracle. This is sampled evidence, not a proof for all inputs.

Both hashes cover the return status, estimated wind speed, `Tg`, `Tnwb`, `Tpsy`,
WBGT, and `esat` result for every case, with every float serialized as its exact
32-bit hexadecimal representation.
