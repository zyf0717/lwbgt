from __future__ import annotations

import csv
import ctypes
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import lwbgt
from _fixtures import NIGHT, SINGAPORE, SOLVER_FAILURE
from lwbgt import _ffi


def packed(result: lwbgt.Result) -> bytes:
    return struct.pack(
        "=i5f",
        result.status,
        result.estimated_wind_speed_m_s,
        result.globe_temperature_c,
        result.natural_wet_bulb_c,
        result.psychrometric_wet_bulb_c,
        result.wbgt_c,
    )


class BatchTests(unittest.TestCase):
    def test_empty_batch(self) -> None:
        self.assertEqual(lwbgt.calculate_batch([]), [])

    def test_one_record_batch_matches_scalar(self) -> None:
        self.assertEqual(
            lwbgt.calculate_batch([SINGAPORE]), [lwbgt.calculate(SINGAPORE)]
        )

    def test_multiple_records_preserve_order_and_caller_objects(self) -> None:
        records = [NIGHT, SINGAPORE, SOLVER_FAILURE]
        before = records.copy()
        results = lwbgt.calculate_batch(records)
        self.assertEqual(records, before)
        self.assertEqual([result.status for result in results], [0, 0, -1])
        self.assertEqual(results, [lwbgt.calculate(record) for record in records])

    def test_batch_matches_direct_native_batch_exactly(self) -> None:
        records = [SINGAPORE, NIGHT, SOLVER_FAILURE]
        count = len(records)
        inputs = (_ffi._InputV1 * count)(*map(_ffi._as_native, records))
        outputs = (_ffi._OutputV1 * count)()
        status = _ffi._library().lwbgt_calc_batch_v1(inputs, outputs, count)
        self.assertEqual(status, 0)
        direct = [_ffi._as_result(output) for output in outputs]
        wrapped = lwbgt.calculate_batch(records)
        self.assertEqual(
            [packed(result) for result in wrapped],
            [packed(result) for result in direct],
        )

    def test_batch_signature_and_invalid_argument_contract(self) -> None:
        function = _ffi._library().lwbgt_calc_batch_v1
        self.assertEqual(function.restype, ctypes.c_int)
        self.assertEqual(function(None, None, 0), 0)
        output = _ffi._OutputV1()
        self.assertEqual(function(None, ctypes.byref(output), 1), 1)

    def test_deterministic_case_set_matches_direct_native_batch_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cases = Path(temporary, "cases.csv")
            subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).parents[1] / "generate_cases.py"),
                    str(cases),
                ],
                check=True,
            )
            with cases.open(newline="", encoding="ascii") as stream:
                records = [
                    lwbgt.Input(
                        year=int(row["year"]),
                        month=int(row["month"]),
                        day=int(row["day"]),
                        hour=int(row["hour"]),
                        minute=int(row["minute"]),
                        gmt_offset_hours=int(row["gmt"]),
                        averaging_minutes=int(row["avg"]),
                        urban=int(row["urban"]),
                        latitude_deg_north=float(row["lat"]),
                        longitude_deg_east=float(row["lon"]),
                        solar_w_m2=float(row["solar"]),
                        pressure_hpa=float(row["pressure"]),
                        air_temperature_c=float(row["air"]),
                        relative_humidity_percent=float(row["rh"]),
                        wind_speed_m_s=float(row["wind"]),
                        wind_height_m=float(row["wind_height"]),
                        vertical_temperature_difference_c=float(row["vertical_delta"]),
                    )
                    for row in csv.DictReader(stream)
                ]
        count = len(records)
        self.assertEqual(count, 454)
        inputs = (_ffi._InputV1 * count)(*map(_ffi._as_native, records))
        outputs = (_ffi._OutputV1 * count)()
        self.assertEqual(_ffi._library().lwbgt_calc_batch_v1(inputs, outputs, count), 0)
        direct = [_ffi._as_result(output) for output in outputs]
        wrapped = lwbgt.calculate_batch(records)
        self.assertEqual(
            [packed(result) for result in wrapped],
            [packed(result) for result in direct],
        )


if __name__ == "__main__":
    unittest.main()
