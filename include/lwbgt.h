#ifndef LWBGT_H
#define LWBGT_H

#ifdef __cplusplus
extern "C" {
#endif

#define LWBGT_VERSION_MAJOR 0
#define LWBGT_VERSION_MINOR 1
#define LWBGT_VERSION_PATCH 0

int calc_wbgt(
    int year,
    int month,
    int day,
    int hour,
    int minute,
    int gmt,
    int averaging_minutes,
    double latitude_deg_north,
    double longitude_deg_east,
    double solar_w_m2,
    double pressure_hpa,
    double air_temperature_c,
    double relative_humidity_percent,
    double wind_speed_m_s,
    double wind_height_m,
    double vertical_temperature_difference_c,
    int urban,
    float *estimated_wind_speed_m_s,
    float *globe_temperature_c,
    float *natural_wet_bulb_c,
    float *psychrometric_wet_bulb_c,
    float *wbgt_c
);

float esat(double temperature_k, int phase);

#ifdef __cplusplus
}
#endif

#endif
