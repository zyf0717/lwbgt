#!/usr/bin/env python3
"""Compare main, default, and psychrometric opt-out through the public C ABI."""

from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import platform
import statistics
import struct
import time
from datetime import datetime, timezone
from pathlib import Path


class InputV1(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_int32)
        for name in "year month day hour minute gmt_offset_hours averaging_minutes urban".split()
    ] + [
        (name, ctypes.c_double)
        for name in (
            "latitude_deg_north longitude_deg_east solar_w_m2 pressure_hpa "
            "air_temperature_c relative_humidity_percent wind_speed_m_s "
            "wind_height_m vertical_temperature_difference_c"
        ).split()
    ]


class OutputV1(ctypes.Structure):
    _fields_ = [("status", ctypes.c_int32)] + [
        (name, ctypes.c_float)
        for name in (
            "estimated_wind_speed_m_s globe_temperature_c natural_wet_bulb_c "
            "psychrometric_wet_bulb_c wbgt_c"
        ).split()
    ]


assert ctypes.sizeof(InputV1) == 104
assert ctypes.sizeof(OutputV1) == 24
SKIP_PSYCHROMETRIC = 1
SKIPPED_BITS = struct.unpack("=I", struct.pack("=f", -9999.0))[0]


def load_inputs(path: Path) -> tuple[bytes, ctypes.Array]:
    """Read the existing test CSV, or native-endian packed v1 input records."""
    if path.suffix == ".csv":
        integers = "year month day hour minute gmt avg urban".split()
        numbers = "lat lon solar pressure air rh wind wind_height vertical_delta".split()
        with path.open(newline="", encoding="ascii") as stream:
            data = b"".join(
                struct.pack("=8i9d", *(int(row[n]) for n in integers),
                            *(float(row[n]) for n in numbers))
                for row in csv.DictReader(stream)
            )
    else:
        data = path.read_bytes()
    if not data or len(data) % ctypes.sizeof(InputV1):
        raise ValueError(f"{path}: expected nonempty 104-byte v1 records")
    count = len(data) // ctypes.sizeof(InputV1)
    return data, (InputV1 * count).from_buffer_copy(data)


def library(path: Path, extended: bool) -> ctypes.CDLL:
    lib = ctypes.CDLL(str(path.resolve()))
    signature = (ctypes.POINTER(InputV1), ctypes.POINTER(OutputV1), ctypes.c_size_t)
    lib.lwbgt_calc_batch_v1.argtypes = signature
    lib.lwbgt_calc_batch_v1.restype = ctypes.c_int
    if extended:
        lib.lwbgt_calc_batch_ex_v1.argtypes = (*signature, ctypes.c_uint32)
        lib.lwbgt_calc_batch_ex_v1.restype = ctypes.c_int
    return lib


def invoke(function, arguments) -> None:
    status = function(*arguments)
    if status != 0:
        raise RuntimeError(f"native batch rejected benchmark inputs: {status}")


def validate(reference, candidate, inputs, outputs) -> dict:
    count = len(inputs)
    invoke(reference.lwbgt_calc_batch_v1, (inputs, outputs, count))
    expected = bytes(outputs)
    invoke(candidate.lwbgt_calc_batch_v1, (inputs, outputs, count))
    if bytes(outputs) != expected:
        raise RuntimeError("default outputs differ from the main build")
    invoke(candidate.lwbgt_calc_batch_ex_v1, (inputs, outputs, count, 0))
    if bytes(outputs) != expected:
        raise RuntimeError("zero flags differ from the default entrypoint")
    invoke(candidate.lwbgt_calc_batch_ex_v1,
           (inputs, outputs, count, SKIP_PSYCHROMETRIC))
    skipped = bytes(outputs)
    for index, (full, reduced) in enumerate(zip(
        struct.iter_unpack("=6I", expected), struct.iter_unpack("=6I", skipped)
    )):
        if full[:4] != reduced[:4] or full[5] != reduced[5] or reduced[4] != SKIPPED_BITS:
            raise RuntimeError(f"opt-out changed a retained output at row {index}")
    statuses = [value[0] for value in struct.iter_unpack("=i20x", expected)]
    if any(status not in (0, -1) for status in statuses):
        raise RuntimeError("unexpected per-record status")
    return {
        "default_bit_identical": True,
        "opt_out_retained_outputs_bit_identical": True,
        "successes": statuses.count(0),
        "failures": statuses.count(-1),
    }


