"""Compare prepared binaries with matching-toolchain oracle probes, then test Julia."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    products, archives, target = map(str, sys.argv[1:4])
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        candidates = list(Path(products).glob(f"lwbgt.v*.{target}.tar.gz"))
        if len(candidates) != 1:
            raise RuntimeError(f"expected one native archive for {target}: {candidates}")
        subprocess.run(["tar", "-xf", str(candidates[0].resolve()), "-C", str(work)], check=True)
        cases, esat, weather = [work / name for name in ("cases.csv", "esat.csv", "weather.csv")]
        subprocess.run([sys.executable, str(ROOT / "tests/generate_cases.py"), str(cases),
                        "--esat-output", str(esat), "--weather-output", str(weather)], check=True)
        suffix = ".exe" if os.name == "nt" else ""
        env = dict(os.environ)
        for name, inputs, mode in [("probe", cases, "compat"), ("esat_probe", esat, "exact")]:
            reference = work / "bin" / f"lwbgt_reference_{name}{suffix}"
            candidate = work / "bin" / f"lwbgt_{name}{suffix}"
            subprocess.run([sys.executable, str(ROOT / "tests/compare.py"), mode,
                            str(reference), str(candidate), str(inputs)], check=True)
            expected = work / f"{name}-expected.csv"
            with expected.open("wb") as output:
                subprocess.run([str(candidate), str(inputs)], stdout=output, check=True)
            prefix = "LWBGT" if name == "probe" else "LWBGT_ESAT"
            env[f"{prefix}_CASES"] = str(inputs)
            env[f"{prefix}_EXPECTED"] = str(expected)
        env["LWBGT_WEATHER_CASES"] = str(weather)
        subprocess.run([sys.executable, str(ROOT / "tests/check_julia_artifact.py"), archives],
                        env=env, check=True)


if __name__ == "__main__":
    main()
