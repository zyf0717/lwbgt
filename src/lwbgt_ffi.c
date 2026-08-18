#include "lwbgt.h"

_Static_assert(sizeof(lwbgt_input_v1) == 104, "unexpected lwbgt_input_v1 layout");
_Static_assert(offsetof(lwbgt_input_v1, latitude_deg_north) == 32,
               "unexpected lwbgt_input_v1 field offset");
_Static_assert(offsetof(lwbgt_input_v1, vertical_temperature_difference_c) == 96,
               "unexpected lwbgt_input_v1 field offset");
_Static_assert(sizeof(lwbgt_output_v1) == 24, "unexpected lwbgt_output_v1 layout");
_Static_assert(offsetof(lwbgt_output_v1, estimated_wind_speed_m_s) == 4,
               "unexpected lwbgt_output_v1 field offset");
_Static_assert(offsetof(lwbgt_output_v1, wbgt_c) == 20,
               "unexpected lwbgt_output_v1 field offset");

int lwbgt_calc_batch_v1(
    const lwbgt_input_v1 *inputs,
    lwbgt_output_v1 *outputs,
    size_t count
)
{
    size_t index;

    if (count == 0) return LWBGT_BATCH_OK;
    if (inputs == NULL || outputs == NULL) return LWBGT_BATCH_INVALID_ARGUMENT;

    for (index = 0; index < count; ++index) {
        const lwbgt_input_v1 *input = &inputs[index];
        lwbgt_output_v1 *output = &outputs[index];

        output->estimated_wind_speed_m_s = (float)input->wind_speed_m_s;
        output->status = calc_wbgt(
            input->year,
            input->month,
            input->day,
            input->hour,
            input->minute,
            input->gmt_offset_hours,
            input->averaging_minutes,
            input->latitude_deg_north,
            input->longitude_deg_east,
            input->solar_w_m2,
            input->pressure_hpa,
            input->air_temperature_c,
            input->relative_humidity_percent,
            input->wind_speed_m_s,
            input->wind_height_m,
            input->vertical_temperature_difference_c,
            input->urban,
            &output->estimated_wind_speed_m_s,
            &output->globe_temperature_c,
            &output->natural_wet_bulb_c,
            &output->psychrometric_wet_bulb_c,
            &output->wbgt_c
        );
    }

    return LWBGT_BATCH_OK;
}
