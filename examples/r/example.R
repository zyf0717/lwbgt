args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("usage: example.R R_BRIDGE_LIBRARY")
dll <- dyn.load(args[[1L]])

inputs <- data.frame(
    year = c(2024L, 2024L), month = c(3L, 4L), day = c(21L, 15L),
    hour = c(7L, 14L), minute = c(0L, 30L), gmt_offset_hours = c(0L, 8L),
    averaging_minutes = c(0L, 60L), urban = c(0L, 1L),
    latitude_deg_north = c(14.515380, 1.3521),
    longitude_deg_east = c(-91.977540, 103.8198), solar_w_m2 = c(0.0, 742.0),
    pressure_hpa = c(1010.0, 1008.4), air_temperature_c = c(42.543334, 32.1),
    relative_humidity_percent = c(31.5, 68.0), wind_speed_m_s = c(0.821752, 2.8),
    wind_height_m = c(2.0, 10.0), vertical_temperature_difference_c = c(0.0, -0.4)
)
outputs <- .Call("lwbgt_batch_example", inputs, PACKAGE = dll[["name"]])
if (any(outputs$status != 0L) || any(!is.finite(outputs$wbgt_c)))
    stop("calculation failed")
if (abs(outputs$estimated_wind_speed_m_s[[1L]] - inputs$wind_speed_m_s[[1L]]) > 1e-6)
    stop("2 m wind result is not deterministic")
saturation <- .Call(
    "lwbgt_esat_example", inputs$air_temperature_c[[1L]] + 273.15, 0L,
    PACKAGE = dll[["name"]]
)
if (!is.finite(saturation)) stop("esat failed")
dyn.unload(args[[1L]])
cat("R binding example: ok\n")
