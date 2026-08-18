# HeatStressBench compatibility proof

- Checkout: `/home/yifei/repos/HeatStressBench`
- Commit: `59224f7b2e8f49d8ffd6cf97ae8cf7cdb927630b`
- Adapter sources were not modified.
- Compile flags matched the frozen target recipe.
- Each adapter object was linked once with the unmodified reference archive and
  once with `liblwbgt.a`; the archive was the only changed link input.

Unchanged adapter source SHA-256 values:

| Source | SHA-256 |
|---|---|
| `adapter.c` | `c25d704110eceeb1c4f75681c9fa7a2f856e1cd329f945e67c8a7ca108643326` |
| `adapter-realistic.c` | `7e9b49976125941366ff20e4aae1cc9e9f359a712c4afec2066e112ddbdecaa3` |
| `decomposition-adapter.c` | `85d24742f002d664b7214c2838e09d38e9345451840d3271c9b6fc8e66c3006b` |

Result CSVs were byte-identical between reference and derivative:

| Path | Result SHA-256 |
|---|---|
| Generated sample | `727907d0e105422251b65bd9e7ef5caf29589d28b5a9925753ad84993e5d2eee` |
| Decomposition sample | `0b75461093e03437110054ae55509f9550afc096a39a8e010ee632927abf11c6` |
| NASA POWER representative sample | `a0e6f80ad4216a10e5f6b79a7d146b4003f8f8f39e8d2efb746125bb47c3a397` |
| ERA5 representative sample | `fa1e09f4160d00e2bc9863632fa3e4074e193882637b9f7e83bba173b3ce2967` |

The three existing C adapter sources compile and link unchanged. The existing
shell scripts and CSV schemas were not changed. A separate HeatStressBench
`lwbgt` target and container manifest were intentionally not added because the
mandatory performance gate failed; the frozen canonical `liljegren-c` target
remains untouched.