def measured(function, arguments, outputs, scale: int) -> dict:
    elapsed_ns = 0
    digest = hashlib.sha256()
    for _ in range(scale):
        started = time.perf_counter_ns()
        status = function(*arguments)
        elapsed_ns += time.perf_counter_ns() - started
        if status != 0:
            raise RuntimeError(f"native batch call failed: {status}")
        # Consume every output bit outside the timed C call.
        digest.update(memoryview(outputs).cast("B"))
    elapsed = elapsed_ns / 1e9
    if elapsed <= 0:
        raise RuntimeError("nonpositive elapsed time")
    return {"seconds": elapsed, "output_sha256": digest.hexdigest()}


def summarize(samples: list[dict], calls: int) -> dict:
    if len({sample["output_sha256"] for sample in samples}) != 1:
        raise RuntimeError("output bits changed between repetitions")
    seconds = [sample["seconds"] for sample in samples]
    median = statistics.median(seconds)
    return {
        "elapsed_seconds": seconds,
        "median_seconds": median,
        "rows_per_second": calls / median,
        "relative_mad": statistics.median(abs(value - median) for value in seconds) / median,
        "output_sha256": samples[0]["output_sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--input", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--scales", nargs="+", type=int, default=[1, 4])
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--compiler-flags", required=True)
    args = parser.parse_args()
    if args.repetitions < 3 or any(scale < 1 for scale in args.scales):
        parser.error("need at least three repetitions and positive scales")
    cpu = None
    if hasattr(os, "sched_getaffinity"):
        available = os.sched_getaffinity(0)
        cpu = min(available) if args.cpu is None else args.cpu
        if cpu not in available:
            parser.error(f"CPU {cpu} is outside the allowed affinity")
        os.sched_setaffinity(0, {cpu})
    elif args.cpu is not None:
        parser.error("CPU affinity is unavailable on this platform")
    reference = library(args.reference, extended=False)
    candidate = library(args.candidate, extended=True)
    report = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "cpu": cpu,
        "compiler": args.compiler, "compiler_flags": args.compiler_flags,
        "repetitions": args.repetitions,
        "method": "serial public C batch calls; pinned CPU where supported; "
                  "input conversion and output hashing excluded; full warm-up per mode; "
                  "rotating mode order; scales repeat the complete input batch",
        "libraries": {
            name: {"path": str(path.resolve()),
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for name, path in [("main", args.reference), ("candidate", args.candidate)]
        },
        "datasets": {},
    }
    for declaration in args.input:
        name, separator, filename = declaration.partition("=")
        if not separator or not name or name in report["datasets"]:
            parser.error("inputs must be distinct NAME=PATH declarations")
        path = Path(filename)
        data, inputs = load_inputs(path)
        count = len(inputs)
        outputs = (OutputV1 * count)()
        dataset = {"path": str(path.resolve()), "rows": count,
                   "input_sha256": hashlib.sha256(data).hexdigest(),
                   "validation": validate(reference, candidate, inputs, outputs), "scales": {}}
        del data
        modes = {
            "main": (reference.lwbgt_calc_batch_v1, (inputs, outputs, count)),
            "default": (candidate.lwbgt_calc_batch_v1, (inputs, outputs, count)),
            "skip": (candidate.lwbgt_calc_batch_ex_v1,
                     (inputs, outputs, count, SKIP_PSYCHROMETRIC)),
        }
        for function, arguments in modes.values():
            invoke(function, arguments)
        print(f"{name}: {count} rows validated bit-for-bit", flush=True)
        for scale in args.scales:
            samples = {mode: [] for mode in modes}
            names = list(modes)
            for repetition in range(args.repetitions):
                rotation = repetition % len(names)
                order = names[rotation:] + names[:rotation]
                if (repetition // len(names)) % 2:
                    order.reverse()
                for mode in order:
                    function, arguments = modes[mode]
                    sample = measured(function, arguments, outputs, scale)
                    samples[mode].append(sample)
                    print(f"{name} {scale}x {mode} {repetition + 1}/{args.repetitions}: "
                          f"{sample['seconds']:.6f} s", flush=True)
            summary = {mode: summarize(values, count * scale) for mode, values in samples.items()}
            if summary["main"]["output_sha256"] != summary["default"]["output_sha256"]:
                raise RuntimeError("default benchmark outputs differ from main")
            summary["calls"] = count * scale
            summary["default_speedup"] = summary["main"]["median_seconds"] / summary["default"]["median_seconds"]
            summary["skip_speedup"] = summary["main"]["median_seconds"] / summary["skip"]["median_seconds"]
            summary["skip_vs_default"] = summary["default"]["median_seconds"] / summary["skip"]["median_seconds"]
            dataset["scales"][str(scale)] = summary
        report["datasets"][name] = dataset
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
