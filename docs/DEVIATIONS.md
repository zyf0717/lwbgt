# Deviations from the original Liljegren C source

The reference is Liljegren WBGT v1.1 at upstream commit
[`cd672a8`](https://github.com/mdljts/wbgt/blob/cd672a886880b67f3f27bdbf75038d8f7ff0bac2/src/wbgt.c.original),
retained verbatim as `upstream/wbgt.c.original`. The modified kernel is
`src/wbgt.c`; the R package compiles a byte-identical copy at `r/src/wbgt.c`.
The source keeps the original copyright, license, acknowledgement, and a
notice identifying the derivative work. For the complete source diff, run
`git diff --no-index -- upstream/wbgt.c.original src/wbgt.c`.

## Changes and impact

- **Modern C declarations.** Typed prototypes replace K&R definitions and
  implicit declarations. The scalar ABI still accepts `double` arguments and
  converts them to `float` at function entry, matching the original calling
  convention and rounding.
- **Defined failure outputs.** Solar-position errors now return `-1` with all
  five scalar outputs set to `-9999`, rather than consuming unwritten values.
  Valid solar calculations retain their original path.
- **Defined 2 m wind output.** A direct scalar call now writes the supplied wind
  speed, rounded to `float`, when no height adjustment is needed. The original
  left this output unwritten. This is the intentional compatibility exception;
  the temperature and WBGT outputs are unchanged.
- **Shared calculation state.** Each row prepares vapor pressure, dew point,
  atmospheric emissivity, and the common long-wave term once. The globe and
  wet-bulb solvers reuse them. Each wet-bulb iteration also reuses its rounded
  viscosity and density for convection and mass transfer. The original
  equations, intermediate precision, convergence rule, and WBGT weights remain
  unchanged. Internal helpers whose only role was recomputing these values
  were removed.
- **Less repeated radiation work.** The psychrometric solve skips unused
  radiation calculations. Solar terms are calculated before the globe and
  natural wet-bulb iterations. The retained-oracle comparison checks that
  these changes preserve output bits on the sampled cases.
- **Isolated demonstration program.** Library builds omit the demonstration
  `main` and its I/O dependencies. The demo initializes its first, unused
  temperature difference, removing an uninitialized read. Comment repairs in
  `esat` do not change the formula.

The public C header preserves `calc_wbgt` and `esat` and adds the versioned
batch ABI. Python, R, and SwiftPM use the same C kernel; the batch entry point
calls the scalar calculation for each row. Packaging and input-policy additions
are described in the [ABI contract](ABI.md) and [input assumptions](INPUTS.md).

## Numerical checks

The 852-case retained-oracle comparison includes every supported year,
thermophysical and wind boundaries, radiation branches, and near-`float`
conversion inputs. On the matched GCC build, `Tg`, `Tnwb`, `Tpsy`, WBGT, and
`esat` match bit for bit; estimated wind matches except for the corrected
scalar 2 m output. The same corpus also matches the v1.0.0 kernel exactly.
Batch tests check scalar equivalence and deterministic failure outputs for
unsupported years and out-of-range solar coordinates. These sampled checks
are not a proof for every input or compiler.

No model constants, solar-position year range, wind-stability table, or
convergence threshold were changed. The retained source, its lineage, and the
license boundary are documented in [Upstream provenance](UPSTREAM.md) and
[Licensing](../LICENSING.md).
