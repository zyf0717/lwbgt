import CLWBGT
import XCTest

final class CLWBGTConsumerTests: XCTestCase {
    func testVersionAndLayout() {
        XCTAssertEqual(LWBGT_VERSION_MAJOR, 0)
        XCTAssertEqual(LWBGT_VERSION_MINOR, 4)
        XCTAssertEqual(LWBGT_VERSION_PATCH, 2)
        XCTAssertEqual(LWBGT_FFI_ABI_VERSION, 1)
        XCTAssertEqual(MemoryLayout<lwbgt_input_v1>.size, 104)
        XCTAssertEqual(MemoryLayout<lwbgt_output_v1>.size, 24)
    }

    func testBatchAndEsat() {
        var input = lwbgt_input_v1()
        input.year = 2024
        input.month = 4
        input.day = 15
        input.hour = 14
        input.minute = 30
        input.gmt_offset_hours = 8
        input.averaging_minutes = 60
        input.urban = 1
        input.latitude_deg_north = 1.3521
        input.longitude_deg_east = 103.8198
        input.solar_w_m2 = 742.0
        input.pressure_hpa = 1008.4
        input.air_temperature_c = 32.1
        input.relative_humidity_percent = 68.0
        input.wind_speed_m_s = 2.8
        input.wind_height_m = 10.0
        input.vertical_temperature_difference_c = -0.4
        var output = lwbgt_output_v1()

        XCTAssertEqual(
            lwbgt_calc_batch_v1(&input, &output, 1),
            Int32(LWBGT_BATCH_OK)
        )
        XCTAssertEqual(output.status, 0)
        XCTAssertEqual(output.wbgt_c.bitPattern, 0x42020259)
        XCTAssertEqual(esat(273.15, 0).bitPattern, 0x40c45e95)
    }

    func testBatchArgumentContract() {
        var output = lwbgt_output_v1()

        XCTAssertEqual(
            lwbgt_calc_batch_v1(nil, nil, 0),
            Int32(LWBGT_BATCH_OK)
        )
        XCTAssertEqual(
            lwbgt_calc_batch_v1(nil, &output, 1),
            Int32(LWBGT_BATCH_INVALID_ARGUMENT)
        )
    }
}
