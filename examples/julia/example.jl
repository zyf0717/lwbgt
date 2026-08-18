using Libdl

struct InputV1
    year::Int32
    month::Int32
    day::Int32
    hour::Int32
    minute::Int32
    gmt_offset_hours::Int32
    averaging_minutes::Int32
    urban::Int32
    latitude_deg_north::Float64
    longitude_deg_east::Float64
    solar_w_m2::Float64
    pressure_hpa::Float64
    air_temperature_c::Float64
    relative_humidity_percent::Float64
    wind_speed_m_s::Float64
    wind_height_m::Float64
    vertical_temperature_difference_c::Float64
end

struct OutputV1
    status::Int32
    estimated_wind_speed_m_s::Float32
    globe_temperature_c::Float32
    natural_wet_bulb_c::Float32
    psychrometric_wet_bulb_c::Float32
    wbgt_c::Float32
end

length(ARGS) == 1 || error("usage: example.jl SHARED_LIBRARY")
sizeof(InputV1) == 104 || error("unexpected InputV1 layout")
sizeof(OutputV1) == 24 || error("unexpected OutputV1 layout")

inputs = InputV1[
    InputV1(2024, 3, 21, 7, 0, 0, 0, 0,
            14.515380, -91.977540, 0.0, 1010.0, 42.543334, 31.5,
            0.821752, 2.0, 0.0),
    InputV1(2024, 4, 15, 14, 30, 8, 60, 1,
            1.3521, 103.8198, 742.0, 1008.4, 32.1, 68.0,
            2.8, 10.0, -0.4),
]
outputs = Vector{OutputV1}(undef, length(inputs))

library = Libdl.dlopen(ARGS[1])
batch = Libdl.dlsym(library, :lwbgt_calc_batch_v1)
saturation = Libdl.dlsym(library, :esat)
GC.@preserve inputs outputs begin
    result = ccall(batch, Cint,
                   (Ptr{InputV1}, Ptr{OutputV1}, Csize_t),
                   inputs, outputs, length(inputs))
    result == 0 || error("batch call failed")
end

all(output -> output.status == 0 && isfinite(output.wbgt_c), outputs) ||
    error("calculation failed")
outputs[1].estimated_wind_speed_m_s == Float32(inputs[1].wind_speed_m_s) ||
    error("2 m wind result is not deterministic")
isfinite(ccall(saturation, Cfloat, (Cdouble, Cint),
               inputs[1].air_temperature_c + 273.15, 0)) || error("esat failed")
Libdl.dlclose(library)
println("julia binding example: ok")
