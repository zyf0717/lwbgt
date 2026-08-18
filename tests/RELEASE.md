# v0.1.0 release verification

The numerical source was frozen after Optimization 3. No Optimization 4 is
included or permitted before v0.1.0.

On 2026-08-18, commit `0b5406ca34d1a5ec65ea697ceeee9ba767b86e4b`
was cloned locally with `git clone --no-hardlinks` into a separate clean
checkout. The checkout reported no tracked or untracked changes before the
release build.

The clean-checkout verification was:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --clean-first --parallel
ctest --test-dir build --output-on-failure
python3 tests/compare.py exact \
  build/lwbgt_reference_probe build/lwbgt_probe build/cases.csv
```

Both CTest tests passed. The explicit differential run reported 454
bit-identical cases with probe SHA-256:

```text
087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff
```

The hash covers status, estimated wind speed, Tg, Tnwb, Tpsy, WBGT, and `esat`
by exact bit pattern. Final frozen HeatStressBench adapter verification is
recorded in `HEATSTRESSBENCH.md`; the API/export audit is recorded in `API.md`.
