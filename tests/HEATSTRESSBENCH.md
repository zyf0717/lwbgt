# Final HeatStressBench compatibility proof

- Checkout: `/home/yifei/repos/HeatStressBench`
- Commit: `59224f7b2e8f49d8ffd6cf97ae8cf7cdb927630b`
- lwbgt finalized clean-checkout commit: `1db2c56943ae793dfdac4520b84d05bfef6c64ae`
- Compiler: GCC 16.2.0
- Core flags: GNU89, `-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing`
- Adapter flags: C11, `-O2 -fno-fast-math -ffp-contract=off -Wall -Wextra -Werror`
- Adapter sources were not modified.
- Compile flags matched the frozen `liljegren-c` target recipe.
- Each adapter object was linked once with the unmodified reference archive and
  once with final `liblwbgt.a`; the archive was the only changed link input.

Unchanged adapter source SHA-256 values:

| Source | SHA-256 |
|---|---|
| `adapter.c` | `c25d704110eceeb1c4f75681c9fa7a2f856e1cd329f945e67c8a7ca108643326` |
| `adapter-realistic.c` | `7e9b49976125941366ff20e4aae1cc9e9f359a712c4afec2066e112ddbdecaa3` |
| `decomposition-adapter.c` | `85d24742f002d664b7214c2838e09d38e9345451840d3271c9b6fc8e66c3006b` |

All three adapter sources compiled unchanged. Result CSVs were byte-identical
between reference and final derivative:

| Adapter/path | Rows | Result SHA-256 |
|---|---:|---|
| `adapter.c`, generated | 47 | `0a438e15e5a2520fe2318651ab5d7ead7cb23710c325a5a8e809f34dc9d55c85` |
| `adapter.c`, decomposition | 8,217 | `c9e1417538941098c3cdb05f9ad979d1cb2f21d602ed8d9a717f14863214d790` |
| `decomposition-adapter.c`, components | 8,217 | `259e452d446995072cd26184e5489558a2a30d90285b3d78f8672dd2b2910d31` |
| `adapter-realistic.c`, NASA POWER | 256 | `cbeecd280e954bacd49ad727b26834c773aba1c8a342af8a629d149d08a6c5e0` |
| `adapter-realistic.c`, ERA5 | 256 | `b5a67503f1a3cf71ab39ff76c9adff5007fe9895691429cd3b6edb85a5cfc49c` |

The existing shell scripts, adapter sources, and CSV schemas were not changed.
The frozen canonical `liljegren-c` target remains the behavioural oracle and
was not replaced or relabelled.
