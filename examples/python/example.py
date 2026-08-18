#!/usr/bin/env python3
"""Minimal dependency-free lwbgt batch binding using ctypes."""

from __future__ import annotations

import ctypes
import math
import sys


class InputV1(ctypes.Structure):
    _fields_ = [
        ("year", ctypes.c_int32),
        ("month", ctypes.c_int32),
        ("day", ctypes.c_int32),
        ("hour", ctypes.c_int32),
        ("minute", ctypes.c_int32),
        ("gmt_offset_hours", ctypes.c_int32),
        ("averaging_minutes", ctypes.c_int32),
        ("urban", ctypes.c_int32),
        ("latitude_deg_north", ctypes.c_double),
        ("longitude_deg_east", ctypes.c_double),
        ("solar_w_m2", ctypes.c_double),
        ("pressure_hpa", ctypes.c_double),
        ("air_temperature_c", ctypes.c_double),
        ("relative_humidity_percent", ctypes.c_double),
        ("wind_speed_m_s", ctypes.c_double),
        ("wind_height_m", ctypes.c_double),
        ("vertical_temperature_difference_c", ctypes.c_double),
    ]


class OutputV1(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int32),
        ("estimated_wind_speed_m_s", ctypes.c_float),
        ("globe_temperature_c", ctypes.c_float),
        ("natural_wet_bulb_c", ctypes.c_float),
        ("psychrometric_wet_bulb_c", ctypes.c_float),
        ("wbgt_c", ctypes.c_float),
    ]


def fixtures() -> list[InputV1]:
    return [
        InputV1(2024, 3, 21, 7, 0, 0, 0, 0,
                14.515380, -91.977540, 0.0, 1010.0, 42.543334, 31.5,
                0.821752, 2.0, 0.0),
        InputV1(2024, 4, 15, 14, 30, 8, 60, 1,
                1.3521, 103.8198, 742.0, 1008.4, 32.1, 68.0,
                2.8, 10.0, -0.4),
    ]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: example.py SHARED_LIBRARY")
    if ctypes.sizeof(InputV1) != 104 or ctypes.sizeof(OutputV1) != 24:
        raise SystemExit("unexpected ctypes structure layout")

    library = ctypes.CDLL(sys.argv[1])
    library.lwbgt_calc_batch_v1.argtypes = (
        ctypes.POINTER(InputV1), ctypes.POINTER(OutputV1), ctypes.c_size_t
    )
    library.lwbgt_calc_batch_v1.restype = ctypes.c_int
    library.esat.argtypes = (ctypes.c_double, ctypes.c_int)
    library.esat.restype = ctypes.c_float

    records = fixtures()
    inputs = (InputV1 * len(records))(*records)
    outputs = (OutputV1 * len(records))()
    if library.lwbgt_calc_batch_v1(inputs, outputs, len(records)) != 0:
        raise SystemExit("batch call failed")
    if any(output.status != 0 or not math.isfinite(output.wbgt_c) for output in outputs):
        raise SystemExit("calculation failed")
    if outputs[0].estimated_wind_speed_m_s != ctypes.c_float(records[0].wind_speed_m_s).value:
        raise SystemExit("2 m wind result is not deterministic")
    if not math.isfinite(library.esat(records[0].air_temperature_c + 273.15, 0)):
        raise SystemExit("esat failed")
    print("python binding example: ok")


if __name__ == "__main__":
    main()
